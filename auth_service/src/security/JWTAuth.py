import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import lru_cache
from typing import Any

import jwt
from fastapi import HTTPException, Request, status

from auth_service.src.core.config import settings


class JWTError(Exception):
    pass


async def get_token(request: Request):
    token = request.cookies.get('user_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')

    return token


async def get_refresh_token(request: Request):
    token = request.cookies.get('user_refresh_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')

    return token


@dataclass
class JWTConfig:
    secret: str = settings.JWT_SECRET_KEY
    algorithm: str = settings.JWT_ALGORITHM
    access_token_ttl: timedelta = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_ttl: timedelta = settings.REFRESH_TOKEN_EXPIRE_MINUTES


class TokenType(str, Enum):
    ACCESS = 'ACCESS'
    REFRESH = 'REFRESH'


# https://habr.com/ru/companies/doubletapp/articles/764424/
# https://github.com/doubletapp/habr-jwt-auth-example/blob/main/src/app/pkg/auth/middlewares/jwt/base/auth.py#L50
class JWTAuth:

    def __init__(self, config: JWTConfig):
        self._config = config

    def generate_unlimited_access_token(self, subject: str, payload: dict[str, Any] = {}) -> str:
        return self.__sign_token(type=TokenType.ACCESS.value, subject=subject, payload=payload)

    def generate_access_token(self, subject: str, payload: dict[str, Any] = {}) -> str:
        return self.__sign_token(
            type=TokenType.ACCESS.value,
            subject=subject,
            payload=payload,
            ttl=self._config.access_token_ttl,
        )

    def generate_refresh_token(self, subject: str, payload: dict[str, Any] = {}) -> str:
        return self.__sign_token(
            type=TokenType.REFRESH.value,
            subject=subject,
            payload=payload,
            ttl=self._config.refresh_token_ttl,
        )

    def __sign_token(self, type: str, subject: str, payload: dict[str, Any] = {}, ttl: timedelta = None) -> str:
        current_datetime = datetime.now(tz=timezone.utc)

        data = dict(
            # Указываем себя в качестве издателя
            iss='befunny@auth_service',
            # владелец токена (username or email)
            sub=subject,
            # тип токена - ACCESS or REFRESH
            type=type,
            # Рандомно генерируем идентификатор токена ( UUID )
            jti=self.__generate_jti(),
            # Временем выдачи ставим текущее
            iat=current_datetime,
            # Временем начала действия токена ставим текущее или то, что было передано в payload
            nbf=payload['nbf'] if payload.get('nbf') else current_datetime,
        )
        data.update(dict(exp=data['nbf'] + ttl)) if ttl else None
        payload.update(data)
        return jwt.encode(payload, self._config.secret, algorithm=self._config.algorithm)

    @staticmethod
    def __generate_jti() -> str:
        return str(uuid.uuid4())

    def verify_token(self, token) -> dict[str, Any]:
        return jwt.decode(token, self._config.secret, algorithms=[self._config.algorithm])

    def get_jti(self, token) -> str:
        return self.verify_token(token)['jti']

    def get_sub(self, token) -> str:
        return self.verify_token(token)['sub']

    def get_exp(self, token) -> int:
        return self.verify_token(token)['exp']

    @staticmethod
    def get_raw_jwt(token) -> dict[str, Any]:
        """
        Return the payload of the token without checking the validity of the token
        """
        return jwt.decode(token, options={'verify_signature': False})


@lru_cache()
def get_jwt_auth() -> JWTAuth:
    return JWTAuth(JWTConfig())
