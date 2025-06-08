from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base
from sqlalchemy import Column, DateTime, func

class Category(Base):
    __tablename__ = "Categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=True)  # Optional icon field for category
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # This line is needed if you want to access all products for a category
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
