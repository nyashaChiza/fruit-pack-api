from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, String
from sqlalchemy.orm import relationship
from db.base import Base

class Cart(Base):
    __tablename__ = "Cart"  # Table name remains plural for clarity

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Integer, nullable=False)  # Store price at the time of adding to cart
    status = Column(String, nullable=False, default="Pending" )  # e.g., "active", "purchased", "removed"
    created = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")
    user = relationship("User")


