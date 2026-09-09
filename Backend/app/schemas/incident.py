from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, Literal, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")

class Location(BaseModel):
    latitude: float
    longitude: float
    address: str
    city: str
    state: str

class IncidentIn(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: str
    description: str
    category: str
    location: Location
    reporter_id: Optional[str] = None

class IncidentData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    title: str
    description: str
    category: str
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Literal["reported", "verified", "resolved", "unverified", "in_progress", "rejected"]
    location: Location
    created_at: datetime
    updated_at: Optional[datetime] = None

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T