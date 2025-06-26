from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('Categories.id'))
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    image = Column(String, nullable=True)  # Stores image filename or path

    # This line is needed if you want to access all orders for a product
    order_items = relationship("OrderItem", back_populates="product")
    supplier = relationship("Supplier", back_populates="products")
    category = relationship("Category", back_populates="products")