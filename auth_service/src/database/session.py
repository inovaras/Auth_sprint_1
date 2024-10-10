from collections.abc import AsyncGenerator

from fastapi.concurrency import asynccontextmanager
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth_service.src.core.config import settings


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(settings.POSTGRES_DSN)
    factory = async_sessionmaker(engine)
    async with factory() as session:
        try:
            yield session
            await session.commit()  # INFO обудмать его наличие здесь, ведь он используется вручную в repository
        except exc.SQLAlchemyError:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_session_for_main() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(settings.POSTGRES_DSN)
    factory = async_sessionmaker(engine)
    async with factory() as session:
        try:
            yield session
            await session.commit()  # Подтверждаем транзакцию
        except exc.SQLAlchemyError:
            await session.rollback()  # Откатываем транзакцию в случае ошибки
            raise
        finally:
            await session.close()  # Закрываем сессию
