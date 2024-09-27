import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Конфиг с использованием Pydantic
class Settings(BaseSettings):
    # model_config for pydantic v2
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/../../configs/.env", extra="ignore")
    # Название проекта
    PROJECT_NAME: str
    POSTGRES_DSN: str


# Инициализация настроек

settings = Settings()
print()
