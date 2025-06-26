# routes/checkout.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.session import get_db
from core.auth import get_current_user
from core.config import settings
from schemas import CheckoutRequest  # adjust import path if needed
import stripe

router = APIRouter(prefix="/checkout", tags=["Checkout"])

stripe.api_key = settings.STRIPE_SECRET_KEY

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

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            metadata={
                "user_id": current_user.id,
                "cart_items": str([
                    {"id": item.id, "qty": item.quantity} for item in payload.items
                ])
            }
        )

        return {
            "client_secret": intent.client_secret,
            "amount": total_amount,
            "currency": "usd"
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")


router = APIRouter(prefix="/webhooks", tags=["Stripe Webhook"])

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Set this securely

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 🔥 Handle specific event types
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        user_id = intent['metadata']['user_id']
        amount = intent['amount_received']
        # TODO: Mark order as paid, clear cart, etc.

    elif event['type'] == 'payment_intent.payment_failed':
        # Log failure
        pass

    return {"status": "success"}