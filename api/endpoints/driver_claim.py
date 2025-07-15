from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.models.driver_claims import DriverClaim
from db.models.driver import Driver
from db.models.order import Order
from db.models import notify_user
from db.session import get_db
from schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from typing import List
from core.auth import get_current_user
from db.models.user import User
from schemas.driver_claims import  DriverClaimOut, DriverClaimList

router = APIRouter()


@router.post("/claim/order/{order_id}/driver/{driver_id}")
def claim_order(order_id: int, driver_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    current_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not current_driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    existing_claim = db.query(DriverClaim).filter_by(order_id=order_id, driver_id=current_driver.id).first()
    if existing_claim:
        raise HTTPException(status_code=400, detail="You already claimed this order.")

    claim = DriverClaim(order_id=order_id, driver_id=current_driver.id)
    db.add(claim)
    db.commit()
    db.refresh(claim)
    notify_user(db, claim.driver_id, f"Claim #{claim.id} for Order #{claim.order_id} has been Created",'Claim Creation','Claim', claim.id)

    
    return {"message": "Claim submitted for approval."}


@router.post("/admin/claims/{claim_id}/approve")
def approve_driver_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    claim = db.query(DriverClaim).filter(DriverClaim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status != "pending":
        raise HTTPException(status_code=400, detail="Claim already processed")

    # Fetch related models
    driver = db.query(Driver).filter(Driver.id == claim.driver_id).first()
    order = db.query(Order).filter(Order.id == claim.order_id).first()

    if not driver or not order:
        raise HTTPException(status_code=400, detail="Driver or Order not found")

    # Update statuses
    claim.status = "approved"
    driver.status = "busy"  # or "active", depending on your logic
    order.delivery_status = "shipped"
    order.driver_id = driver.id  # optional if not already assigned

    db.commit()
    notify_user(db, claim.driver_id, f"Claim #{claim.id} for Order #{claim.order_id} has been Approved",'Claim Approved','Claim', claim.id)

    return {"message": "Claim approved, driver marked busy, and order marked as shipped"}


@router.post("/admin/claims/{claim_id}/reject")
def reject_claim(claim_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    claim = db.query(DriverClaim).get(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status != "pending":
        raise HTTPException(status_code=400, detail="Claim already resolved")

    claim.status = "rejected"
    db.commit()
    notify_user(db, claim.driver_id, f"Claim #{claim.id} for Order #{claim.order_id} has been Rejected",'Claim Rejected','Claim', claim.id)
    return {"message": "Claim rejected."}


@router.get("/driver/{driver_id}/claims", response_model=List[DriverClaimOut])
def get_driver_claims(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    current_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not current_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    claims = db.query(DriverClaim).filter_by(driver_id=current_driver.id).order_by(DriverClaim.created.desc()).all()
    return claims

@router.get("/admin/claims", response_model=List[DriverClaimList])
def list_all_claims(db: Session = Depends(get_db)):
    claims = db.query(DriverClaim).order_by(DriverClaim.created.desc()).all()
    return claims

