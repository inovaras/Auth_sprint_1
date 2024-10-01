from http import HTTPStatus
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Optional

from pydantic import BaseModel, ConfigDict

from auth_service.src.dto.role import RoleCreateDTO, RoleDTO, RoleUpdateDTO
from auth_service.src.dto.permission import PermissionCreateDTO
from auth_service.src.services.role import RoleService as role_service, get_role_service


router = APIRouter()

RoleService = Annotated[role_service, Depends(get_role_service)]

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=RoleDTO)
async def create_role(service: RoleService, data: RoleCreateDTO):
    role = await service.create(data)
    return role



@router.post("/update", status_code=status.HTTP_201_CREATED, response_model=RoleDTO)
async def update_role(service: RoleService, pk: uuid.UUID, data: RoleUpdateDTO):
    role = await service.update(pk, data)
    return role
