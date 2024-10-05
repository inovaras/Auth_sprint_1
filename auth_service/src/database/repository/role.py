from collections.abc import Callable
import uuid

from fastapi import Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.database.models.role import Permission, Role
from auth_service.src.database.repository.base import DatabaseRepository
from auth_service.src.database.session import get_db_session



class RoleRepository(DatabaseRepository):

    async def find_by_name(self, name: str) -> Role | None:
        query = select(self.model).where(self.model.name == name)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def get_all(self) -> Role | None:
        query = select(self.model).limit(100)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def create(self, data: dict) -> Role:
        permissions = data.pop('permissions')
        role = self.model(**data)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)

        for permission in permissions:
            self.session.add(Permission(allowed=permission, role_id=role.pk))
        await self.session.commit()
        await self.session.refresh(role)

        return role

    async def update(self, pk: uuid.UUID, data: dict) -> Role | None:
        entity = await self.get(pk)
        if not entity:
            return "Such pk does not exist"

        if data["name"] != entity.name:
            entity.name = data["name"]
            await self.session.commit()
            await self.session.refresh(entity)

        if data["permissions"]:

            for value in entity.permissions:
                # d1 = value.allowed
                # d2 = data["permissions"]
                if value.allowed not in data["permissions"]:
                    result = await self.session.execute(
                    select(Permission).where(Permission.allowed == value.allowed, Permission.role_id == pk)
                )
                    permission_to_delete = result.first()

                    if permission_to_delete:
                        await self.session.delete(permission_to_delete[0])
                        await self.session.commit()
                        print("удален:", value.allowed)

                else:
                    print("остался",value.allowed)
                    data["permissions"].remove(value.allowed)

            for permission in data["permissions"]:
                self.session.add(Permission(allowed=permission, role_id=pk))
                print("добавлен:", permission)
            await self.session.commit()
            await self.session.refresh(entity)

        return entity

    async def delete(self, pk: uuid.UUID) -> int:
        result = await self.session.execute(
                    select(self.model).where(self.model.pk == pk)
                )
        role_to_delete = result.first()

        if role_to_delete:
            await self.session.delete(role_to_delete[0])
            await self.session.commit()
            return status.HTTP_200_OK

        return status.HTTP_404_NOT_FOUND




    async def change_role_for_user(self, pk: uuid.UUID, data: dict) -> Role | None:
        entity = await self.get(pk)
        if not entity:
            return "Such pk does not exist"

        if data["name"] != entity.name:
            entity.name = data["name"]

            await self.session.commit()
            await self.session.refresh(entity)


        return entity

    async def check_user_permissions(self, pk: uuid.UUID, data: dict) -> Role | None:
        entity = await self.get(pk)
        if not entity:
            return "Such pk does not exist"

        if data["permissions"]:

            for value in entity.permissions:
                # d1 = value.allowed
                # d2 = data["permissions"]
                if value.allowed not in data["permissions"]:
                    result = await self.session.execute(
                    select(Permission).where(Permission.allowed == value.allowed, Permission.role_id == pk)
                )
                    permission_to_delete = result.first()

                    if permission_to_delete:
                        await self.session.delete(permission_to_delete[0])
                        await self.session.commit()
                        print("удален:", value.allowed)

                else:
                    print("остался",value.allowed)
                    data["permissions"].remove(value.allowed)

            for permission in data["permissions"]:
                self.session.add(Permission(allowed=permission, role_id=pk))
                print("добавлен:", permission)
            await self.session.commit()
            await self.session.refresh(entity)

        return entity

def get_role_repository(
    model: type[Role],
) -> Callable[[AsyncSession], RoleRepository]:
    def func(session: AsyncSession = Depends(get_db_session)):
        return RoleRepository(model, session)

    return func
