from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from db.models import Cart, Product
from schemas import CartCreate, CartResponse, CartUpdate
from core.auth import get_current_user # your auth dependency

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=List[CartResponse])
def get_cart_items(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    return items

@router.post("/", response_model=CartResponse)
def add_cart_item(item_in: CartCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(Cart).filter(
        Cart.user_id == current_user.id, Cart.product_id == item_in.product_id
    ).first()

    # if cart_item:
    #     cart_item.quantity += item_in.quantity
    #     # Optionally: Do NOT update price here to preserve original cart state
    # else:
    cart_item = Cart(
            user_id=current_user.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            price=product.price  # Capture snapshot
        )
        
    db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.put("/{item_id}", response_model=CartResponse)
def update_cart_item(item_id: int, item_in: CartUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cart_item = db.query(Cart).filter(
        Cart.id == item_id,
        Cart.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # cart_item.quantity = item_in.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/{item_id}", status_code=204)
def delete_cart_item(item_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cart_item = db.query(Cart).filter(
        Cart.id == item_id,
        Cart.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
