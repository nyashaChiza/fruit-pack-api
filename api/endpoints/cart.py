from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import OrderItem, Order, DriverClaim, Driver
from db.models import Order, notify_user
from core.auth import get_current_user
from schemas import CheckoutRequest
from core.config import settings
from helpers import create_order, create_order_items, create_driver_claims, create_payment_intent
import stripe

router = APIRouter(prefix="/checkout", tags=["Checkout"])


endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Set this securely

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

        # 4. Notify Drivers (await the async function)
        await create_driver_claims(db, Driver, DriverClaim, order)

        # 5. Handle Payment
        if payload.payment_method == "cash":
            response = {
                "order_id": order.id,
                "amount": total_amount,
                "client_secret": None
            }
        else:
            intent = create_payment_intent(payload, current_user.id, order.id, amount_cents)
            response = {
                "client_secret": intent.client_secret,
                "amount": total_amount,
                "order_id": order.id
            }

        db.commit()
        return response

    except stripe.error.StripeError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook")

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        order_id = intent['metadata'].get('order_id')

        if order_id:
            order = db.query(Order).filter(Order.id == int(order_id)).first()
            if order:
                order.payment_status = "paid"
                db.commit()

    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        order_id = intent['metadata'].get('order_id')

        if order_id:
            order = db.query(Order).filter(Order.id == int(order_id)).first()
            if order:
                order.payment_status = "failed"
                db.commit()

    return {"status": "success"}
