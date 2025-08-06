import datetime
from fastapi import APIRouter, HTTPException, Depends
from db.models.order import Order
from schemas.user import UserCreate, UserRead, PushTokenPayload
from db.models.user import User
from db.session import get_db
from sqlalchemy.orm import Session
from core.security import get_password_hash
from core.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=UserRead)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if the email is already registered
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password before saving
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,  # Use the role from the schema
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}

@router.get("/", response_model=list[UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}/credit-eligibility")
def check_credit_eligibility(user_id: int, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    # Get all orders by user
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created.desc()).all()

    if not orders:
        return {"eligible": False, "reason": "No orders found."}

    # Find latest credit order
    last_credit_order = next((o for o in orders if o.payment_status == 'credit'), None)
    last_credit_time = last_credit_order.created if last_credit_order else datetime.datetime.min


    # Count paid orders after last credit order
    paid_orders = [
        o for o in orders
        if o.payment_status == 'paid' and o.created > last_credit_time
    ]

    # Sum unpaid credit order balances
    credit_orders = [
        o for o in orders if o.payment_status == 'credit' and o.delivery_status != 'completed'
    ]
    total_credit_balance = sum(o.total_amount for o in credit_orders)

    eligible = len(paid_orders) >= 5 and total_credit_balance < 300

    return {
        "eligible": eligible,
        "reason": (
            "Eligible for credit." if eligible else
            f"{len(paid_orders)} paid orders after last credit, credit balance is R{total_credit_balance:.2f}"
        ),
        "remaining_credit_limit": max(0, 300 - total_credit_balance)
    }

@router.post("/users/push-token")
def store_push_token(payload: PushTokenPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.push_token = payload.pushToken
    db.commit()
    print(f"Received push token: {payload.pushToken}")
    return {"message": "Push token saved"}