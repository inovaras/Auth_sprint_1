import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Annotated, List

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from auth_service.src.cache.cache import Cache, get_cache_storage
from auth_service.src.core.config import settings
from auth_service.src.database.models.role import Role
from auth_service.src.database.models.user import User
from auth_service.src.database.repository.user import (
    UserRepository,
    get_user_repository,
)
from auth_service.src.dto.auth import TokensDTO
from auth_service.src.dto.user import UserCredentialsDTO, UserCredentialsDTO_v2, UserUpdateDTO
from auth_service.src.security.JWTAuth import JWTAuth, JWTError, get_jwt_auth, get_token

# to get a string like this run:
# openssl rand -hex 32


# https://habr.com/ru/companies/doubletapp/articles/764424/
# https://github.com/doubletapp/habr-jwt-auth-example/blob/main/src/app/pkg/auth/middlewares/jwt/base/auth.py#L50
class AuthService:
    # https://security.stackexchange.com/questions/4781/do-any-security-experts-recommend-bcrypt-for-password-storage/6415#6415
    # bcrypt vs pdkdf2 == все равно. оба хороши. Цель достигнуть 350мс на хеширование функции подбором раундов.
    # deprecated='auto' - разрешить только схемы указанные в schemes=[]
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto", pbkdf2_sha256__default_rounds=30000)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def __init__(
        self,
        repository: UserRepository,
        jwt_auth: JWTAuth,
        request: Request,
        response: Response,
        cache: Cache
    ) -> None:
        self.repository = repository
        self._jwt_auth = jwt_auth
        self.request = request
        self.response = response
        self.cache = cache

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password):
        return cls.pwd_context.hash(password)

    async def _issue_tokens_for_user(
        self, user: User, device_id: str = str(uuid.uuid4()), permissions: list[str] = []
    ) -> tuple[str, str]:
        access_token = self._jwt_auth.generate_access_token(
            subject=str(user.login), payload={'device_id': device_id, "permissions": permissions}
        )
        refresh_token = self._jwt_auth.generate_refresh_token(subject=str(user.login), payload={'device_id': device_id})
        await self.repository.set_or_update_refresh_token(user, refresh_token)

        return access_token, refresh_token

    # INFO ok
    async def register(self, body: UserCredentialsDTO|UserCredentialsDTO_v2) -> User:
        if await self.repository.find_by_login(body.login):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User blocked')

        body.password = self.get_password_hash(body.password)

        user = await self.repository.create(body.model_dump())
        if isinstance(body, UserCredentialsDTO):
            await self.repository.partial_update(pk=user.pk, data={'is_active': True})

        return user

    async def login(self, body: OAuth2PasswordRequestForm) -> tuple[TokensDTO, None] | tuple[None, str]:
        user = await self.repository.find_by_login(body.username)
        if not user or not self.verify_password(body.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect login or password')
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User blocked')
        if user.role:
            permissions: List[str] = [permission.allowed for permission in user.role.permissions]
            # INFO add refresh_token in postgres  +
            access_token, refresh_token = await self._issue_tokens_for_user(user=user, permissions=permissions)
        else:
            access_token, refresh_token = await self._issue_tokens_for_user(user=user, permissions=[])

        self.response.set_cookie(key="user_access_token", value=access_token, httponly=True)
        self.response.set_cookie(key="user_refresh_token", value=refresh_token, httponly=True)
        await self.repository.add_to_history(user, self.request.headers['user-agent'])

        return TokensDTO(access_token=access_token, refresh_token=refresh_token, token_type='bearer'), None

    async def logout(self):
        # TODO add access_token in redis
        # TODO remove refresh_token to postgres ??
        self.response.delete_cookie(key="user_access_token", httponly=True)
        self.response.delete_cookie(key="user_refresh_token", httponly=True)
        await self.cache.set_cache(self.request.cookies['user_access_token'] , self.request.cookies['user_access_token'] )

        return {'message': 'Пользователь успешно вышел из системы'}

    async def _update_tokens_after_change_role_or_permission(self, user: User):
        """Автоматический проброс permissions в access_token, refresh_token
        пользователя после обновления его прав без необходимости re-login пользователя

        invalid_token устанавливается в true после обновления роли или permission.
        """
        perms_allowed = [permission.allowed for permission in user.role.permissions]
        access_token, refresh_token = await self._issue_tokens_for_user(user=user, permissions=perms_allowed)
        self.response.set_cookie(key="user_access_token", value=access_token, httponly=True)
        self.response.set_cookie(key="user_refresh_token", value=refresh_token, httponly=True)
        await self.repository.partial_update(pk=user.pk, data={"invalid_token": False})

    # FIXME rename здесь не только декодирование токена, но и проверка на наличие необходимых атрибутов.
    async def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self._jwt_auth._config.secret, algorithms=[self._jwt_auth._config.algorithm])
        except (JWTError, jwt.ExpiredSignatureError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')

        expire = payload.get('exp')
        expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
        if (not expire) or (expire_time < datetime.now(timezone.utc)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек')

        login = payload.get('sub')
        if not login:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не содержит логин пользователя')
        return payload

    async def get_endpoint_access(self, request_endpoint: str, token: str):
        # in DB
        # permissions: List[str] = [permission.allowed for permission in user.role.permissions]
        # in CPU
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if request_endpoint in payload["permissions"]:
            return True

        return False

    async def get_current_user_if_has_permissions(self, token: Annotated[str, Depends(get_token)]):
        has_token = await self.cache.get_cache(key=token)
        if has_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Токен в черном списке')
        # TODO add decode result in Redis??
        payload = await self.decode_token(token)

        # запрошенный эндпоинт разрешен для использования владельцем токена.
        if not self.request.url.path in payload["permissions"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

        user = await self.repository.find_by_login(payload['sub'])
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

        if user.invalid_token:  # type: ignore
            await self._update_tokens_after_change_role_or_permission(user)

        return user

    # INFO dry
    async def change_login(
        self,
        user: User,
        data: UserUpdateDTO,
    ):
        updated_model = await self.repository.partial_update(user.pk, data.model_dump())
        access_token, refresh_token = await self._issue_tokens_for_user(updated_model)
        self.response.set_cookie(key="user_access_token", value=access_token, httponly=True)
        self.response.set_cookie(key="user_refresh_token", value=refresh_token, httponly=True)
        return updated_model

    # INFO dry
    async def change_password(self, user: User, data: UserUpdateDTO):
        data.password = self.get_password_hash(data.password)
        updated_model = await self.repository.partial_update(user.pk, data.model_dump())
        access_token, refresh_token = await self._issue_tokens_for_user(updated_model)
        self.response.set_cookie(key="user_access_token", value=access_token, httponly=True)
        self.response.set_cookie(key="user_refresh_token", value=refresh_token, httponly=True)
        return updated_model

    async def invalidate_tokens(self, role: Role):
        await self.repository.invalidate_tokens(role)


@lru_cache()
def get_auth_service(
    repository: Annotated[UserRepository, Depends(get_user_repository(model=User))],
    jwt_auth: Annotated[JWTAuth, Depends(get_jwt_auth)],
    request: Request,
    response: Response,
    cache: Cache = Depends(get_cache_storage)
) -> AuthService:
    return AuthService(
        repository=repository,
        jwt_auth=jwt_auth,
        request=request,
        response=response,
        cache=cache
    )
