from sqlalchemy import JSON, Column, BigInteger, Date, String, Time, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(BigInteger, primary_key=True, index=True)
    creator_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    title_image_url = Column(String(255), nullable=True)
    cities = Column(JSON, nullable=True)
    user = relationship("User", back_populates="plans")
    user_plans = relationship("UserPlan", back_populates="plan")
    visit_spots = relationship("VisitSpot", back_populates="plan")
