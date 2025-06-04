from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

    # This line is needed if you want to access all orders for a product
    orders = relationship("Order", back_populates="product")