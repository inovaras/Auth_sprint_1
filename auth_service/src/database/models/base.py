import uuid

from sqlalchemy import Column, DateTime, func, orm
from sqlalchemy.ext.declarative import declared_attr


# https://www.slingacademy.com/article/sqlalchemy-created-at-and-updated-at-columns/
# добавление таймзоны также указано в ссылке выше - DateTime(timezone=True)
class TimestampMixin(object):
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # INFO хз зачем, после него все __tablename__ в сущностях подчеркнуты красным
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Base(TimestampMixin, orm.DeclarativeBase):
    """Base database model."""

    pk: orm.Mapped[uuid.UUID] = orm.mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
