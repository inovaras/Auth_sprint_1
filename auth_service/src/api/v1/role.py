import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth_service.src.dto.role import (
    PermissionDTO,
    RoleCreateDTO,
    RoleDTO,
    RoleUpdateDTO,
    RoleUsersDTO,
)
from auth_service.src.security.JWTAuth import get_token
from auth_service.src.services.auth import AuthService, get_auth_service
from auth_service.src.services.role import RoleService as role_service
from auth_service.src.services.role import get_role_service

router = APIRouter()

RoleService = Annotated[role_service, Depends(get_role_service)]


# TODO права доступа к эндпоинтам
# TODO создание админа на пустой системе через консоль
@router.get("/get-all", status_code=status.HTTP_200_OK, response_model=list[RoleUsersDTO])
async def get_all(
    service: RoleService,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
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
    user = await auth_service.get_current_user_if_has_permissions(token)
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
    user = await auth_service.get_current_user_if_has_permissions(token)
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
    user = await auth_service.get_current_user_if_has_permissions(token)
    result = await service.delete(pk)
    return result


@router.patch(
    "/set-role-for-user",
    status_code=status.HTTP_200_OK,
    response_model=RoleDTO,
    description='Назначить пользователю роль',
)
async def set_role_for_user(
    service: RoleService,
    role_pk: uuid.UUID,
    login: str,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
    role = await service.set_role_for_user(role_pk, login)
    return role


# INFO в нашей системе разрешена только 1 роль на юзера. Этот эндпоинт имеет смысл в системе где разрешено
# несколько ролей на пользователя
@router.patch("/remove-role-for-user", status_code=status.HTTP_200_OK, response_model=RoleDTO)
async def remove_role_for_user():
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


# CHECK доделать или проверить при интеграции сервисов
@router.get("/check-user-permissions", status_code=status.HTTP_200_OK, response_model=None, tags=["permissions"])
async def check_user_permissions(
    request: Request,
    request_endpoint: str,  # role/get-all
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> bool:
    user = await auth_service.get_current_user_if_has_permissions(token)
    is_allowed = await auth_service.get_endpoint_access(request_endpoint, token)
    return is_allowed


@router.get("/create-permissions", status_code=status.HTTP_200_OK, response_model=None, tags=["permissions"])
async def create_permissions(
    service: RoleService,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    user = await auth_service.get_current_user_if_has_permissions(token)
    await service.add_permissions()


@router.get("/get-permissions", status_code=status.HTTP_200_OK, response_model=List[PermissionDTO], tags=["permissions"])
async def get_permissions(
    service: RoleService,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
    return await service.get_permissions()


@router.post("/set-permissions-to-role", status_code=status.HTTP_200_OK, response_model=None, tags=["permissions"])
async def set_permissions_to_role(
    service: RoleService,
    token: Annotated[str, Depends(get_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    permissions: List[str],
    role_pk: uuid.UUID,
) -> None:
    user = await auth_service.get_current_user_if_has_permissions(token)
    role = await service.set_permissions_to_role(role_pk, permissions)
    # INFO деактивация токенов для юзеров, использующих роль
    await auth_service.invalidate_tokens(role)
