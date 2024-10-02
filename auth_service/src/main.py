from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from auth_service.src.api.v1 import auth, user, role
from auth_service.src.core.config import settings

# from db import psycopg, redis
# from auth_service.src.database.session import get_db_session


@asynccontextmanager
async def lifespan(_: FastAPI):
    # TODO наличие соединения не проверяется
    # redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

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
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(role.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
