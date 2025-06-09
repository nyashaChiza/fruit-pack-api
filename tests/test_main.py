from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Fruit-Pack Platform API"}

def test_users_router():
    response = client.get("/users/")
    assert response.status_code in (200, 401, 403, 404)  # Depending on auth

def test_auth_router():
    response = client.post("/auth/login/", json={"username": "test", "password": "test"})
    assert response.status_code in (200, 401, 422)

def test_suppliers_router():
    response = client.get("/suppliers/")
    assert response.status_code in (200, 401, 403, 404)

def test_categories_router():
    response = client.get("/categories/")
    assert response.status_code in (200, 401, 403, 404)

def test_products_router():
    response = client.get("/products/")
    assert response.status_code in (200, 401, 403, 404)

def test_orders_router():
    response = client.get("/orders/")
    assert response.status_code in (200, 401, 403, 404)
