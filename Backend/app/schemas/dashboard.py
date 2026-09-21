from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Literal, Generic, TypeVar

T = TypeVar("T")

from .incident import IncidentData

class Overview(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    nearby_reports: int
    active_incidents: int
    resolved_today: int

class SafetyStatus(BaseModel):
    level: Literal["safe", "caution", "danger"]
    message: str

class DashboardData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    overview: Overview
    safety_status: SafetyStatus
    recent_incidents: list[IncidentData]

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T