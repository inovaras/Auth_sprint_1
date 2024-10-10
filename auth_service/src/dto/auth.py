from pydantic import BaseModel


class SuccessOut(BaseModel):
    success: bool = True


class ErrorOut(BaseModel):
    type: str
    message: str


class TokensDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
