from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256


from auth_service.src.database.models.base import Base

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256", pbkdf2_sha256__default_rounds=30000)


class User(Base):
    __tablename__ = 'users'

    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=False)
    invalid_token = Column(Boolean, default=False)
    # INFO 1toM связь, тк M2M требует создания промежуточной таблицы прямо здесь в файле.
    sessions = relationship("UserSessionLog", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    role_id = Column(UUID, ForeignKey("roles.pk"))
    role = relationship("Role", back_populates="users")


    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = password

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class UserSessionLog(Base):
    __tablename__ = 'sessions'

    info = Column(String(200))
    user_id = Column(UUID, ForeignKey("users.pk"))
    user = relationship("User", back_populates="sessions")


class Token(Base):
    __tablename__ = 'tokens'

    refresh_token = Column(Text)
    user_id = Column(UUID, ForeignKey("users.pk"))
    user = relationship("User", back_populates="tokens")
