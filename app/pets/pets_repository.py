from sqlalchemy import select
from sqlalchemy.orm import Session

from app.pets.pets_model import PetModel


class PetsRepository:
    """Acceso a datos. No hace commit: la transacción la controla el servicio."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all_by_student(self, student_id: str) -> list[PetModel]:
        stmt = (
            select(PetModel)
            .where(PetModel.studentId == student_id)
            .order_by(PetModel.createdAt.desc())
        )
        return list(self.db.scalars(stmt))

    def find_by_id(self, pet_id: str) -> PetModel | None:
        return self.db.get(PetModel, pet_id)

    def find_by_student_and_name(self, student_id: str, name: str) -> PetModel | None:
        stmt = select(PetModel).where(
            PetModel.studentId == student_id, PetModel.name == name
        )
        return self.db.scalars(stmt).first()

    def add(self, pet: PetModel) -> PetModel:
        self.db.add(pet)
        self.db.flush()
        return pet

    def delete(self, pet: PetModel) -> None:
        self.db.delete(pet)
        self.db.flush()
