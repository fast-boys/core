from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class MySpot(Base):
    __tablename__ = "my_spots"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    spot_id = Column(BigInteger, nullable=False)
    memo = Column(String(255), nullable=True)
    created_date = Column(String(255), nullable=True)

    user = relationship("User", back_populates="my_spots")
