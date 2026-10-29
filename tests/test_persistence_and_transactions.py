import pytest
from sqlalchemy import text

from app.pets.pets_repository import PetsRepository
from app.shared.database import SessionLocal, engine
from tests.conftest import student_payload


def count(table: str) -> int:
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()


def test_student_is_persisted_in_database(client):
    res = client.post("/api/students", json=student_payload())
    assert res.status_code == 201
    student_id = res.json()["data"]["id"]

    # Se lee con una sesión completamente nueva: viene de PostgreSQL, no de memoria
    with SessionLocal() as db:
        row = db.execute(
            text("SELECT username FROM students WHERE id = :id"), {"id": student_id}
        ).one()
    assert row.username == "jperez"


def test_crud_students(client):
    created = client.post("/api/students", json=student_payload()).json()["data"]
    sid = created["id"]

    assert client.get("/api/students").json()["data"]["total"] == 1
    assert client.get(f"/api/students/{sid}").json()["data"]["email"] == (
        "jperez@alu.uct.cl"
    )

    upd = client.patch(f"/api/students/{sid}", json={"age": 30})
    assert upd.status_code == 200 and upd.json()["data"]["age"] == 30

    assert client.delete(f"/api/students/{sid}").status_code == 200
    assert client.get(f"/api/students/{sid}").status_code == 404


def test_crud_pets(client):
    sid = client.post("/api/students", json=student_payload()).json()["data"]["id"]
    pets = f"/api/students/{sid}/pets"

    pet = client.post(pets, json={"name": "Firulais", "species": "Perro", "age": 3})
    assert pet.status_code == 201
    pid = pet.json()["data"]["id"]
    assert pet.json()["data"]["studentId"] == sid

    assert client.get(pets).json()["data"]["total"] == 1
    assert client.patch(f"{pets}/{pid}", json={"age": 4}).json()["data"]["age"] == 4
    assert client.delete(f"{pets}/{pid}").status_code == 200
    assert client.get(pets).json()["data"]["total"] == 0


def test_unique_email_and_username_return_409(client):
    client.post("/api/students", json=student_payload())
    res = client.post("/api/students", json=student_payload())
    assert res.status_code == 409
    assert count("students") == 1


def test_duplicate_pet_name_per_student_returns_409(client):
    sid = client.post("/api/students", json=student_payload()).json()["data"]["id"]
    body = {"name": "Rex", "species": "Perro"}
    assert client.post(f"/api/students/{sid}/pets", json=body).status_code == 201
    assert client.post(f"/api/students/{sid}/pets", json=body).status_code == 409


# ---------------------------------------------------------------- TRANSACCIONES


def test_create_student_with_pets_is_atomic_on_success(client):
    res = client.post(
        "/api/students",
        json=student_payload(
            pets=[
                {"name": "Rex", "species": "Perro"},
                {"name": "Misu", "species": "Gato"},
            ]
        ),
    )
    assert res.status_code == 201
    assert count("students") == 1
    assert count("pets") == 2


def test_rollback_when_second_pet_is_duplicated(client):
    """Mascota repetida en el mismo payload => 409 y el estudiante NO queda creado."""
    res = client.post(
        "/api/students",
        json=student_payload(
            pets=[
                {"name": "Rex", "species": "Perro"},
                {"name": "Rex", "species": "Gato"},
            ]
        ),
    )
    assert res.status_code == 409
    assert count("students") == 0
    assert count("pets") == 0


def test_rollback_when_database_fails_midway(client, monkeypatch):
    """Fallo inesperado al guardar la 2ª mascota => rollback total (500, sin datos)."""
    original_add = PetsRepository.add
    calls = {"n": 0}

    def failing_add(self, pet):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("fallo simulado de la base de datos")
        return original_add(self, pet)

    monkeypatch.setattr(PetsRepository, "add", failing_add)

    res = client.post(
        "/api/students",
        json=student_payload(
            pets=[
                {"name": "Rex", "species": "Perro"},
                {"name": "Misu", "species": "Gato"},
            ]
        ),
    )
    assert res.status_code == 500
    assert count("students") == 0  # el estudiante se revirtió
    assert count("pets") == 0  # la 1ª mascota también


def test_delete_student_cascades_to_pets_in_one_transaction(client):
    sid = client.post(
        "/api/students",
        json=student_payload(pets=[{"name": "Rex", "species": "Perro"}]),
    ).json()["data"]["id"]
    assert count("pets") == 1

    assert client.delete(f"/api/students/{sid}").status_code == 200
    assert count("students") == 0
    assert count("pets") == 0


@pytest.mark.parametrize("path", ["/api/students/nope", "/api/students/nope/pets"])
def test_unknown_student_is_404(client, path):
    assert client.get(path).status_code == 404
