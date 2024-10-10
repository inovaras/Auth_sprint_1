import uuid

from pydantic import BaseModel


class PermissionCreateDTO(BaseModel):
    pk: uuid.UUID
    allowed: str
    role_id: uuid.UUID
