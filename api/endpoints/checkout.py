from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import stripe
from schemas.cart import CheckoutRequest
from decouple import config


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

stripe.api_key = config("STRIPE_SECRET_KEY")

@router.post("/checkout")
async def create_checkout(request: CheckoutRequest, token: str = Depends(oauth2_scheme)):
    try:
        # Calculate total amount in cents
        total_amount = sum(item.price * item.quantity for item in request.items)
        total_cents = int(total_amount * 100)

        # Create a PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=total_cents,
            currency="usd",
            metadata={"integration_check": "accept_a_payment"},
        )

        return {
            "clientSecret": intent.client_secret,
            "amount": total_amount,
            "currency": "usd",
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
