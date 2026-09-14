from pydantic import BaseModel #, ConfigDict
from uuid import UUID
#from pydantic.alias_generators import to_camel
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
    title: str
    description: str
    category: str
    location: Location
    reporter_id: Optional[str] = None

    class Config:
        from_attributes = True

class IncidentData(BaseModel):
    id: UUID
    title: str
    description: str
    category: str
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Literal["reported", "verified", "resolved", "unverified", "in_progress", "rejected"]
    location: Location
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
            from_attributesfrom_attributes = True

class IncidentPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[Literal["reported", "verified", "resolved", "unverified", "in_progress", "rejected"]] = None
    location: Optional[Location] = None

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T