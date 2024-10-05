import uuid
from typing import Any, Dict, Generic, TypeVar

from sqlalchemy import BinaryExpression, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.database.models.base import Base

Model = TypeVar("Model", bound=Base)


class DatabaseRepository(Generic[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict) -> Model:
        instance = self.model(**data)
        self.session.add(instance)
        # TODO why?
        await self.session.commit()
        await self.session.refresh(instance)
        return instance


    async def get(self, pk: uuid.UUID) -> Model | None:
        return await self.session.get(self.model, pk)

    async def partial_update(self, pk: uuid.UUID, data: Dict[str, Any]) -> Model | None:
        entity = await self.get(pk)
        if entity:
            dict_without_none = {}
            for key, value in data.items():
                if data[key] is not None:
                    dict_without_none.update({key: value})

            query = update(self.model).where(self.model.pk == pk).values(**dict_without_none)
            await self.session.execute(query)
        return entity

    # INFO не понимаю expressions
    async def filter(self, *expressions: BinaryExpression) -> list[Model]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(await self.session.scalars(query))
