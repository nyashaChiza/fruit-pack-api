from helpers import get_nearby_drivers
from helpers.notifications import send_push_notification
import stripe
import requests
from core.config import settings

def create_order(db, Order,user, payload, total_amount):
    order = Order(
        user_id=user.id,
        total_amount=total_amount,
        destination_address=payload.address,
        destination_latitude=payload.latitude,
        destination_longitude=payload.longitude,
        customer_phone=payload.phone,
        customer_name=payload.email,
        payment_method=payload.payment_method,
        payment_status="credit" if payload.payment_method == 'credit' else "unpaid",
    )
    db.add(order)
    db.flush()
    return order


def create_order_items(db, OrderItem, order_id, items):
    for item in items:
        order_item = OrderItem(
            order_id=order_id,
            name=item.name,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(order_item)


async def create_driver_claims(db, Driver, DriverClaim, order):
    drivers = db.query(Driver).all()
    nearby_drivers = get_nearby_drivers(order, drivers)

    for driver in nearby_drivers:
        claim = DriverClaim(
            driver_id=driver.id,
            order_id=order.id,
            claim_type="system",
            status="pending"
        )
        db.add(claim)

        if driver.user.push_token:
            await send_push_notification(
                driver.user.push_token,
                "Order Claim",
                "A new order has been created"
            )

    db.commit()
        


def create_payment_intent(payload, user_id, order_id, amount_cents):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="zar",
        metadata={
            "user_id": str(user_id),
            "order_id": str(order_id),
            "full_name": payload.email,
            "address": payload.address,
            "phone": payload.phone,
            "payment_method": payload.payment_method,
        },
    )


def initialize_paystack_transaction(payload, user_id, order_id, amount_cents):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": payload.email,
        "amount": amount_cents,  # Paystack expects amount in cents
        "currency": "ZAR",
        "reference": f"ORDER_{order_id}_{user_id}",
        "metadata": {
            "user_id": str(user_id),
            "order_id": str(order_id),
            "email": payload.email,
            "address": payload.address,
            "phone": payload.phone,
            "payment_method": payload.payment_method,
        },
  
    }

    response = requests.post(settings.PAYSTACK_ENDPOINT, json=data, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Paystack init failed: {response.json().get('message')}")

    return response.json()["data"]  # includes payment_url and access_code

def verify_paystack_transaction(reference: str):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    url = f"{settings.PAYSTACK_VERIFY}{reference}"
    response = requests.get(url, headers=headers)
    return response.json()