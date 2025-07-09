from typing import List
from fastapi import APIRouter, Depends, HTTPException
from schemas.supplier import SupplierCreate, SupplierUpdate, Supplier, SupplierRead
from db.models.supplier import Supplier as SupplierModel
from db.session import get_db
from sqlalchemy.orm import Session
from core.auth import get_current_user
from db.models.user import User  # Assuming you have a User model

router = APIRouter()

@router.post("/", response_model=Supplier)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_supplier = SupplierModel(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


@router.get("/", response_model=List[SupplierRead])
def read_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(SupplierModel).all()

@router.get("/{supplier_id}", response_model=Supplier)
def read_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.put("/{supplier_id}", response_model=Supplier)
def update_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in supplier.dict(exclude_unset=True).items():
        setattr(db_supplier, key, value)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.delete("/{supplier_id}", response_model=dict)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(db_supplier)
    db.commit()
    return {"message": "Supplier deleted successfully"}