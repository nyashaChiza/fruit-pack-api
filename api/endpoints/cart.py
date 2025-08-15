from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import OrderItem, Order, DriverClaim, Driver
from db.models import notify_user
from loguru import logger
from core.auth import get_current_user
from schemas import CheckoutRequest
from core.config import settings
from helpers import (
    create_order,
    create_order_items,
    create_driver_claims,
    initialize_paystack_transaction,
    verify_paystack_transaction
)
import json
import requests

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/")
async def create_checkout_session(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    try:
        total_amount = sum(item.price * item.quantity for item in payload.items)
        amount_cents = int(total_amount * 100)

        # 1. Create Order
        order = create_order(db, Order, current_user, payload, total_amount)

        # 2. Create Order Items
        create_order_items(db, OrderItem, order.id, payload.items)

        # 3. Send user notification
        notify_user(
            db,
            current_user.id,
            f"Order #{order.id} is created and is being processed",
            'Order Created',
            'Order',
            order.id
        )

        # 4. Notify Drivers
        await create_driver_claims(db, Driver, DriverClaim, order)

        # 5. Handle Payment
        if payload.payment_method == "cash":
            response = {
                "order_id": order.id,
                "amount": total_amount,
                "payment_url": None
            }
        else:
            init = initialize_paystack_transaction(payload, current_user.id, order.id, amount_cents)
            logger.critical(init)
            response = {
                'order_id': order.id,
                'payment_url': init.get('authorization_url'),
                'access_code': init.get('access_code'),
                'reference': init.get('reference')
            }

        db.commit()
        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paystack")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        event = json.loads(payload)

        if event.get("event") == "charge.success":
            reference = event["data"]["reference"]
            verification = verify_paystack_transaction(reference)

            if verification.get("status") and verification["data"]["status"] == "success":
                metadata = verification["data"].get("metadata", {})
                order_id = metadata.get("order_id")

                if order_id:
                    order = db.query(Order).filter(Order.id == int(order_id)).first()
                    if order:
                        order.payment_status = "paid"
                        db.commit()
        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")