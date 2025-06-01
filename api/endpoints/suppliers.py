from fastapi import APIRouter, Depends, HTTPException
from schemas.supplier import SupplierCreate, SupplierUpdate, Supplier
from db.models.supplier import Supplier as SupplierModel
from db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=Supplier)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = SupplierModel(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.get("/{supplier_id}", response_model=Supplier)
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.put("/{supplier_id}", response_model=Supplier)
def update_supplier(supplier_id: int, supplier: SupplierUpdate, db: Session = Depends(get_db)):
    db_supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in supplier.dict(exclude_unset=True).items():
        setattr(db_supplier, key, value)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.delete("/{supplier_id}", response_model=dict)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    db_supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(db_supplier)
    db.commit()
    return {"message": "Supplier deleted successfully"}