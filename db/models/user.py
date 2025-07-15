from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="customer")  # e.g., "customer", "driver", "admin"

    
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    orders = relationship("Order", back_populates="user")
    driver = relationship("Driver", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
