from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from auth_service.src.database.models.base import Base


class User(Base):
    __tablename__ = 'users'

    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    #INFO 1toM связь, тк M2M требует создания промежуточной таблицы прямо здесь в файле.
    connections = relationship("UserConnection", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @staticmethod
    def update_password(password: str) -> str:
        return generate_password_hash(password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class UserConnection(Base):
    __tablename__ = 'connections'

    info = Column(String(200))
    user_id = Column(UUID, ForeignKey("users.pk"))
    user = relationship("User", back_populates="connections")
