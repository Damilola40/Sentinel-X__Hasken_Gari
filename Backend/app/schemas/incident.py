from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from uuid import UUID
from typing import Optional, Literal
from datetime import datetime

from ..schemas.user import UserPatch
from ..schemas.common import APIResponse, Meta


class Location(BaseModel):
    latitude: float
    longitude: float
    address: str
    city: str
    state: str


class LocationPatch(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class IncidentIn(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    location: Location

class IncidentData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, 
                              from_attributes=True,
                              populate_by_name=True)

    id: UUID
    title: str
    description: str
    category: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Literal["reported", "verified", "resolved", "unverified", "in_progress", "rejected"]
    location: Location
    created_at: datetime
    updated_at: Optional[datetime] = None

class IncidentPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[Literal["reported", "verified", "resolved", "unverified", "in_progress", "rejected"]] = None
    location: Optional[LocationPatch] = None


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