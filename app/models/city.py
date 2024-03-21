from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship
from database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    title_image_url = Column(String(255), nullable=True)

    plan_citys = relationship("PlanCity", back_populates="city")
