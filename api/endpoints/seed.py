from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.supplier import Supplier
from db.models.category import Category
from db.models.product import Product
from core.auth import get_current_user
from db.models.user import User
import os
import random

router = APIRouter()

@router.post("/seed/")
def seed_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Seed suppliers with correct fields
    supplier1 = Supplier(
        name="FreshFruits Ltd",
        contact_email="info@freshfruits.com",
        phone_number="123-456-7890"
    )
    supplier2 = Supplier(
        name="Tropical Goods",
        contact_email="contact@tropical.com",
        phone_number="234-567-8901"
    )
    supplier3 = Supplier(
        name="Green Valley",
        contact_email="hello@greenvalley.com",
        phone_number="345-678-9012"
    )
    db.add_all([supplier1, supplier2, supplier3])
    db.commit()

    # Seed categories with icons
    categories = [
        Category(name="Citrus", icon="🍊"),
        Category(name="Berries", icon="🍓"),
        Category(name="Tropical", icon="🥭"),
        Category(name="Stone Fruits", icon="🍑"),
        Category(name="Melons", icon="🍉"),
        Category(name="Pomes", icon="🍏"),
        Category(name="Exotic", icon="🥝"),
    ]
    db.add_all(categories)
    db.commit()

    # Get all category and supplier IDs
    category_objs = db.query(Category).all()
    supplier_objs = db.query(Supplier).all()

    # Get images from assets/images
    image_dir = "assets/images"
    image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
    def random_image():
        return os.path.join(image_dir, random.choice(image_files)) if image_files else None

    # Seed products
    products = [
        Product(
            name="Orange",
            description="Fresh oranges",
            price=1.5,
            stock=100,
            supplier_id=supplier_objs[0].id,
            category_id=category_objs[0].id,
            image=random_image()
        ),
        Product(
            name="Strawberry",
            description="Sweet strawberries",
            price=2.0,
            stock=50,
            supplier_id=supplier_objs[1].id,
            category_id=category_objs[1].id,
            image=random_image()
        ),
        Product(
            name="Mango",
            description="Juicy tropical mangoes",
            price=2.5,
            stock=80,
            supplier_id=supplier_objs[2].id,
            category_id=category_objs[2].id,
            image=random_image()
        ),
        Product(
            name="Peach",
            description="Ripe stone fruit peaches",
            price=2.2,
            stock=60,
            supplier_id=supplier_objs[0].id,
            category_id=category_objs[3].id,
            image=random_image()
        ),
        Product(
            name="Watermelon",
            description="Refreshing watermelons",
            price=3.0,
            stock=40,
            supplier_id=supplier_objs[1].id,
            category_id=category_objs[4].id,
            image=random_image()
        ),
        Product(
            name="Green Apple",
            description="Crisp green apples",
            price=1.8,
            stock=90,
            supplier_id=supplier_objs[2].id,
            category_id=category_objs[5].id,
            image=random_image()
        ),
        Product(
            name="Kiwi",
            description="Tangy exotic kiwis",
            price=2.7,
            stock=70,
            supplier_id=supplier_objs[0].id,
            category_id=category_objs[6].id,
            image=random_image()
        ),
    ]
    db.add_all(products)
    db.commit()

    return {"detail": "Seed data inserted successfully"}