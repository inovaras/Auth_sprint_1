import uuid
from collections.abc import Callable
from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.database.models.role import Permission, Role
from auth_service.src.database.models.user import User
from auth_service.src.database.repository.base import DatabaseRepository
from auth_service.src.database.session import get_db_session


class RoleRepository(DatabaseRepository):

    async def find_by_name(self, name: str) -> Role | None:
        query = select(self.model).where(self.model.name == name)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def get_all(self) -> Role | None:
        query = select(self.model).limit(100)
        rows = list(await self.session.scalars(query))
        return rows

    async def create(self, data: dict) -> Role:
        role = self.model(**data)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)

        return role

    # TODO rewrite
    async def update(self, pk: uuid.UUID, data: dict) -> Role | None:
        role_db = await self.get(pk)
        if not role_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not exists')

        if data["name"] != role_db.name:
            role_db.name = data["name"]
            await self.session.commit()
            await self.session.refresh(role_db)

        # if data["permissions"]:

        #     for value in role_db.permissions:
        #         if value.allowed not in data["permissions"]:
        #             result = await self.session.execute(
        #                 select(Permission).where(Permission.allowed == value.allowed, Permission.role_id == pk)
        #             )
        #             permission_to_delete = result.first()

        #             if permission_to_delete:
        #                 await self.session.delete(permission_to_delete[0])
        #                 await self.session.commit()
        #                 print("удален:", value.allowed)

        #         else:
        #             print("остался", value.allowed)
        #             data["permissions"].remove(value.allowed)

        #     for permission in data["permissions"]:
        #         self.session.add(Permission(allowed=permission, role_id=pk))
        #         print("добавлен:", permission)
        #     await self.session.commit()
        #     await self.session.refresh(role_db)
        return role_db

    async def delete(self, pk: uuid.UUID) -> int:
        result = await self.session.execute(select(self.model).where(self.model.pk == pk))
        role_to_delete = result.first()

        if role_to_delete:
            await self.session.delete(role_to_delete[0])
            await self.session.commit()
            return status.HTTP_200_OK

        return status.HTTP_404_NOT_FOUND

    async def find_by_login(self, login: str) -> User | None:
        query = select(User).where(User.login == login)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def set_role_for_user(self, pk: uuid.UUID, user: User) -> Role | None:
        role_db = await self.get(pk)
        user.role_id = role_db.pk
        user.invalid_token = True
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(role_db)

        return role_db

    async def get_permissions(self) -> List[Permission] | None:
        query = select(Permission)
        permissions = list(await self.session.scalars(query))
        return permissions

    async def add_permissions(self, endpoints: list[dict]):

        db_permissions = await self.get_permissions()
        allowed_in_db = [permission.allowed for permission in db_permissions]

        has_new_urls = False
        for url in endpoints:
            url = url['path']
            if url not in allowed_in_db:
                has_new_urls = True
                self.session.add(Permission(allowed=url))
        if has_new_urls:
            await self.session.commit()
        return endpoints

    async def set_permission_to_role(self, role: Role, permissions: List[str]):
        for permission in permissions:
            query = select(Permission).where(Permission.allowed == permission)
            rows = await self.session.execute(query)
            perm = rows.scalar_one_or_none()
            if perm:
                role.permissions.append(perm)

            await self.session.commit()
            await self.session.refresh(role)
        return True


def get_role_repository(
    model: type[Role],
) -> Callable[[AsyncSession], RoleRepository]:
    def func(session: AsyncSession = Depends(get_db_session)):
        return RoleRepository(model, session)

    return func
