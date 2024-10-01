from functools import lru_cache
from typing import Annotated
import uuid

from fastapi import Depends

from auth_service.src.dto.role import RoleCreateDTO, RoleDTO, RoleUpdateDTO
from auth_service.src.dto.permission import PermissionCreateDTO
from auth_service.src.database.models.role import Role
from auth_service.src.database.repository.role import RoleRepository, get_role_repository


class RoleService:

    def __init__(self, repository: RoleRepository) -> None:
        self.repository = repository

    async def create(self, data: RoleCreateDTO):
        #TODO сделать валидатор permissions
        role = await self.repository.create(data.model_dump())

        return role

    async def update(self, pk: uuid.UUID, data: RoleUpdateDTO):
        #TODO сделать валидатор
        role = await self.repository.update(pk, data.model_dump())

        return role


class PermissionService:

    def __init__(self, repository: RoleRepository) -> None:
        self.repository = repository

    async def create(self, data: PermissionCreateDTO):
        #TODO сделать валидатор permissions
        role = await self.repository.create(data.model_dump())

        return role



@lru_cache()
def get_role_service(
    repository: Annotated[RoleRepository, Depends(get_role_repository(model=Role))],
) -> RoleService:
    return RoleService(repository)

# session = AsyncSess()
# role_repo = RoleRepository(Role, session)
# role_service = RoleService(role_repo)