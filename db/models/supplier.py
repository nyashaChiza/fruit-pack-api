from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base
from sqlalchemy import Column, DateTime, func

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # This line is needed if you want to access all products for a supplier
    products = relationship("Product", back_populates="supplier", cascade="all, delete-orphan")