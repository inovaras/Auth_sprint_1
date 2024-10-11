import asyncio

import typer
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth_service.src.cache.cache import get_cache_storage
from auth_service.src.core.config import settings
from auth_service.src.database.models.role import Role
from auth_service.src.database.models.user import User
from auth_service.src.database.repository.role import RoleRepository
from auth_service.src.database.repository.user import UserRepository
from auth_service.src.database.session import get_db_session_for_main
from auth_service.src.dto.user import UserCredentialsDTO
from auth_service.src.main import add_permissions_in_db
from auth_service.src.security.JWTAuth import JWTAuth, JWTConfig
from auth_service.src.services.auth import AuthService
from auth_service.src.services.role import RoleService

app = typer.Typer()


async def create_superuser_with_role(session: AsyncSession, login: str):
    jwt_auth = JWTAuth(config=JWTConfig())
    cache = await get_cache_storage()
    role_repository = RoleRepository(model=Role, session=session)
    auth_repository = UserRepository(model=User, session=session)
    role_service = RoleService(repository=role_repository, request=Request, response=Response)
    auth_service = AuthService(
        repository=auth_repository, request=Request, response=Response, jwt_auth=jwt_auth, cache=cache
    )

    # create admin
    admin_creds = UserCredentialsDTO(login=login, password=settings.ADMIN_PASSWORD)
    current_admin = await auth_service.repository.find_by_login(admin_creds.login)
    print(f"Find {current_admin}")
    if not current_admin:
        current_admin: User = await auth_service.register_admin(admin_creds)
        print(f"Created {current_admin.login}")

    permissions = await role_service.repository.get_permissions()
    if not permissions:
        raise RuntimeError("Не созданы права доступа для ролей")

    admin_permissions = [permission.allowed for permission in permissions]

    role_name = {"name": "admin"}
    admin_role = await role_service.repository.find_by_name(role_name['name'])
    print(f"Find admin role {admin_role}")
    if admin_role:
        await role_service.set_role_for_user(pk=admin_role.pk, login=current_admin.login)
    else:
        admin_role = await role_service.repository.create(role_name)
        await role_service.repository.set_permission_to_role(admin_role, admin_permissions)
        await role_service.set_role_for_user(pk=admin_role.pk, login=role_name['name'])
        admin = await auth_service.repository.find_by_login(login)
        await auth_service.repository.partial_update(pk=admin.pk, data={"invalid_token": False})


async def create_superuser(login: str):
    """Ф-я должна запускаться ПОСЛЕ запуска приложения"""
    session = get_db_session_for_main()

    async with session as s:
        # Проверяем, существует ли уже пользователь с таким login
        result = await s.execute(select(User).filter_by(login=login))
        user = result.scalar()

        if user:
            typer.echo("Пользователь с таким login уже существует!")
            return

        await create_superuser_with_role(session=s, login=login)
        typer.echo(f"Суперпользователь {login} создан!")


@app.command()
def createsuperuser(
    login: str = typer.Option(..., prompt=True),
    # password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True)
):
    """Создать суперпользователя"""
    asyncio.run(create_superuser(login))


if __name__ == "__main__":
    app()
