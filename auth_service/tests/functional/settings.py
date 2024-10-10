import os
from datetime import timedelta

from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSettings(BaseSettings):
    PROJECT_NAME: str
    POSTGRES_DSN: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: timedelta = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRE_MINUTES: timedelta = timedelta(minutes=60 * 24 * 7)
    ADMIN_PASSWORD: str
    ADMIN_LOGIN: str
    REDIS_HOST: str
    REDIS_PORT: int
    AUTH_SERVICE_URL: str

    class Config:
        env_file = f'{BASE_DIR}/functional/.env'
        extra = "ignore"


test_settings = TestSettings()
print()
