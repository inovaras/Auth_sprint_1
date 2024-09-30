from http import HTTPStatus
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth_service.src.dto.user import (
    UserCreateDTO,
    UserDTO,
    UserLoginDTO,
    UserUpdateDTO,
)
from auth_service.src.services.user import UserService as user_service
from auth_service.src.services.user import get_user_service

router = APIRouter()

UserService = Annotated[user_service, Depends(get_user_service)]

"""
**API для сайта и личного кабинета**

- регистрация пользователя;  - /register сохранить в бд  == db +
- вход пользователя в аккаунт (обмен логина и пароля на пару токенов: JWT-access токен и refresh токен); - ?  /login
- обновление access-токена; - /refresh
- выход пользователя из аккаунта; - /logout
- изменение логина или пароля (с отправкой email вы познакомитесь в
следующих модулях, поэтому пока ваш сервис должен позволять изменять
личные данные без дополнительных подтверждений); /changepassword /changelogin  ==db +
- получение пользователем своей истории входов в аккаунт; - logging in db  /gethistory ==db
"""


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO)
async def create_user(service: UserService, data: UserCreateDTO):
    user = await service.register(data)
    return user


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserDTO)
async def login(service: UserService, data: UserLoginDTO, request: Request):
    user_agent = request.headers["user-agent"]
    response = await service.login(data, user_agent)
    if not response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    if isinstance(response, str):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=response)
    return response

# BUG не реализовано
@router.post("/logout", status_code=status.HTTP_200_OK, response_model=UserDTO)
async def logout(service: UserService, login: str) -> UserDTO:
    user = await service.logout(login=login)
    return user


@router.patch("/change-login", status_code=status.HTTP_200_OK, response_model=UserDTO)
async def change_login(service: UserService, pk: uuid.UUID, data: UserUpdateDTO):
    user = await service.change_login(pk, data)
    return user


@router.patch("/change-password", status_code=status.HTTP_200_OK, response_model=UserDTO)
async def change_password(service: UserService, pk: uuid.UUID, data: UserUpdateDTO):
    user = await service.change_password(pk, data)
    return user
