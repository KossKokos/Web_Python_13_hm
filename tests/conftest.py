import sys
from pathlib import Path

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.models import Base
from src.database.db import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Users\\kosko\\Documents\\Python\\Python_Web\\Module_13\\Web_Python_13_hm\\web_14_hm_tests.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "koskoks", "email": "example@example.com", "password": "password"}
