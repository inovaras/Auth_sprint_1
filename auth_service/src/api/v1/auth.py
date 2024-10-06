from typing import Annotated

import fastapi
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from auth_service.src.dto.auth import ErrorOut, TokensDTO
from auth_service.src.dto.user import UserCredentialsDTO
from auth_service.src.services.auth import AuthService, get_auth_service, get_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/me/", tags=['need_auth'])
async def get_me(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[str, Depends(get_token)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
    return user


@router.post(
    path='/register',
    responses={
        200: {'model': TokensDTO},
        400: {'model': ErrorOut},
    },
    response_model=None,
)
async def register(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    data: UserCredentialsDTO,
) -> JSONResponse:
    data, error = await auth_service.register(data)
    if error:
        return error

    return data


@router.post(
    path='/login',
    response_model=None,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
) -> TokensDTO | JSONResponse:
    data, error = await auth_service.login(body=form_data)
    if error:
        return error

    return data


@router.post(path='/logout', response_model=None, tags=['need_auth'])
async def logout(
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    message = await auth_service.logout()
    return message
