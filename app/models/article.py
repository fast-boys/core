from sqlalchemy import Column, String
from database import Base


class Article(Base):
    __tablename__ = "article"

    Key = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    content = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    url = Column(String(255), nullable=True)
