import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCredentialsDTO(BaseModel):
    login: str
    password: str


class UserCredentialsDTO_v2(BaseModel):
    login: str
    password: str
    is_active: bool = True


class UserLoginDTO(BaseModel):
    login: str
    password: str


class UserUpdateDTO(BaseModel):
    login: Optional[str] = None
    password: Optional[str] = None


class UserSessionLogDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    info: str


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: uuid.UUID
    login: str
    # TODO убрать на проде отображение пароля в апи
    # password: str

    sessions: list[UserSessionLogDTO] = []
