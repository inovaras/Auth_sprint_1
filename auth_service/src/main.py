from fastapi.concurrency import asynccontextmanager

from fastapi import  FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from redis.asyncio import Redis

from auth_service.src.api.v1 import auth, user, role
from auth_service.src.core.config import settings
from auth_service.src.database.models.role import Permission, Role
from auth_service.src.database.repository.role import RoleRepository
from auth_service.src.database.session import get_db_session_for_main

from sqlalchemy.ext.asyncio import AsyncSession


async def add_permissions_in_db(_: FastAPI, session: AsyncSession):
    #TODO add prefix service in endpoint url  auth_service_/api/v1/create-user
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

async def create_superadmin():
    #TODO add all permissions
    #TODO check admin on exists in db.
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO наличие соединения не проверяется
    # redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    async with get_db_session_for_main() as session:
        # Добавляем права в базу данных
        await add_permissions_in_db(app, session)
        print("permissions added successfully")
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
app.include_router(user.router, prefix="/api/v1/users", )
app.include_router(role.router, prefix="/api/v1/roles", tags=["roles","need_auth"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
