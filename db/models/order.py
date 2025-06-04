from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Float, String
from sqlalchemy.orm import relationship
from db.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Float, nullable=False)
    status = Column(String, nullable=False, default='pending')
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    

    # Relationship to Product
    product = relationship("Product", back_populates="orders")