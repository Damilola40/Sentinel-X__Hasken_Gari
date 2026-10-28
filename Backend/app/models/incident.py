from sqlalchemy import Column, Enum, String, DateTime, Boolean, func, ForeignKey, false
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import uuid

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    severity = Column(Enum("low", "medium", "high", "critical", name="incident_severity"), nullable=True)
    status = Column(Enum("reported", "verified", "resolved", "unverified", "in_progress", "rejected", name="incident_status"), nullable=False)
    flagged_for_review = Column(Boolean, default=False, server_default="false", nullable=False)
    geom = Column("location", Geometry(geometry_type="POINT", srid=4326), nullable=False)
    # latitude = Column(Float, nullable=False)
    # longitude = Column(Float, nullable=False) POSTGIS has been setup these are replaced by location_geom
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reporter = relationship("User")

    # Commented out to properly handle backfill
    # To use this change location to location_geom 
    @property
    def location(self):
        point = to_shape(self.geom)
        return {
            "latitude": point.y,
            "longitude": point.x,
            # "latitude": self.latitude,
            # "longitude": self.longitude, PostGIS setup
            "address": self.address,
            "city": self.city,
            "state": self.state,
        }

