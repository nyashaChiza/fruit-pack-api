from fastapi import FastAPI
from api.endpoints import orders, suppliers, users

app = FastAPI()

app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fruit Ordering Platform API"}