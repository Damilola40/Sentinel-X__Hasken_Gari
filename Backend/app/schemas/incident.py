from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from uuid import UUID
from ..schemas.user import UserPatch
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


class IncidentData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, 
                              from_attributes=True,
                              populate_by_name=True)

    id: UUID
    title: str
    description: str
    category: str
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Literal["reported", "verified", "resolved", "unverified", "in_progress", "rejected"]
    location: Location
    created_at: datetime
    updated_at: Optional[datetime] = None
    reporter: UserPatch

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

class Meta(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page: int
    limit: int
    total: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool

class NearbyLocation(BaseModel):
    latitude: float
    longitude: float
    address: str

class NearbyIncidentData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: UUID
    title: str
    category: str
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Literal["reported", "verified", "resolved", "unverified", "in_progress", "rejected"]
    distance: float
    location: NearbyLocation
    created_at: datetime


class MapLocation(BaseModel):
    latitude: float
    longitude: float

class MapIncidentData(BaseModel):
    id: UUID
    title: str
    category: str
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Literal["reported", "verified", "resolved", "unverified", "in_progress", "rejected"]
    location: MapLocation