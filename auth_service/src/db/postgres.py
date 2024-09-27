from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from auth_service.src.core.config import settings

# Создаём базовый класс для будущих моделей
Base = declarative_base()

# Создаём движок
# Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
engine = create_async_engine(settings.POSTGRES_DSN, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Функция понадобится при внедрении зависимостей
# Dependency
# https://python-bloggers.com/2022/07/connect-to-postgresql-with-sqlalchemy-and-asyncio/
async def get_pg_session() -> AsyncSession:
    try:
        async with async_session() as session:
            yield session
    except: # CHECK maybe dont work
        await session.rollback()
    finally:
        await session.close()
