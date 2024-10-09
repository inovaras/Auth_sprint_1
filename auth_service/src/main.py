from fastapi import FastAPI, Request, Response
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.api.v1 import auth, role, user
from auth_service.src.core.config import settings
from auth_service.src.database.models.role import Permission, Role
from auth_service.src.database.models.user import User
from auth_service.src.database.repository.role import RoleRepository
from auth_service.src.database.repository.user import UserRepository
from auth_service.src.database.session import get_db_session_for_main
from auth_service.src.dto.user import UserCredentialsDTO
from auth_service.src.security.JWTAuth import JWTAuth, JWTConfig
from auth_service.src.services.auth import AuthService
from auth_service.src.services.role import RoleService


async def add_permissions_in_db(_: FastAPI, session: AsyncSession):
    # TODO add prefix service in endpoint url  auth_service_/api/v1/create-user
    api_url_list = [{"path": route.path, "name": route.name} for route in app.routes if isinstance(route, APIRoute)]
    repo = RoleRepository(Role, session)
    db_permissions = await repo.get_permissions()
    allowed_in_db = [permission.allowed for permission in db_permissions]

    has_new_urls = False
    for url in api_url_list:
        url = url['path']
        if url not in allowed_in_db:
            has_new_urls = True
            session.add(Permission(allowed=url))
    if has_new_urls:
        await session.commit()
    return api_url_list


async def create_basic_roles_and_users(session: AsyncSession):
    jwt_auth = JWTAuth(config=JWTConfig())
    role_repository = RoleRepository(model=Role, session=session)
    auth_repository = UserRepository(model=User, session=session)
    role_service = RoleService(repository=role_repository, request=Request, response=Response)
    auth_service = AuthService(repository=auth_repository, request=Request, response=Response, jwt_auth=jwt_auth)

    # create admin
    admin_creds = UserCredentialsDTO(login=settings.ADMIN_LOGIN, password=settings.ADMIN_PASSWORD)
    if not await auth_service.repository.find_by_login(admin_creds.login):
        admin: User = await auth_service.register(admin_creds)

    permissions = await role_service.repository.get_permissions()
    if not permissions:
        raise RuntimeError("Не созданы права доступа для ролей")
    user_permissions = ["/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/auth/logout", "/api/v1/auth/me/"]
    correct_user_permissions = []
    for permission in permissions:
        for user_permission in user_permissions:
            if permission.allowed == user_permission:
                correct_user_permissions.append(permission.allowed)
                break

    admin_permissions = [permission.allowed for permission in permissions]

    user_role_name = {"name": "user"}
    admin_role_name = {"name": "admin"}
    if not await role_service.repository.find_by_name(user_role_name['name']):
        user_role = await role_service.repository.create(user_role_name)
        await role_service.repository.set_permission_to_role(user_role, correct_user_permissions)

    if not await role_service.repository.find_by_name(admin_role_name['name']):
        admin_role = await role_service.repository.create(admin_role_name)
        await role_service.repository.set_permission_to_role(admin_role, admin_permissions)
        await role_service.set_role_for_user(pk=admin_role.pk, login=admin_role_name['name'])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO наличие соединения не проверяется
    # redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    async with get_db_session_for_main() as session:
        # Добавляем права в базу данных
        await add_permissions_in_db(app, session)
        print("permissions added successfully")
        await create_basic_roles_and_users(session)
        print("Created basic roles and users")
    print("redis connection successful")
    yield
    # await redis.redis.close()
    print("redis disconnection successful")


app = FastAPI(
    lifespan=lifespan,
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=settings.PROJECT_NAME,
    # Адрес документации в красивом интерфейсе
    docs_url="/api/openapi",
    # Адрес документации в формате OpenAPI
    openapi_url="/api/openapi.json",
    # Можно сразу сделать небольшую оптимизацию сервиса
    # и заменить стандартный JSON-сериализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
)

# Подключаем роутер к серверу, указав префикс /v1/users
# Теги указываем для удобства навигации по документации
app.include_router(
    user.router,
    prefix="/api/v1/users",
)
app.include_router(role.router, prefix="/api/v1/roles", tags=["roles", "need_auth"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
