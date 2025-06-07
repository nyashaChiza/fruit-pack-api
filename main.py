from fastapi import FastAPI
from api.endpoints import orders, suppliers, users, product, auth
from db.base import Base
from db.session import engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:8081",  # Expo/React Native web
    "http://localhost:3000",  # If you're also using React web
    "https://studio.expo.dev",  # Expo preview environment
    "https://fruit-pack-api.onrender.com",  # If needed (not necessary for your own domain)
    "*"  # Use only for testing — restrict in production!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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