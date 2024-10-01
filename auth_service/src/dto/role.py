import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RoleCreateDTO(BaseModel):
    name: str
    permissions: list[str]


class RoleUpdateDTO(BaseModel):
    pk: uuid.UUID
    name: str
    permissions: list[str]


class PermissionDTO(BaseModel):
    allowed: str


class RoleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: uuid.UUID
    name: str
    permissions: list[PermissionDTO] = []
