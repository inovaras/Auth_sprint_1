from enum import Enum
from sqlalchemy import Column, String

from auth_service.src.database.models.base import Base
from sqlalchemy.orm import relationship

class Role(Base):
    __tablename__ = 'roles'

    name = Column(String(255), unique=True, nullable=False)
    permissions = relationship("Permission", back_populates="role", cascade="all, delete-orphan", lazy="selectin")



    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class PermissionEnum(Enum):
    GET = "get"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class Permission(Base):

    allowed: PermissionEnum   #
    role = relationship("Role", back_populates="permissions")



    role = Role()
    role.permissions.append(Permission(allowed=PermissionEnum.CREATE))
    role.permissions.append(Permission(allowed=PermissionEnum.GET))