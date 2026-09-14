from sqlalchemy import Column, Enum, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from .. database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=True, unique=True)
    phone_number = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)
    role = Column(Enum("citizen", "responder", "admin", name="user_role"), nullable=False)
    created_at = Column(DateTime(timezone=True), 
                       nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), 
                       server_default=func.now(), onupdate=func.now())
    incidents = relationship("Incident")