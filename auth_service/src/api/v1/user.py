import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth_service.src.dto.user import (
    UserCredentialsDTO,
    UserDTO,
    UserLoginDTO,
    UserUpdateDTO,
)
from auth_service.src.security.JWTAuth import get_token
from auth_service.src.services.auth import AuthService, get_auth_service
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


@router.patch("/change-login", status_code=status.HTTP_200_OK, response_model=None, tags=['need_auth'])
async def change_login(
    data: UserUpdateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
    updated_user = await auth_service.change_login(user, data)
    return {"updated_login": updated_user.login}


@router.patch("/change-password", status_code=status.HTTP_200_OK, response_model=None, tags=['need_auth'])
async def change_password(
    data: UserUpdateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
    await auth_service.change_password(user, data)
    return {"updated_password": True}
