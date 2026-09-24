from fastapi import APIRouter, HTTPException, status, Response, Depends, Query
from .. core.deps import get_current_user
from typing import Optional
from datetime import datetime, timezone
from .. models.incident import Incident
from .. models.user import User
from .. schemas.incident import APIResponse, IncidentData
from .. schemas.dashboard import Overview, SafetyStatus, DashboardData
from .. routers.incidents import haversine_km
from math import radians, sin, cos, asin, sqrt
from sqlalchemy.orm import Session
from .. database import get_db

# Put all dashboard routes under the same URL and API tag.
dashboard_router = APIRouter(
    prefix = "/dashboard",
    tags = ["Dashboard"]
)

ACTIVE_STATUSES = {"reported", "verified", "unverified", "in_progress"}

def compute_safety_status(active_incidents: list[Incident]) -> SafetyStatus:
    if not active_incidents:
        return SafetyStatus(level="safe", message="No active incidents reported in your area.")

    severities = {i.severity for i in active_incidents}

    if "critical" in severities:
        return SafetyStatus(level="danger", message="Critical incident(s) reported nearby — exercise extreme caution.")
    if "high" in severities or len(active_incidents) >= 3:
        return SafetyStatus(level="caution", message="There are active incidents near your area.")
    return SafetyStatus(level="caution", message="Minor incidents reported nearby — stay alert.")

@dashboard_router.get("", response_model=APIResponse[DashboardData], status_code=status.HTTP_200_OK)
def display_dashboard(
    current_user: User = Depends(get_current_user),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius: float = Query(10, gt=0),
    db: Session = Depends(get_db),
):
    all_incidents = db.query(Incident).all()

    if latitude is not None and longitude is not None:
        scoped_incidents = [
            i for i in all_incidents
            if haversine_km(latitude, longitude, i.latitude, i.longitude) <= radius
        ]
    else:
        scoped_incidents = all_incidents

    active_incidents = [i for i in scoped_incidents if i.status in ACTIVE_STATUSES]

    today = datetime.now(timezone.utc).date()
    resolved_today = [
        i for i in scoped_incidents
        if i.status == "resolved" and i.updated_at.date() == today
    ]

    overview = Overview(
        nearby_reports=len(scoped_incidents),
        active_incidents=len(active_incidents),
        resolved_today=len(resolved_today),
    )

    safety_status = compute_safety_status(active_incidents)

    recent_incidents = (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .limit(5)
        .all()
    )

    dashboard_data = DashboardData(
        overview=overview,
        safety_status=safety_status,
        recent_incidents=recent_incidents,
    )

    return APIResponse(success=True, message="Dashboard retrieved successfully", data=dashboard_data)