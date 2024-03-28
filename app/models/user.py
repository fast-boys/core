from database import Base
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    DateTime,
    LargeBinary,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    provider_id = Column(String(255), index=True)
    provider = Column(String(255))
    # internal_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    internal_id = Column(String(36), nullable=False, unique=True, index=True)
    nickname = Column(String(255))
    profile_image = Column(String(255), nullable=True)
    survey_status = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    vector = Column(LargeBinary, nullable=True)

    plans = relationship("Plan", back_populates="user")
    user_plans = relationship("UserPlan", back_populates="user")
    my_spots = relationship("MySpot", back_populates="user")
    urls = relationship("Url", back_populates="user")
