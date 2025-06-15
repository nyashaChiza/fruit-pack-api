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
import shutil

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
    assets_dir = "assets/images"
    static_dir = "static/images"
    os.makedirs(static_dir, exist_ok=True)
    image_files = [f for f in os.listdir(assets_dir) if os.path.isfile(os.path.join(assets_dir, f))]

    def assign_image(product_name):
        if not image_files:
            return None
        chosen = random.choice(image_files)
        ext = os.path.splitext(chosen)[1]
        safe_name = product_name.replace(" ", "_")
        new_filename = f"{safe_name}_{chosen}"
        src_path = os.path.join(assets_dir, chosen)
        dst_path = os.path.join(static_dir, new_filename)
        # Copy only if not already present
        if not os.path.exists(dst_path):
            shutil.copyfile(src_path, dst_path)
        return f"{new_filename}"

    # Seed products
    products = [
        Product(
            name="Orange",
            description="Fresh oranges",
            price=1.5,
            stock=100,
            supplier_id=supplier_objs[0].id,
            category_id=category_objs[0].id,
            image=assign_image("Orange")
        ),
        Product(
            name="Strawberry",
            description="Sweet strawberries",
            price=2.0,
            stock=50,
            supplier_id=supplier_objs[1].id,
            category_id=category_objs[1].id,
            image=assign_image("Strawberry")
        ),
        Product(
            name="Mango",
            description="Juicy tropical mangoes",
            price=2.5,
            stock=80,
            supplier_id=supplier_objs[2].id,
            category_id=category_objs[2].id,
            image=assign_image("Mango")
        ),
        Product(
            name="Peach",
            description="Ripe stone fruit peaches",
            price=2.2,
            stock=60,
            supplier_id=supplier_objs[0].id,
            category_id=category_objs[3].id,
            image=assign_image("Peach")
        ),
        Product(
            name="Watermelon",
            description="Refreshing watermelons",
            price=3.0,
            stock=40,
            supplier_id=supplier_objs[1].id,
            category_id=category_objs[4].id,
            image=assign_image("Watermelon")
        ),
        Product(
            name="Green Apple",
            description="Crisp green apples",
            price=1.8,
            stock=90,
            supplier_id=supplier_objs[2].id,
            category_id=category_objs[5].id,
            image=assign_image("Green Apple")
        ),
        Product(
            name="Kiwi",
            description="Tangy exotic kiwis",
            price=2.7,
            stock=70,
            supplier_id=supplier_objs[0].id,
            category_id=category_objs[6].id,
            image=assign_image("Kiwi")
        ),
    ]
    db.add_all(products)
    db.commit()

    return {"detail": "Seed data inserted successfully"}