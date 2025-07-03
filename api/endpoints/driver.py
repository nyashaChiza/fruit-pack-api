from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.models.driver import Driver
from core.auth import get_current_user
from db.models.user import User
from schemas.driver import DriverCreate, DriverLocationUpdate, DriverRead, DriverUpdate 
from db.session import get_db
from pydantic import BaseModel

router = APIRouter(tags=["drivers"])

class DriverStatusUpdate(BaseModel):
    status: str

@router.post("/", response_model=DriverRead)
def create_driver(driver_create: DriverCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    db_driver = Driver(**driver_create.dict())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.put("/{driver_id}", response_model=DriverRead)
def update_driver(driver_id: int, driver: DriverUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    for key, value in driver.dict(exclude_unset=True).items():
        setattr(db_driver, key, value)
    
    db.commit()
    db.refresh(db_driver)
    return db_driver

@router.get("/", response_model=list[DriverRead])
def list_drivers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    drivers = db.query(Driver).all()
    return drivers

@router.patch("/{driver_id}/status", response_model=DriverRead)
def set_driver_status(
    driver_id: int,
    status_update: DriverStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    db_driver.status = status_update.status
    
    db.commit()
    db.refresh(db_driver)
    return db_driver

@router.post("/driver/{driver_id}/location")
def update_driver_location(
    location: DriverLocationUpdate,
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: Driver = Depends(get_current_user)
):
    
    current_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    current_driver.latitude = location.latitude
    current_driver.longitude = location.longitude
    db.commit()
    db.refresh(current_driver)
    return {"detail": "Location updated"}