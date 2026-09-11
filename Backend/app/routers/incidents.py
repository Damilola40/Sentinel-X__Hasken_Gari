from fastapi import APIRouter, HTTPException, status, Response, Depends
from app.schemas.incident import IncidentIn, IncidentData, IncidentPatch, APIResponse
from app.models.incident import Incident
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session
from app.database import get_db

incidents_router = APIRouter()
#data = get_db.incident


# Helper functions
def find_incident(id):
    for incident in get_db().query(Incident).all():
        if incident.id == id:
            return incident

def find_index_incident(id):
    for index, incident in enumerate(get_db().query(Incident).all()):
        if incident["id"] == id:
            return index
        
## GET routers
# GET all incidents
@incidents_router.get("/incidents", 
            response_model=APIResponse[list[IncidentData]],
            status_code=status.HTTP_200_OK
            )
def list_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).all()
    return APIResponse(success=True, message="Incidents Listed", data=incidents)

# GET incident by id
@incidents_router.get("/incidents/{id}", 
            response_model=APIResponse[IncidentData],
            status_code=status.HTTP_200_OK
            )

def get_incident(id: str, db: Session = Depends(get_db)):
    try:
        incident_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id format")
    
    incident = db.query(Incident).filter(Incident.id == incident_uuid).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")
    
    return APIResponse(success=True, message="Incident Found", data=incident)

# Incident POST router - create a new incident
@incidents_router.post("/incidents",
             response_model=APIResponse[IncidentData],
             status_code=status.HTTP_201_CREATED
             )

def create_incident(incident_data: IncidentIn, db: Session = Depends(get_db)):
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
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return APIResponse(success=True, message="New Incident Recorded!!!", data=new_incident)


# Incident PATCH router - update an existing incident
@incidents_router.patch("/incidents/{id}", 
            response_model=APIResponse[IncidentData],
            status_code=status.HTTP_200_OK
            )

def update_incident(id: str, incident_data: IncidentPatch, db: Session = Depends(get_db)):
    try:
        incident_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id format")
    
    incident = db.query(Incident).filter(Incident.id == incident_uuid).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")
    
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


# Incident DELETE router - delete an existing incident
@incidents_router.delete("/incidents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(id: str, db: Session = Depends(get_db)):
    try:
        incident_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id format")

    incident = db.query(Incident).filter(Incident.id == incident_uuid).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"incident with {id}, not found")

    db.delete(incident)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)