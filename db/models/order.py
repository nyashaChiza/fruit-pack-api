from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Float, String
from sqlalchemy.orm import relationship
from db.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String, default='unpaid')  # 'paid' or 'credit'
    delivery_status = Column(String, default='pending')  # 'pending', 'processing', 'delivered', 'completed'
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    user = relationship("User", back_populates="orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # snapshot at time of purchase

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
