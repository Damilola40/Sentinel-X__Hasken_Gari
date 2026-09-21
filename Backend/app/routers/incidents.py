from fastapi import APIRouter, HTTPException, status, Response, Depends, Query
from .. core.deps import get_current_user
from .. schemas.incident import IncidentIn, IncidentData, IncidentPatch, APIResponse, NearbyIncidentData, MapIncidentData, Meta
from .. models.incident import Incident
from .. models.user import User
from typing import Optional, List
from math import radians, sin, cos, asin, sqrt
import uuid
from sqlalchemy.orm import Session
from .. database import get_db

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

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Distance between two lat/lng points in km."""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))
        
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
    # Pull all incidents
    incidents = db.query(Incident).all()

    nearby = []
    for i in incidents:
        distance = haversine_km(latitude, longitude, i.latitude, i.longitude)
        if distance <= radius:
            nearby.append({
                "id": i.id,
                "title": i.title,
                "category": i.category,
                "severity": i.severity,
                "status": i.status,
                "distance": round(distance, 2),
                "location": {
                    "latitude": i.latitude,
                    "longitude": i.longitude,
                    "address": i.address,
                },
                "created_at": i.created_at,
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
    incidents = db.query(Incident).all()
    
    map_data = []
    for i in incidents:
        distance = haversine_km(latitude, longitude, i.latitude, i.longitude)
        if distance <= radius:
            map_data.append({
                "id": i.id,
                "title": i.title,
                "category": i.category,
                "severity": i.severity,
                "status": i.status,
                "location": {
                    "latitude": i.latitude,
                    "longitude": i.longitude,
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
@incidents_router.post("/",
             response_model=APIResponse[IncidentData],
             status_code=status.HTTP_201_CREATED
             )

def create_incident(incident_data: IncidentIn, 
                    db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user)):
    # Save the location details from the request.
    new_incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        category=incident_data.category,
        status="reported",
        severity=None,
        latitude=incident_data.location.latitude,
        longitude=incident_data.location.longitude,
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
    
    # Only change fields sent by the user.
    if incident_data.title is not None:
        incident.title = incident_data.title
    if incident_data.description is not None:
        incident.description = incident_data.description
    if incident_data.category is not None:
        incident.category = incident_data.category
    if incident_data.location is not None:
        incident.latitude = incident_data.location.latitude
        incident.longitude = incident_data.location.longitude
        incident.address = incident_data.location.address
        incident.city = incident_data.location.city
        incident.state = incident_data.location.state

    db.commit()
    db.refresh(incident)
    return APIResponse(success=True, message="Existing Incident Recorded", data=incident)

# Delete incident from database
@incidents_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)

def delete_incident(id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
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
