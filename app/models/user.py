from database import Base
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, LargeBinary, func, ForeignKey
from sqlalchemy.orm import relationship
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    provider_id = Column(String(255), index=True)
    provider = Column(String(255))
    # internal_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    internal_id = Column(String(36), default=uuid.uuid4)
    nickname = Column(String(255))
    profile_image = Column(String(255), nullable=True)
    survey_status = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(DateTime(timezone=True), nullable=True)
    vector = Column(LargeBinary, nullable=True)

    plans = relationship("Plan", back_populates="user")
    user_plan = relationship("UserPlan", back_populates="user")
    my_spots = relationship("MySpot", back_populates="user")
    urls = relationship("Url", back_populates="user")


# class MySpot(Base):
#     __tablename__ = "my_spots"

#     id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
#     spot_id = Column(BigInteger, ForeignKey("spots.id"), nullable=False)
#     memo = Column(String(255), nullable=True)
#     created_date = Column(String(255), nullable=True)

#     user = relationship("User", back_populates="my_spots")
#     spot = relationship("Spot", back_populates="my_spots")


# class Url(Base):
#     __tablename__ = "urls"

#     id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
#     url = Column(String(255), nullable=True)
#     title = Column(String(255), nullable=True)
#     memo = Column(String(255), nullable=True)
#     created_at = Column(String(255), nullable=True)

#     user = relationship("User", back_populates="urls")
