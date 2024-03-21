from sqlalchemy import Column, BigInteger, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base


class VisitPlace(Base):
    __tablename__ = "visit_place"

    id = Column(BigInteger, primary_key=True, index=True)
    travel_id = Column(BigInteger, ForeignKey("plans.id"), nullable=False)
    internal_id = Column(BigInteger, nullable=False)  # 계획 관리자
    spot_id = Column(BigInteger, ForeignKey("spots.id"), nullable=False)
    date = Column(String(255), nullable=True)
    time = Column(String(255), nullable=True)
    memo = Column(String(255), nullable=True)

    plan = relationship("Plan", back_populates="visit_places")
    spot = relationship("Spot", back_populates="visit_places")
