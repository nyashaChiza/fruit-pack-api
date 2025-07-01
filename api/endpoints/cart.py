from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import Order, OrderItem
from core.auth import get_current_user
from schemas import CheckoutRequest
from core.config import settings
import stripe

router = APIRouter(prefix="/checkout", tags=["Checkout"])

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Set this securely

@router.post("/")
def create_checkout_session(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = sum(item.price * item.quantity for item in payload.items)
    amount_cents = int(total_amount * 100)

    # Step 1: Create Order
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        #id payment method is credit, set payment_status to 'credit
        payment_status="credit" if payload.payment_method == 'credit' else "unpaid",  # Default to unpaid, will be updated after payment
    )
    db.add(order)
    db.flush()  # get order.id

    # Step 2: Create OrderItems
    for item in payload.items:
        order_item = OrderItem(
            order_id=order.id,
            name=item.name,  # Capture product name at time of order
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(order_item)

    db.commit()

    # Step 3: Create Stripe PaymentIntent with metadata
    try:
        if payload.payment_method != 'credit':
           intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="zar",  # corrected to match your return value
                metadata={
                    "user_id": str(current_user.id),
                    "order_id": str(order.id),
                    "full_name": payload.full_name,
                    "address": payload.address,
                    "phone": payload.phone,
                    "payment_method": payload.payment_method,
                    },
                )

           return {
                "client_secret": intent.client_secret,
                "amount": total_amount,
                "currency": "zar",
                "order_id": order.id,
            }
        else:
            # If payment method is credit, just return order details
            return {
                "order_id": order.id,
                "total_amount": total_amount,
                "currency": "zar",
                "payment_status": order.payment_status,
            }
    except stripe.error.StripeError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")



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
