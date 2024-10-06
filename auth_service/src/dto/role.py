import uuid

from pydantic import BaseModel, ConfigDict

from auth_service.src.dto.user import UserDTO


class RoleCreateDTO(BaseModel):
    name: str


class RoleUpdateDTO(BaseModel):
    name: str


class PermissionDTO(BaseModel):
    allowed: str


class RoleUsersDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: uuid.UUID
    name: str
    permissions: list[PermissionDTO] = []
    users: list[UserDTO]


class RoleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: uuid.UUID
    name: str
