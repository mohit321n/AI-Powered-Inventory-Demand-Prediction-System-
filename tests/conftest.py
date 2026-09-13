import sys
import os
import pytest
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database.database import Base, get_db
from app.main import app
from app.api.auth import get_password_hash, create_access_token
from app.models import User, Category, Supplier, Product, Sale, InventoryTransaction

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user):
    token = create_access_token(data={"sub": test_user.username})
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_category(db_session):
    category = Category(name="Electronics", description="Electronic devices")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture(scope="function")
def test_supplier(db_session):
    supplier = Supplier(name="Acme Corp", lead_time_days=7)
    db_session.add(supplier)
    db_session.commit()
    db_session.refresh(supplier)
    return supplier


@pytest.fixture(scope="function")
def test_product(db_session, test_category, test_supplier):
    product = Product(
        name="Test Widget",
        sku="TST-001",
        category_id=test_category.id,
        supplier_id=test_supplier.id,
        price=29.99,
        cost_price=15.00,
        current_stock=100,
        minimum_stock=10,
        safety_stock=5,
        lead_time_days=7,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture(scope="function")
def test_product_low_stock(db_session, test_category, test_supplier):
    product = Product(
        name="Low Stock Widget",
        sku="TST-002",
        category_id=test_category.id,
        supplier_id=test_supplier.id,
        price=19.99,
        cost_price=10.00,
        current_stock=3,
        minimum_stock=10,
        safety_stock=5,
        lead_time_days=7,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product
