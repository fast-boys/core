from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class PlanCity(Base):
    __tablename__ = "plan_city"

    plan_id = Column(BigInteger, ForeignKey("plans.id"), primary_key=True)
    city_id = Column(BigInteger, ForeignKey("cities.id"), nullable=False)

    plan = relationship("Plan", back_populates="plan_citys")
    city = relationship("City", back_populates="plan_citys")
