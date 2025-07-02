from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
from sqlalchemy.orm import Session
from db.models.product import Product
from db.session import get_db
from schemas.product import ProductCreate, ProductUpdate, ProductRead
from typing import List, Optional
from core.auth import get_current_user
from db.models.user import User  # Assuming you have a User model

router = APIRouter()
IMAGE_DIR = "static/images"


@router.post("/", response_model=ProductRead)
async def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    supplier_id: int = Form(...),
    category_id: Optional[int] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    image_filename = None
    if image:
        os.makedirs(IMAGE_DIR, exist_ok=True)
        image_filename = f"{name}_{image.filename}"
        image_path = os.path.join(IMAGE_DIR, image_filename)
        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    product_data = {
        "name": name,
        "description": description,
        "supplier_id": supplier_id,
        "category_id": category_id,
        "price": price,
        "stock": stock,
        "image": image_filename
    }
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[ProductRead])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    products = db.query(Product).offset(skip).limit(limit).all()
    # Attach category name to each product if relationship exists
    result = []
    for product in products:
        product_data = ProductRead.from_orm(product).dict()
        product_data["category_name"] = product.category.name if product.category else None
        result.append(product_data)
    return result

@router.get("/{product_id}", response_model=ProductRead)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_data = ProductRead.from_orm(product).dict()
    product_data["category_name"] = product.category.name if product.category else None
    return product_data

@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", response_model=dict)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": "Product deleted"}


@router.get("/images/{image_filename}")
def get_image(image_filename: str):
    image_path = os.path.join(IMAGE_DIR, image_filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)