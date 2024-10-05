import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from auth_service.src.database.models.user import User
from auth_service.src.database.repository.user import (
    UserRepository,
    get_user_repository,
)
from auth_service.src.dto.user import (
    UserCredentialsDTO,
    UserDTO,
    UserLoginDTO,
    UserUpdateDTO,
)


class UserService:

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    # INFO dry
    async def change_login(self, user:User, data:UserUpdateDTO):
        updated_model = await self.repository.partial_update(user.pk, data.model_dump())
        return updated_model

    # INFO dry
    async def change_password(self, user:User, data:UserUpdateDTO):
        updated_model = await self.repository.partial_update(user.pk, data.model_dump())
        return updated_model


@lru_cache()
def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository(model=User))],
) -> UserService:
    return UserService(repository)
