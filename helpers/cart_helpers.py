from helpers import get_nearby_drivers
from helpers.notifications import send_push_notification
import stripe
from core.config import settings

def create_order(db, Order,user, payload, total_amount):
    order = Order(
        user_id=user.id,
        total_amount=total_amount,
        destination_address=payload.address,
        destination_latitude=payload.latitude,
        destination_longitude=payload.longitude,
        customer_phone=payload.phone,
        customer_name=payload.full_name,
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
            "full_name": payload.full_name,
            "address": payload.address,
            "phone": payload.phone,
            "payment_method": payload.payment_method,
        },
    )
