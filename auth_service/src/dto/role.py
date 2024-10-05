import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Enum

from auth_service.src.database.models.role import PermissionEnum

class RoleCreateDTO(BaseModel):
    name: str
    permissions: list[PermissionEnum]
    # permissions: list[str]


class RoleUpdateDTO(BaseModel):
    pk: uuid.UUID
    name: str
    permissions: list[str]


class PermissionDTO(BaseModel):
    allowed: PermissionEnum
    # allowed: str


class RoleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: uuid.UUID
    name: str
    permissions: list[PermissionDTO] = []


# class UserRoleDTO(BaseModel):

#     pk: uuid.UUID
#     #как сюда добавить модель юзера
