from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    func,
    Boolean,
    LargeBinary,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base


class Url(Base):
    __tablename__ = "urls"

    id = Column(BigInteger, primary_key=True, index=True)
    creator_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    url = Column(String(2048), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String(255), nullable=True)
    image = Column(String(2048), nullable=True)
    description = Column(String(255), nullable=True)
    status = Column(String(6), nullable=False, default="None")
    vector = Column(LargeBinary, nullable=True)

    user = relationship("User", back_populates="urls")
