from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class MySpot(Base):
    __tablename__ = "my_spots"

    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    spot_id = Column(BigInteger, ForeignKey("spots.id"), nullable=False)
    memo = Column(String(255), nullable=True)
    created_date = Column(String(255), nullable=True)

    user = relationship("User", back_populates="my_spots")
    spot = relationship("Spot", back_populates="my_spots")
