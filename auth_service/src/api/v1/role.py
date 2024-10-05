import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Optional

from pydantic import BaseModel, ConfigDict

from auth_service.src.dto.role import RoleCreateDTO, RoleDTO, RoleUpdateDTO
from auth_service.src.dto.permission import PermissionCreateDTO
from auth_service.src.security.JWTAuth import get_token
from auth_service.src.services.auth import AuthService, get_auth_service
from auth_service.src.services.role import RoleService as role_service, get_role_service


router = APIRouter()

RoleService = Annotated[role_service, Depends(get_role_service)]


# TODO permission for create role
# TODO права доступа к эндпоинтам
# TODO создание админа на пустой системе через консоль
@router.get("/get-all", status_code=status.HTTP_200_OK, response_model=list[RoleDTO])
async def get_all(
    service: RoleService,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user(token)
    role = await service.get_all()
    return role


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=RoleDTO)
async def create_role(
    requset: Request,
    service: RoleService,
    data: RoleCreateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user(token)
    role = await service.create(data)
    return role


@router.patch("/update", status_code=status.HTTP_200_OK, response_model=RoleDTO)
async def update_role(
    service: RoleService,
    pk: uuid.UUID,
    data: RoleUpdateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user(token)
    role = await service.update(pk, data)
    return role


@router.delete(
    "/delete",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
)
async def delete_role(
    service: RoleService,
    pk: uuid.UUID,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user(token)
    result = await service.delete(pk)
    return result


# update user added role field
@router.patch("/set-role-for-user", status_code=status.HTTP_200_OK, response_model=RoleDTO)
async def set_role(
    service: RoleService,
    pk: uuid.UUID,
    data: RoleUpdateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user(token)
    role = await service.update(pk, data, user)
    return role


@router.patch("/change-role-for-user", status_code=status.HTTP_200_OK, response_model=RoleDTO)
async def change_role_for_user(
    service: RoleService,
    pk: uuid.UUID,
    data: RoleUpdateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user(token)
    role = await service.change_role_for_user(pk, data)
    return role


@router.get("/check-user-permissions", status_code=status.HTTP_200_OK, response_model=RoleDTO)
async def check_user_permissions(
    service: RoleService,
    pk: uuid.UUID,
    data: RoleUpdateDTO,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user(token)
    role = await service.check_user_permissions(pk, data)
    return role
