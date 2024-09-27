from uuid import UUID

from pydantic import BaseModel

class UserCreateDTOAPI(BaseModel):
    login: str
    password: str


class UserInDB(BaseModel):
    id: UUID
    login: str
    password: str

    class Config:
        orm_mode = True