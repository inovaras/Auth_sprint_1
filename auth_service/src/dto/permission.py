import uu
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict




class PermissionCreateDTO(BaseModel):
    pk: uuid.UUID
    allowed: str
    role_id: uuid.UUID