from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from auth_service.src.dto.user import UserUpdateDTO
from auth_service.src.security.JWTAuth import get_token
from auth_service.src.services.auth import AuthService, get_auth_service
from auth_service.src.services.user import UserService as user_service
from auth_service.src.services.user import get_user_service

router = APIRouter()

UserService = Annotated[user_service, Depends(get_user_service)]


@router.patch("/change-login", status_code=status.HTTP_200_OK, response_model=None, tags=["auth"])
async def change_login(
    data: UserUpdateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
    updated_user = await auth_service.change_login(user, data)
    return {"updated_login": updated_user.login}


@router.patch("/change-password", status_code=status.HTTP_200_OK, response_model=None, tags=["auth"])
async def change_password(
    data: UserUpdateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
    await auth_service.change_password(user, data)
    return {"updated_password": True}


@router.patch("/connection-history", status_code=status.HTTP_200_OK, response_model=None, tags=["auth"])
async def history(
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    limit: int = Query(10, ge=1, le=100),  # Default 10, min 1, max 100
    offset: int = Query(0, ge=0),  # Default offset 0
):
    user = await auth_service.get_current_user_if_has_permissions(token)

    return user.sessions[offset:offset+limit]
