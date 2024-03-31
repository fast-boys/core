from sqlalchemy import Column, BigInteger, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base


class VisitSpot(Base):
    __tablename__ = "visit_spots"

    id = Column(BigInteger, primary_key=True, index=True)
    plan_id = Column(BigInteger, ForeignKey("plans.id"), nullable=False)
    creator_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)  # 계획 관리자
    spot_id = Column(BigInteger, nullable=False)
    date = Column(Date, nullable=True)

    plan = relationship("Plan", back_populates="visit_spots")
