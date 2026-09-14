from sqlalchemy import Column, Enum, String, DateTime, Float, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    severity = Column(Enum("low", "medium", "high", "critical", name="incident_severity"), nullable=True)
    status = Column(Enum("reported", "verified", "resolved", "unverified", "in_progress", "rejected", name="incident_status"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reporter = relationship("User")

    @property
    def location(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "city": self.city,
            "state": self.state,
        }