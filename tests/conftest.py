import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.shared.database import engine


@pytest.fixture(autouse=True)
def clean_db():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE pets, students RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def student_payload(**overrides):
    data = {
        "name": "Juan Pérez",
        "username": "jperez",
        "email": "jperez@alu.uct.cl",
        "age": 22,
    }
    data.update(overrides)
    return data
