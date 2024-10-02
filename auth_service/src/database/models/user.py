from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256


from auth_service.src.database.models.base import Base

from passlib.context import CryptContext

# https://security.stackexchange.com/questions/4781/do-any-security-experts-recommend-bcrypt-for-password-storage/6415#6415
# bcrypt vs pdkdf2 == все равно. оба хороши. Цель достигнуть 350мс на хеширование функции подбором раундов.
pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)


class User(Base):
    __tablename__ = 'users'

    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    #INFO 1toM связь, тк M2M требует создания промежуточной таблицы прямо здесь в файле.
    connections = relationship("UserSessionLog", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    #TODO
    # role

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = self.generate_password_hash(password)


    def generate_password_hash(self,password:str)-> str:
        return pwd_context.encrypt(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)


    def update_password(self, password: str) -> str:
        return self.generate_password_hash(password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'

class UserSessionLog(Base):
    __tablename__ = 'connections'

    info = Column(String(200))
    user_id = Column(UUID, ForeignKey("users.pk"))
    user = relationship("User", back_populates="connections")
