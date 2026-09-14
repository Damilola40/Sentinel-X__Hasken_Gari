"""Routes for creating, viewing, changing, and deleting incidents."""

from fastapi import APIRouter, HTTPException, status, Response, Depends

from ..core.deps import get_current_user
from .. schemas.incident import IncidentIn, IncidentData, IncidentPatch, APIResponse
from .. models.incident import Incident
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
        
# Only signed-in users can view incidents.
@incidents_router.get("/", 
            response_model=APIResponse[list[IncidentData]],
            status_code=status.HTTP_200_OK
            )
def list_incidents(db: Session = Depends(get_db),
                    user_id: int = Depends(get_current_user)):
    incidents = db.query(Incident).all()
    return APIResponse(success=True, message="Incidents Listed", data=incidents)

@incidents_router.get("/{id}", 
            response_model=APIResponse[IncidentData],
            status_code=status.HTTP_200_OK
            )

def get_incident(id: str, db: Session = Depends(get_db), 
                    user_id: int = Depends(get_current_user)):
    # Check the ID before looking for the incident.
    try:
        incident_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id format")
    
    incident = db.query(Incident).filter(Incident.id == incident_uuid).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")
    
    return APIResponse(success=True, message="Incident Found", data=incident)

@incidents_router.post("/",
             response_model=APIResponse[IncidentData],
             status_code=status.HTTP_201_CREATED
             )

def create_incident(incident_data: IncidentIn, 
                    db: Session = Depends(get_db), 
                    user_id: int = Depends(get_current_user)):

    print(user_id)
    
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
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return APIResponse(success=True, message="New Incident Recorded!!!", data=new_incident)


@incidents_router.patch("/{id}", 
            response_model=APIResponse[IncidentData],
            status_code=status.HTTP_200_OK
            )

def update_incident(id: str, incident_data: IncidentPatch, 
                    db: Session = Depends(get_db), 
                    user_id: int = Depends(get_current_user)):
    try:
        incident_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid incident id format")
    
    incident = db.query(Incident).filter(Incident.id == incident_uuid).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")
    
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


@incidents_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(id: str, db: Session = Depends(get_db), 
                    user_id: int = Depends(get_current_user)):
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
