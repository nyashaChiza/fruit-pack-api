from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import Cart, Product
from core.auth import get_current_user
from core.config import settings  # contains STRIPE_SECRET_KEY
import stripe

router = APIRouter(prefix="/checkout", tags=["Checkout"])
 
current_user = get_current_user()
stripe.api_key = settings.STRIPE_SECRET_KEY  # Your secret Stripe key

@router.post("/")
def create_checkout_session(db: Session = Depends(get_db)):
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0
    for item in cart_items:
        total_amount += item.price * item.quantity

    amount_cents = int(total_amount * 100)  # Stripe expects amount in cents

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            metadata={"user_id": current_user.id},
        )

        return {
            "client_secret": intent.client_secret,
            "amount": total_amount,
            "currency": "usd"
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")
