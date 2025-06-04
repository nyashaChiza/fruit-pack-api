from fastapi import FastAPI
from api.endpoints import orders, suppliers, users, product, auth
from db.base import Base
from db.session import engine

app = FastAPI()

app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(product.router, prefix="/products", tags=["products"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fruit Ordering Platform API"}

# Run this once in your main.py or a setup script
Base.metadata.create_all(bind=engine)