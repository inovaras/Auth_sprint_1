from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
import fastapi
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from auth_service.src.dto.auth import ErrorOut, TokensDTO, User
from auth_service.src.dto.user import UserCredentialsDTO
from auth_service.src.services.auth import AuthService, get_auth_service, get_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/me/", tags=['need_auth'])
async def get_me(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[str, Depends(get_token)],
):
    user = await auth_service.get_current_user(token)
    return user


@router.post(
    path='/register',
    responses={
        200: {'model': TokensDTO},
        400: {'model': ErrorOut},
    },
    response_model=None,
    # status_code=status.HTTP_201_CREATED
)
async def register(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    # token: Annotated[str, Depends(oauth2_scheme)],
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
    # body: UserCredentialsDTO,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
) -> TokensDTO | JSONResponse:
    # data, error = await auth_service.login(body=body)
    data, error = await auth_service.login(body=form_data)
    if error:
        return error

    return data


@router.post(
    path='/logout',
    # responses={200: {'model': SuccessOut}},
    # dependencies=[Security(check_access_token)],
    response_model=None,
    tags=['need_auth']
)
async def logout(
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    message = await auth_service.logout()
    return message


# @router.post("/token")
# async def login_for_access_token(
#     request: Request,
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#     auth_service: Annotated[AuthService, Depends(get_auth_service)],
# ) -> TokensDTO:
#     user = auth_service.authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = auth_service.generate_access_token(subject=user.username, payload={"hello": "1", "text": 2})
#     refresh_token = auth_service.generate_refresh_token(subject=user.username, payload={"hello": "2222", "text": 345})
#     return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


# @router.get("/users/me/", response_model=User)
# async def read_users_me(current_user: Annotated[User, Depends()]):
#     return current_user


# @router.get("/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[User, Depends(AuthService.get_current_active_user)],
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]
