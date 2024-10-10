from sqlalchemy import UUID, Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship

from auth_service.src.database.models.base import Base

# ManyToMany
association_table = Table(
    'roles_permissions',
    Base.metadata,
    Column('role_pk', UUID, ForeignKey('roles.pk')),
    Column('permission_pk', UUID, ForeignKey('permissions.pk')),
)


class Role(Base):
    __tablename__ = 'roles'

    name = Column(String(255), unique=True, nullable=False)
    permissions = relationship("Permission", lazy="selectin", secondary=association_table)
    users = relationship("User", back_populates="role", cascade="all, delete-orphan", lazy="selectin")

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class Permission(Base):
    __tablename__ = "permissions"
    allowed = Column(Text, unique=True)  # endpoints api   microservice_name/endpoint
