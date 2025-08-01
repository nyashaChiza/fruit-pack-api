from fastapi import APIRouter, HTTPException, Depends
from db.models.adverts import Advert
from core.auth import get_current_user
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.user import User
from schemas.advert import  AdvertCreate, AdvertRead, AdvertUpdate


router = APIRouter()

@router.post("/create", response_model=AdvertCreate)
def create_advert(
    advert: AdvertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_advert = Advert(**advert.dict())
    db.add(db_advert)
    db.commit()
    db.refresh(db_advert)
    return db_advert


@router.get("/", response_model=list[AdvertRead])
def read_adverts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Advert).offset(skip).limit(limit).all()

@router.get("/{advert_id}", response_model=AdvertRead)
def read_advert(
    advert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    advert = db.query(Advert).filter(Advert.id == advert_id).first()
    if not advert:
        raise HTTPException(status_code=404, detail="Advert not found")
    return advert

@router.put("/{advert_id}", response_model=AdvertRead)
def update_advert(
    advert_id: int,
    advert: AdvertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_advert = db.query(Advert).filter(Advert.id == advert_id).first()
    if not db_advert:
        raise HTTPException(status_code=404, detail="Advert not found")
    
    for key, value in advert.dict(exclude_unset=True).items():
        setattr(db_advert, key, value)
    
    db.commit()
    db.refresh(db_advert)
    return db_advert