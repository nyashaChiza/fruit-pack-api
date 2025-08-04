from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Float, String
from sqlalchemy.orm import relationship
import random
from db.base import Base

from nanoid import generate

def generate_order_id():
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # 32 unique characters
    return generate(alphabet, 10)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    total_amount = Column(Float, nullable=False)
    destination_address = Column(String, nullable=True)
    order_number = Column(String, unique=True, nullable=False, default=generate_order_id)
    destination_latitude = Column(Float, nullable=True)
    destination_longitude = Column(Float, nullable=True)
    payment_method = Column(String, nullable=True)  # e.g., 'card', 'cash', 'paypal'
    customer_phone = Column(String, nullable=True)  # Customer's phone number
    customer_name = Column(String, nullable=True)  # Customer's name for delivery
    payment_status = Column(String, default='unpaid')  # 'paid' or 'credit'
    delivery_status = Column(String, default='pending')  # 'pending', 'processing', 'delivered', 'completed'
    delivery_code = Column(Integer, default=random.randint(10000,99999))
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    driver = relationship("Driver", back_populates="orders")
    user = relationship("User", back_populates="orders")
    claim = relationship("DriverClaim", uselist=False, back_populates="order")
    
    @property
    def total(self):
        return sum(item.price * item.quantity for item in self.items)




class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # snapshot at time of purchase

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
