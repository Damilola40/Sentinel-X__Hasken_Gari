from fastapi import APIRouter, HTTPException, status, Response, Depends, Query
from geoalchemy2.elements import WKTElement
from typing import Optional, List
# from math import radians, sin, cos, asin, sqrt
from sqlalchemy import func
from geoalchemy2 import Geography
import uuid
from sqlalchemy.orm import Session
import logging


from ..core.deps import get_current_user
from ..schemas.common import APIResponse, Meta
from ..schemas.incident import IncidentIn, IncidentData, IncidentPatch, NearbyIncidentData, MapIncidentData
from ..models.incident import Incident
from ..models.user import User
from ..database import get_db
from ..ai.ai_config import AIConfig
from ..ai.service import classify_report


# Put all incident routes under the same URL and API tag.
incidents_router = APIRouter(
    prefix = "/incidents",
    tags = ["Incidents"]
)

# Helper functions
def find_incident(id):
    for incident in get_db().query(Incident).all():
        if incident.id == id:
            return incident

def find_index_incident(id):
    for index, incident in enumerate(get_db().query(Incident).all()):
        if incident["id"] == id:
            return index

logger = logging.getLogger(__name__)

AI_CATEGORY_MIN_CONF = 0.60
AI_SEVERITY_MIN_CONF = 0.60

# No longer used as POSTGIS has been setup
"""def haversine_km(lat1, lon1, lat2, lon2) -> float:
    #Distance between two lat/lng points in km.
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))"""
        
# Only signed-in users can view incidents.
# Get all incidents
@incidents_router.get("",
            response_model=APIResponse[list[IncidentData]],
            status_code=status.HTTP_200_OK
            )
def list_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    ):
    query = db.query(Incident)

    if status_filter:
        query = query.filter(Incident.status == status_filter)

    total = query.count()
    incidents = query.offset((page - 1) * limit).limit(limit).all()
    total_pages = (total + limit - 1) // limit

    meta = Meta(
        page=page, limit=limit, total=total, total_pages=total_pages,
        has_next_page=page < total_pages, has_previous_page=page > 1,
    )

    return APIResponse(success=True, message="Incidents retrieved successfully", data=incidents, meta=meta)


# Get incident by latitude, longitude and radius
@incidents_router.get(
    "/nearby",
    response_model=APIResponse[List[NearbyIncidentData]],
    status_code=status.HTTP_200_OK,
)
def get_nearby_incidents(
    current_user: User = Depends(get_current_user),
    latitude: float = Query(..., ge=-90, le=90, description="Center latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Center longitude"),
    radius: float = Query(10, gt=0, description="Radius in kilometers"),
    db: Session = Depends(get_db),
    ):
    # 
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    distance_m = func.ST_Distance(
        func.cast(Incident.geom, Geography),
        func.cast(point, Geography),
    )

    # 
    results = (
        db.query(Incident, distance_m.label("distance"))
        .filter(func.ST_DWithin(
            func.cast(Incident.geom, Geography),
            func.cast(point, Geography),
            radius * 1000,  # km -> meters
        ))
        .order_by(distance_m)
        .all()
    )

    nearby = []
    for incident, distance in results:
        nearby.append({
            "id": incident.id,
            "title": incident.title,
            "category": incident.category,
            "severity": incident.severity,
            "status": incident.status,
            "distance": round(distance / 1000, 2),  # meters -> km
            "location": {
                "latitude": incident.location["latitude"],
                "longitude": incident.location["longitude"],
                "address": incident.location["address"],
            },
            "created_at": incident.created_at,
        })

    if not nearby:
        return APIResponse(success=True, message="No incidents found within radius", data=[])

    return APIResponse(success=True, message=f"{len(nearby)} incident(s) found nearby", data=nearby)


@incidents_router.get(
        "/map",
        response_model=APIResponse[List[MapIncidentData]],
        status_code=status.HTTP_200_OK,
)
def map_incidents(
    current_user: User = Depends(get_current_user),
    latitude: float = Query(..., ge=-90, le=90, description="Center latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Center longitude"),
    radius: float = Query(20, gt=0, description="Radius in kilometers"),
    db: Session = Depends(get_db),
):
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    
    results = (
        db.query(Incident)
        .filter(func.ST_DWithin(
            func.cast(Incident.geom, Geography),
            func.cast(point, Geography),
            radius * 1000,  # km -> meters
        ))
        .all()
    )
    
    map_data = []
    for incident in results:
            map_data.append({
                "id": incident.id,
                "title": incident.title,
                "category": incident.category,
                "severity": incident.severity,
                "status": incident.status,
                "location": {
                    "latitude": incident.location["latitude"],
                    "longitude": incident.location["longitude"],
                },
            })
    
    if not map:
        return APIResponse(success=True, message="No incidents found within radius", data=[])
    
    return APIResponse(success=True, message=f"{len(map_data)} incident(s) found.", data=map_data)


# Get incidents by id
@incidents_router.get("/{id}", 
            response_model=APIResponse[IncidentData],
            status_code=status.HTTP_200_OK
            )

def get_incident(id: str, db: Session = Depends(get_db), 
                    current_user: int = Depends(get_current_user)):
    # Check the ID before looking for the incident
    try:
        incident_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id format")
    
    incident = db.query(Incident).filter(Incident.id == incident_uuid).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")
    
    return APIResponse(success=True, message="Incident Found", data=incident)

# Create new incident on the database
@incidents_router.post("",
             response_model=APIResponse[IncidentData],
             status_code=status.HTTP_201_CREATED
             )

def create_incident(incident_data: IncidentIn, 
                    db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user)):
    # Classify the incident using the AI model
    try:
        result = classify_report(title=incident_data.title, description=incident_data.description)
        logger.info(f"AI Classification Result: {result}")  # Debugging line to check the classification result
    except Exception:
        logger.exception("AI classification failed")
        result = None
    
    category = incident_data.category.strip().lower()
    severity = None
    if result:
        if result["category_confidence"] >= AI_CATEGORY_MIN_CONF:
            category = result["category"]
        if result["severity_confidence"] >= AI_SEVERITY_MIN_CONF:
            severity = result["severity"]
    if category not in AIConfig.CATEGORIES:
        category = "other"

    # Save the location details from the request.
    new_incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        category=category,
        status="reported",
        severity=severity,
        geom=WKTElement(
            f"POINT({incident_data.location.longitude} {incident_data.location.latitude})",
            srid=4326,
        ),
        address=incident_data.location.address,
        city=incident_data.location.city,
        state=incident_data.location.state,
        reporter_id=current_user.id
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return APIResponse(success=True, message="New Incident Recorded!!!", data=new_incident)

# Edit existing incident on the database
@incidents_router.patch("/{id}", 
            response_model=APIResponse[IncidentData],
            status_code=status.HTTP_200_OK
            )

def update_incident(id: str, incident_data: IncidentPatch, 
                    db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user)):

    # Check if the user is authorized to update an incident
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    
    try:
        incident_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id format")
    
    incident_query = db.query(Incident).filter(Incident.id == incident_uuid)

    incident = incident_query.first()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")

    if incident.reporter_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not authorized to perform requested action")
    
    if incident_data.location is not None:
        loc = incident_data.location
        current = incident.location  # existing @property — decodes current geom + reads address/city/state

        if loc.latitude is not None or loc.longitude is not None:
            new_lat = loc.latitude if loc.latitude is not None else current["latitude"]
            new_lon = loc.longitude if loc.longitude is not None else current["longitude"]
            incident.geom = WKTElement(f"POINT({new_lon} {new_lat})", srid=4326)

        if loc.address is not None:
            incident.address = loc.address
        if loc.city is not None:
            incident.city = loc.city
        if loc.state is not None:
            incident.state = loc.state

    db.commit()
    db.refresh(incident)
    return APIResponse(success=True, message="Existing Incident Recorded", data=incident)

# Delete incident from database
@incidents_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)

def delete_incident(id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):

    # Check if the user is authorized to delete an incident
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    try:
        incident_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id format")

    incident = db.query(Incident).filter(Incident.id == incident_uuid).first()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"incident with {id}, not found")

    if incident.reporter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    db.delete(incident)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
