from fastapi import APIRouter, HTTPException, status, Response
from app.schemas.incident import IncidentIn, IncidentData, APIResponse
from datetime import datetime, timezone
import uuid
from app import fake_db as db

incidents_router = APIRouter()
data = db.incidents

def find_incident(id):
    for incident in db.incidents:
        if incident["id"] == id:
            return incident

def find_index_incident(id):
    for index, incident in enumerate(db.incidents):
        if incident["id"] == id:
            return index

@incidents_router.get("/incidents", 
            response_model=APIResponse[list[IncidentData]],
            status_code=status.HTTP_200_OK
            )
def list_incidents():
    return APIResponse(success=True, message="Incidents Listed", data=db.incidents)

@incidents_router.get("/incidents/{id}", 
            response_model=APIResponse[IncidentData],
            status_code=status.HTTP_200_OK
            )
def get_incident(id: str,):
    incident = find_incident(id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")
    return APIResponse(success=True, message="Incident Found", data=incident)

@incidents_router.post("/incidents", 
             response_model=APIResponse[IncidentData], 
             status_code=status.HTTP_201_CREATED
             )
def create_incident(incident_data: IncidentIn):
    new_incident = {
        "id": str(uuid.uuid4()),
        "title": incident_data.title,
        "description": incident_data.description,
        "category": incident_data.category,
        "severity": None,
        "status": "reported",
        "location": {
            "latitude": incident_data.location.latitude,
            "longitude": incident_data.location.longitude,
            "address": incident_data.location.address,
            "city": incident_data.location.city,
            "state": incident_data.location.state
        },
        "created_at": datetime.now(timezone.utc)
    }
    db.incidents.append(new_incident)
    return APIResponse(success=True, message="New Incident Recorded!!!", data=new_incident)

@incidents_router.put("/incidents/{id}", 
            response_model=APIResponse[IncidentData],
            status_code=status.HTTP_202_ACCEPTED
            )
def update_incident(id: str, incident_data: IncidentIn):
    incident_index = find_index_incident(id)
    if incident_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")
    updated_incident = {
            "id": id,
            "title": incident_data.title,
            "description": incident_data.description,
            "category": incident_data.category,
            "severity": db.incidents[incident_index]["severity"],
            "status": db.incidents[incident_index]["status"],
            "location": {
                "latitude": incident_data.location.latitude,
                "longitude": incident_data.location.longitude,
                "address": incident_data.location.address,
                "city": incident_data.location.city,
                "state": incident_data.location.state
            },
            "created_at": db.incidents[incident_index]["created_at"],
            "updated_at": datetime.now(timezone.utc)
        }
    db.incidents[incident_index] = updated_incident
    return APIResponse(success=True, message="Existing Incident Recorded", data=updated_incident)

@incidents_router.delete("/incidents/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(id: str):
    incident_index = find_index_incident(id)
    if incident_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"incident with {id}, not found")
    db.incidents.pop(incident_index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)