from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional
from ..schemas.common import APIResponse, Meta
from uuid import UUID
from datetime import datetime

class NotificationData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, 
                              from_attributes=True,
                              populate_by_name=True)

    id: UUID
    user_id: UUID
    title: str
    message: str
    type: str
    read: bool
    incident_id: Optional[UUID] = None
    created_at: datetime