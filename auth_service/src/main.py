from contextlib import asynccontextmanager

from api.v1 import films, persons, genres
from core.config import settings
from db import psycopg, redis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis



@asynccontextmanager
async def lifespan(_: FastAPI):
    # TODO наличие соединения не проверяется
    redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    p

    print("redis connection successful")
    yield
    await redis.redis.close()
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
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
