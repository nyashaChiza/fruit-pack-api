from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    vehicle_number = Column(String, nullable=True)
    status = Column(String, default="available")  # e.g., "available", "busy", "offline"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="driver")
    orders = relationship("Order", back_populates="driver")
    claims = relationship("DriverClaim", back_populates="driver")