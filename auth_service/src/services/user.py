from functools import lru_cache
from typing import Annotated
import uuid

from fastapi import Depends

from auth_service.src.dto.user import UserCreateDTO, UserDTO, UserLoginDTO, UserUpdateDTO
from auth_service.src.database.models.user import User
from auth_service.src.database.repository.user import UserRepository, get_user_repository


class UserService:

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def register(self, data: UserCreateDTO):
        user = await self.repository.create(data.model_dump())
        return user

    async def login(self, data: UserLoginDTO, user_agent: str) -> User | None:
        user = await self.repository.find_by_login(data.login)
        # add to connect history
        if user:
            await self.repository.add_to_history(user, user_agent)
        # TODO надо возвращать jwt
        return user

    # INFO dry
    async def change_login(self, pk: uuid.UUID, data: UserUpdateDTO):
        result = await self.repository.partial_update(pk, data.model_dump())
        return result

    # INFO dry
    async def change_password(self, pk: uuid.UUID, data: UserUpdateDTO):
        result = await self.repository.partial_update(pk, data.model_dump())
        return result


@lru_cache()
def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository(model=User))],
) -> UserService:
    return UserService(repository)
