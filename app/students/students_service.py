from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.pets.pets_model import PetModel
from app.pets.pets_repository import PetsRepository
from app.shared.database import transaction
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.shared.types import FieldErrors
from app.students.students_model import StudentModel
from app.students.students_repository import StudentsRepository
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)


class StudentsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = StudentsRepository(db)
        self.pets_repository = PetsRepository(db)

    def find_all(self) -> StudentList:
        students = [Student.model_validate(s) for s in self.repository.find_all()]

        return StudentList(total=len(students), items=students)

    def find_by_id(self, student_id: str) -> Student:
        return Student.model_validate(self._get_or_404(student_id))

    def create(self, data: CreateStudentDto) -> Student:
        self.assert_no_conflicts(data)

        now = utc_now()
        student = StudentModel(
            id=str(uuid4()),
            name=data.name,
            username=data.username,
            email=data.email,
            age=data.age,
            createdAt=now,
            updatedAt=now,
        )

        # TRANSACCIÓN: estudiante + mascotas se guardan juntos o no se guarda nada.
        # Si una mascota falla (nombre repetido, error de BD, etc.) se hace rollback
        # y el estudiante tampoco queda creado.
        try:
            with transaction(self.db):
                self.repository.add(student)

                for pet_data in data.pets:
                    if self.pets_repository.find_by_student_and_name(
                        student.id, pet_data.name
                    ):
                        raise conflict(
                            {"name": {"message": "Ya tienes una mascota con ese nombre"}}
                        )

                    pet_now = utc_now()
                    self.pets_repository.add(
                        PetModel(
                            id=str(uuid4()),
                            studentId=student.id,
                            name=pet_data.name,
                            species=pet_data.species,
                            age=pet_data.age,
                            createdAt=pet_now,
                            updatedAt=pet_now,
                        )
                    )
        except IntegrityError as exc:
            raise self._integrity_conflict() from exc

        return Student.model_validate(student)

    def update(self, student_id: str, data: UpdateStudentDto) -> Student:
        student = self._get_or_404(student_id)
        self.assert_no_conflicts(data, except_id=student_id)

        try:
            with transaction(self.db):
                for field, value in data.model_dump(exclude_none=True).items():
                    setattr(student, field, value)

                student.updatedAt = utc_now()
                self.db.flush()
        except IntegrityError as exc:
            raise self._integrity_conflict() from exc

        return Student.model_validate(student)

    def delete(self, student_id: str) -> Student:
        student = self._get_or_404(student_id)
        deleted = Student.model_validate(student)

        # Una sola operación: borrar al estudiante elimina sus mascotas (CASCADE).
        with transaction(self.db):
            self.repository.delete(student)

        return deleted

    def _get_or_404(self, student_id: str) -> StudentModel:
        student = self.repository.find_by_id(student_id)

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )

        return student

    def assert_no_conflicts(
        self,
        data: CreateStudentDto | UpdateStudentDto,
        except_id: str | None = None,
    ) -> None:
        errors: FieldErrors = {}

        if data.email:
            existing = self.repository.find_by_email(data.email)
            if existing and existing.id != except_id:
                errors["email"] = {"message": "El correo electrónico ya está en uso"}

        if data.username:
            existing = self.repository.find_by_username(data.username)
            if existing and existing.id != except_id:
                errors["username"] = {"message": "El nombre de usuario ya está en uso"}

        if errors:
            raise conflict(errors)

    @staticmethod
    def _integrity_conflict() -> HTTPException:
        # Respaldo ante condiciones de carrera: la BD tiene constraints UNIQUE.
        return conflict(
            {"email": {"message": "El correo o el nombre de usuario ya está en uso"}}
        )
