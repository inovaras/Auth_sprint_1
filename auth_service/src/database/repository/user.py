from collections.abc import Callable
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.database.models.user import User, UserConnection
from auth_service.src.database.repository.base import DatabaseRepository
from auth_service.src.database.session import get_db_session


class UserRepository(DatabaseRepository):

    async def find_by_login(self, login: str) -> User | None:
        query = select(self.model).where(self.model.login == login)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def add_to_history(self, user: User, user_agent: str):
        connection = UserConnection(info=user_agent, user_id=user.pk)
        self.session.add(connection)
        await self.session.commit()
        await self.session.refresh(user)  # INFO важно обновить user, чтобы его актуальные данные подтянуть в DTO


def get_user_repository(
    model: type[User],
) -> Callable[[AsyncSession], UserRepository]:
    def func(session: AsyncSession = Depends(get_db_session)):
        return UserRepository(model, session)

    return func
