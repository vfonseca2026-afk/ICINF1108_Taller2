from sqlalchemy import select
from sqlalchemy.orm import Session

from app.students.students_model import StudentModel


class StudentsRepository:
    """Acceso a datos. No hace commit: la transacción la controla el servicio."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self) -> list[StudentModel]:
        stmt = select(StudentModel).order_by(StudentModel.createdAt.desc())
        return list(self.db.scalars(stmt))

    def find_by_id(self, student_id: str) -> StudentModel | None:
        return self.db.get(StudentModel, student_id)

    def find_by_email(self, email: str) -> StudentModel | None:
        stmt = select(StudentModel).where(StudentModel.email == email)
        return self.db.scalars(stmt).first()

    def find_by_username(self, username: str) -> StudentModel | None:
        stmt = select(StudentModel).where(StudentModel.username == username)
        return self.db.scalars(stmt).first()

    def add(self, student: StudentModel) -> StudentModel:
        self.db.add(student)
        self.db.flush()
        return student

    def delete(self, student: StudentModel) -> None:
        self.db.delete(student)
        self.db.flush()
