from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderLocationUpdate, OrderItemResponse
from db.models.order import Order, OrderItem
from db.models.driver_claims import DriverClaim
from db.session import get_db
from helpers import distance_between
from sqlalchemy.orm import Session, joinedload
from db.models.product import Product as ProductModel
from db.models.driver import Driver
from core.auth import get_current_user
from db.models.user import User
from db.models import notify_user
from fastapi import Body
from pydantic import BaseModel

router = APIRouter()


@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = Order(
        user_id=current_user.id,
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
        product.stock -= item.quantity  # Decrease stock
        db.add(product)  # Update product stock in the database
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
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()

    # If current user is not a driver, fallback to the driver assigned to the order
    if not driver and order.driver_id:
        driver = db.query(Driver).filter(Driver.id == order.driver_id).first()
        

    distance_km = None
    if driver:
        if all([driver.latitude is not None, driver.longitude is not None, order.destination_latitude is not None, order.destination_longitude is not None]):
            distance_km = distance_between(
            {'lat': driver.latitude, 'lng': driver.longitude},
            {'lat': order.destination_latitude, 'lng': order.destination_longitude}
        )
        distance_km = round(distance_km, 2)

        order_data = OrderResponse(
        id=order.id,
                user_id=order.user_id,
                driver_id=order.driver_id,
                customer_name=order.customer_name,
                customer_phone=order.customer_phone,
                destination_address=order.destination_address,
                delivery_status=order.delivery_status,
                payment_status=order.payment_status,
                payment_method=order.payment_method,
                destination_latitude=order.destination_latitude,
                destination_longitude=order.destination_longitude,
                distance_from_driver=distance_km,
                created=order.created,
                updated=order.updated,
                total=order.total,  
                items=order.items or []  # Ensure items is always a list
            )
        return order_data
    else:
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
    orders = db.query(Order).all()
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
def update_delivery_order_status(
    order_id: int,
    status_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Optional: Add role check if needed (e.g. if only supplier can update certain statuses)
    if status_data.status == 'delivered' and db_order.payment_method == 'cash':
        db_order.payment_status = 'paid'
        driver = db.query(Driver).filter(Driver.id == db_order.driver_id).first()
        if driver:
            driver.status = 'available'

    if status_data.status:
        db_order.delivery_status = status_data.status
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
    
    db_order.delivery_status = "completed"
    db.commit()
    db.refresh(db_order)
    notify_user(db, db_order.user_id, f"Order #{db_order.id} delivery has been Completed",'Order Completed','Order', db_order.id)

    return db_order

@router.get("/user/{user_id}/orders", response_model=List[OrderResponse])
def get_orders_by_user(user_id: int, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created.desc())
        .all()
    )
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")

    return orders


@router.get("/driver/{driver_id}/orders", response_model=List[OrderResponse])
def get_orders_by_driver(driver_id: int, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    orders = (
        db.query(Order)
        .filter(Order.driver_id == driver_id)
        .filter(Order.delivery_status == 'shipped')
        .order_by(Order.created.desc())
        .all()
    )
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this driver")

    return orders

@router.get("/available/orders", response_model=List[OrderResponse])
def get_available_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()

    if not driver:
        orders = (
        db.query(Order)
        .options(joinedload(Order.items))  # ✅ Eager-load order items
        .filter(Order.driver_id == None)
        .order_by(Order.created.desc())
        .all()
       )
        return orders

    orders = (
        db.query(Order)
        .options(joinedload(Order.items))  # ✅ Eager-load order items
        .filter(Order.driver_id == None)
        .order_by(Order.created.desc())
        .all()
    )

    if not orders:
        raise HTTPException(status_code=404, detail="No available orders found")

    result = []
    for order in orders:
        distance = None
        if (
            driver.latitude is not None and driver.longitude is not None
            and order.destination_latitude is not None and order.destination_longitude is not None
        ):
            distance = distance_between(
                {'lat': driver.latitude, 'lng': driver.longitude},
                {'lat': order.destination_latitude, 'lng': order.destination_longitude}
            )

        # 🔧 Manual mapping
        item_responses = [
            OrderItemResponse.from_orm(item)
            for item in order.items
        ]

        order_data = OrderResponse(
            id=order.id,
            user_id=order.user_id,
            driver_id=order.driver_id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            destination_address=order.destination_address,
            delivery_status=order.delivery_status,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            destination_latitude=order.destination_latitude,
            destination_longitude=order.destination_longitude,
            distance_from_driver=distance,
            created=order.created,
            updated=order.updated,
            total=order.total,  # ⚠️ Double-check: total vs total_amount?
            items=item_responses
        )

        result.append(order_data)

    return result
@router.get("/status/{delivery_status}/driver/{driver_id}/orders", response_model=List[OrderResponse])
def get_orders_by_delivery_status(delivery_status: str, driver_id: int, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    if delivery_status == 'unassigned':
        orders = (
            db.query(Order)
            .filter(Order.driver_id.is_(None), Order.payment_status != 'unpaid')
            .order_by(Order.created.desc())
            .all()
        )
    elif delivery_status == 'assigned':
        orders = (
            db.query(Order)
            .filter(Order.driver_id == driver_id)
            .order_by(Order.created.desc())
            .all()
        )
    elif delivery_status == 'delivered':
        orders = (
            db.query(Order)
            .filter(Order.delivery_status == 'delivered', Order.driver_id == driver_id)
            .order_by(Order.created.desc())
            .all()
        )
    else:
        raise HTTPException(status_code=404, detail="No orders found for this driver")

    return orders

class AssignDriverRequest(BaseModel):
    driver_id: int

@router.put("/{order_id}/assign-driver", response_model=OrderResponse)
def assign_driver_to_order(
    order_id: int,
    data: AssignDriverRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Assign driver to order
    db_order.driver_id = data.driver_id
    db_order.delivery_status = "shipped"

    # Update driver status
    driver = db.query(Driver).filter(Driver.id == data.driver_id).first()
    if driver:
        driver.status = "busy" 

    # Create DriverClaim with status "approved"
      # adjust import if needed
    driver_claim = DriverClaim(
        order_id=order_id,
        driver_id=data.driver_id,
        status="approved"
    )
    db.add(driver_claim)

    db.commit()
    db.refresh(db_order)
    notify_user(db, db_order.driver_id, f"Order #{db_order.id} delivery has been Assigned a Driver",'Order Assigned','Order', db_order.id)

    return db_order

@router.post("/order/{order_id}/location")
def update_order_location(
    location: OrderLocationUpdate,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    order = db.query(Order).filter(Order.id == order_id).first()
    order.destination_latitude = location.latitude
    order.destination_longitude = location.longitude
    db.commit()
    db.refresh(order)
    return {"detail": "Location updated"}

@router.get("/driver/{driver_id}/delivered-orders", response_model=List[OrderResponse])
def get_driver_delivered_orders(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = (
        db.query(Order)
        .filter(
            Order.driver_id == driver_id,
            Order.delivery_status.in_(["delivered", "completed"])
        )
        .order_by(Order.created.desc())
        .all()
    )
    if not orders:
        raise HTTPException(status_code=404, detail="No delivered or completed orders found for this driver")
    return orders