from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.order import OrderCreate, OrderUpdate, OrderResponse
from db.models.order import Order, OrderItem
from db.session import get_db
from sqlalchemy.orm import Session
from db.models.product import Product as ProductModel
from core.auth import get_current_user
from db.models.user import User
from fastapi import Body

router = APIRouter(tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = Order(
        user_id=current_user.id,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order.items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        order_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(order_item)

    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/{order_id}", response_model=OrderResponse)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/{order_id}", response_model=dict)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"detail": "Order deleted successfully"}

@router.get("/", response_model=List[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/{order_id}/items")
def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    return [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": item.price
        }
        for item in items
    ]



@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Optional: Add role check if needed (e.g. if only supplier can update certain statuses)

    if status_data.status:
        db_order.status = status_data.status
        db.commit()
        db.refresh(db_order)

    return db_order


@router.post("/{order_id}/confirm-delivery", response_model=OrderResponse)
def confirm_delivery(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    db_order.status = "completed"
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/user/{user_id}/orders", response_model=List[OrderResponse])
def get_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created.desc())
        .all()
    )
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")

    return orders