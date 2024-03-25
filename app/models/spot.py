from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Spot(Base):
    __tablename__ = "spots"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    lat = Column(String(255), nullable=False)
    long = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    category = Column(
        String(255), nullable=True
    )  # Assuming it's stored as a JSON string or similar.

    visit_places = relationship("VisitPlace", back_populates="spot")
    my_spots = relationship("MySpot", back_populates="spot")
    # properties = relationship("Properties", back_populates="spot", uselist=False)
    url_des = relationship("UrlDes", back_populates="spot")


class UrlDes(Base):
    __tablename__ = "url_des"

    depiction_id = Column(BigInteger, primary_key=True, index=True)
    spot_id = Column(BigInteger, ForeignKey("spots.id"), nullable=False)
    url = Column(String(255), nullable=True)

    spot = relationship("Spot", back_populates="url_des")
