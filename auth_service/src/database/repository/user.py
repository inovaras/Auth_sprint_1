from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.database.models.role import Role
from auth_service.src.database.models.user import Token, User, UserSessionLog
from auth_service.src.database.repository.base import DatabaseRepository
from auth_service.src.database.session import get_db_session


class UserRepository(DatabaseRepository):

    async def find_by_login(self, login: str) -> User | None:
        query = select(self.model).where(self.model.login == login)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def add_to_history(self, user: User, user_agent: str):
        connection = UserSessionLog(info=user_agent, user_id=user.pk)
        self.session.add(connection)
        await self.session.commit()
        await self.session.refresh(user)  # INFO важно обновить user, чтобы его актуальные данные подтянуть в DTO

    async def find_refresh_token(self, user: User):
        query = select(Token).where(Token.user_id == user.pk)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def update_refresh_token(self, token_db: Token, refresh_token:str):
        query = (
            update(Token)
            .where(Token.refresh_token == token_db.refresh_token)
            .values(refresh_token=refresh_token, updated_at=datetime.now())
        )
        await self.session.execute(query)

    async def set_or_update_refresh_token(self, user: User, refresh_token: str):
        token_db = await self.find_refresh_token(user)
        if token_db:
            await self.update_refresh_token(token_db, refresh_token )
            return refresh_token

        token = Token(refresh_token=refresh_token, user_id=user.pk)
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(user)


    async def invalidate_tokens(self, role:Role) -> None:
        query = select(User).where(User.role == role)
        users = list(await self.session.scalars(query))
        if users:
            for user in users:
                user.invalid_token = True
                self.session.add(user)
        await self.session.commit()
        print()

def get_user_repository(
    model: type[User],
) -> Callable[[AsyncSession], UserRepository]:
    def func(session: AsyncSession = Depends(get_db_session)):
        return UserRepository(model, session)

    return func
