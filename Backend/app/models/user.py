from sqlalchemy import Column, Enum, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=True, unique=True)
    phoneNumber = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True, unique=True)
    hashedPassword = Column(String, nullable=True)
    role = Column(Enum("citizen", "responder", "admin", name="user_role"), nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    reporter = relationship("Incident")