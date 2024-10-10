from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from auth_service.src.dto.auth import TokensDTO
from auth_service.src.dto.user import UserCredentialsDTO
from auth_service.src.services.auth import AuthService, get_auth_service, get_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/me/", status_code=status.HTTP_200_OK)
async def get_me(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[str, Depends(get_token)],
):
    user = await auth_service.get_current_user_if_has_permissions(token)
    return user


@router.post(path='/register', response_model=None, status_code=status.HTTP_201_CREATED)
async def register(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    data: UserCredentialsDTO,
) -> JSONResponse:
    data = await auth_service.register(data)

    return data


@router.post(path='/login', response_model=None, status_code=status.HTTP_200_OK)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
) -> TokensDTO | JSONResponse:
    data, error = await auth_service.login(body=form_data)
    if error:
        return error

    return data


@router.post(path='/logout', response_model=None, status_code=status.HTTP_200_OK)
async def logout(
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    message = await auth_service.logout()
    return message
