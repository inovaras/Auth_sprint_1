import os
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Конфиг с использованием Pydantic
class Settings(BaseSettings):
    # model_config for pydantic v2
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/../../configs/.env", extra="ignore")
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


# Инициализация настроек
settings = Settings()
print()
