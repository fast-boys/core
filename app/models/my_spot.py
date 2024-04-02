from sqlalchemy import Boolean, Column, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class MySpot(Base):
    __tablename__ = "my_spots"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    spot_id = Column(BigInteger, nullable=False)
    memo = Column(String(255), nullable=True)
    like_status = Column(Boolean, nullable=False, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="my_spots")
