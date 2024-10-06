import uuid
from functools import lru_cache
from typing import Annotated, List

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.routing import APIRoute

from auth_service.src.core.config import settings
from auth_service.src.database.models.role import Permission, Role
from auth_service.src.database.models.user import User
from auth_service.src.database.repository.role import (
    RoleRepository,
    get_role_repository,
)
from auth_service.src.dto.role import RoleCreateDTO, RoleUpdateDTO


class RoleService:

    def __init__(self, repository: RoleRepository, request: Request, response: Response) -> None:
        self.repository = repository
        self.request = request
        self.response = response

    async def get_all(self):
        role = await self.repository.get_all()

        return role

    async def create(self, data: RoleCreateDTO):
        role_db = await self.repository.find_by_name(data.name)
        if role_db:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Role already exists')
        role = await self.repository.create(data.model_dump())

        return role

    async def update(self, pk: uuid.UUID, data: RoleUpdateDTO):
        role = await self.repository.update(pk, data.model_dump())

        return role

    async def delete(self, pk: uuid.UUID):
        status = await self.repository.delete(pk)

        return status



    async def set_role_for_user(self, pk: uuid.UUID, login: str):
        user_db = await self.repository.find_by_login(login)
        if not user_db:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect user login')

        role = await self.repository.set_role_for_user(pk, user=user_db)

        return role

    async def get_permissions(self) -> List[Permission] | None:
        return await self.repository.get_permissions()

    async def add_permissions(self):
        # TODO add prefix service in endpoint url  auth_/api/v1/create-user
        api_url_list = [
            {"path": route.path, "name": route.name} for route in self.request.app.routes if isinstance(route, APIRoute)
        ]
        await self.repository.add_permissions(endpoints=api_url_list)

    async def set_permissions_to_role(self, role_pk: uuid.UUID, permissions: List[str]) -> Role:
        role_db = await self.repository.get(role_pk)
        if not role_db:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Role is not exists')

        await self.repository.set_permission_to_role(role_db, permissions)

        return role_db


@lru_cache()
def get_role_service(
    repository: Annotated[RoleRepository, Depends(get_role_repository(model=Role))],
    request: Request,
    response: Response,
) -> RoleService:
    return RoleService(repository, request=request, response=response)
