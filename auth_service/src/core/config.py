import os

from pydantic_settings import BaseSettings

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Конфиг с использованием Pydantic
class Settings(BaseSettings):
    # Название проекта
    PROJECT_NAME: str

    # Настройки Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # Настройки Postgresql
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_SCHEMA: str = "http://"
    POSTGRES_USER="postgres"
    POSTGRES_PASSWORD="postgres"
    POSTGRES_DB="auth_db"

    SQL_ENGINE: str
    LOG_LEVEL: str

    class Config:
        env_file = f"{BASE_DIR}/../../configs/.env"
        extra = "ignore"


# Инициализация настроек
settings = Settings()