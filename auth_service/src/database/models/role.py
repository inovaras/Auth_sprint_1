from sqlalchemy import Column, ForeignKey, String

from auth_service.src.database.models.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# TODO
from sqlalchemy import Enum
import enum


class Role(Base):
    __tablename__ = 'roles'

    name = Column(String(255), unique=True, nullable=False)
    permissions = relationship("Permission", back_populates="role", cascade="all, delete-orphan", lazy="selectin")
    users = relationship("User", back_populates="role", cascade="all, delete-orphan", lazy="selectin")


    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class PermissionEnum(str, enum.Enum):
    # TODO users:get, actors:update
    role_get_all = "role:get_all"
    role_create = "role:create"
    role_update = "role:update"
    role_delete = "role:delete"
    set_role = "role:set_role"
    change_role_for_user = "role:change_role_for_user"
    check_user_permissions = "role:check_user_permissions"


class Permission(Base):
    allowed = Column(Enum(PermissionEnum))
    role_id = Column(UUID, ForeignKey("roles.pk"))
    role = relationship("Role", back_populates="permissions")
