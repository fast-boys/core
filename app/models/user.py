from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(String, index=True)
    provider = Column(String)
    internal_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    nickname = Column(String)
    profile_image = Column(String, nullable=True)
    survey_status = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(DateTime(timezone=True), nullable=True)
