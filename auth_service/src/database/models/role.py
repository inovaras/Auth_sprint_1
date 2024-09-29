from sqlalchemy import Column, String

from auth_service.src.database.models.base import Base


class Role(Base):
    __tablename__ = 'roles'

    name = Column(String(255), unique=True, nullable=False)

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'<Role {self.name}>'
