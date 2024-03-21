from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# class UserPlan(Base):
#     __tablename__ = "user_plan"

#     user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
#     plan_id = Column(BigInteger, ForeignKey("plans.id"), primary_key=True)

#     user = relationship("User", back_populates="user_plans")
#     plan = relationship("Plan", back_populates="user_plans")
