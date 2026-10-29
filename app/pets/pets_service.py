from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.pets.pets_model import PetModel
from app.pets.pets_repository import PetsRepository
from app.pets.pets_schemas import CreatePetDto, Pet, PetList, UpdatePetDto
from app.shared.database import transaction
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.students.students_repository import StudentsRepository

NAME_TAKEN = {"name": {"message": "Ya tienes una mascota con ese nombre"}}


class PetsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = PetsRepository(db)
        self.students_repository = StudentsRepository(db)

    def find_all_for_student(self, student_id: str) -> PetList:
        self._assert_student_exists(student_id)

        pets = [
            Pet.model_validate(p)
            for p in self.repository.find_all_by_student(student_id)
        ]

        return PetList(total=len(pets), items=pets)

    def create(self, student_id: str, data: CreatePetDto) -> Pet:
        self._assert_student_exists(student_id)
        self.assert_no_conflicts(student_id, data)

        now = utc_now()
        pet = PetModel(
            id=str(uuid4()),
            studentId=student_id,
            name=data.name,
            species=data.species,
            age=data.age,
            createdAt=now,
            updatedAt=now,
        )

        try:
            with transaction(self.db):
                self.repository.add(pet)
        except IntegrityError as exc:
            raise conflict(NAME_TAKEN) from exc

        return Pet.model_validate(pet)

    def update(self, student_id: str, pet_id: str, data: UpdatePetDto) -> Pet:
        pet = self.find_owned(student_id, pet_id)
        self.assert_no_conflicts(student_id, data, except_id=pet_id)

        try:
            with transaction(self.db):
                for field, value in data.model_dump(exclude_none=True).items():
                    setattr(pet, field, value)

                pet.updatedAt = utc_now()
                self.db.flush()
        except IntegrityError as exc:
            raise conflict(NAME_TAKEN) from exc

        return Pet.model_validate(pet)

    def delete(self, student_id: str, pet_id: str) -> Pet:
        pet = self.find_owned(student_id, pet_id)
        deleted = Pet.model_validate(pet)

        with transaction(self.db):
            self.repository.delete(pet)

        return deleted

    def find_owned(self, student_id: str, pet_id: str) -> PetModel:
        self._assert_student_exists(student_id)

        pet = self.repository.find_by_id(pet_id)

        if pet is None or pet.studentId != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada",
            )

        return pet

    def assert_no_conflicts(
        self,
        student_id: str,
        data: CreatePetDto | UpdatePetDto,
        except_id: str | None = None,
    ) -> None:
        if not data.name:
            return

        existing = self.repository.find_by_student_and_name(student_id, data.name)

        if existing and existing.id != except_id:
            raise conflict(NAME_TAKEN)

    def _assert_student_exists(self, student_id: str) -> None:
        if self.students_repository.find_by_id(student_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )
