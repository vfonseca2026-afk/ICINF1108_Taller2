from sqlalchemy.orm import Session
from app.students.students_model import StudentModel
from app.students.students_schemas import StudentCreate, StudentUpdate

class StudentsRepository:
    def __init__(self, db: Session):
        
        self.db = db

    def get_all(self):
        
        return self.db.query(StudentModel).all()

    def get_by_id(self, student_id: str):
        
        return self.db.query(StudentModel).filter(StudentModel.id == student_id).first()

    def get_by_email(self, email: str):
       
        return self.db.query(StudentModel).filter(StudentModel.email == email).first()

    def create(self, student_data: StudentCreate):

        db_student = StudentModel(**student_data.model_dump())
        self.db.add(db_student)
        self.db.commit()
        self.db.refresh(db_student)
        return db_student

    def update(self, student_id: str, student_data: StudentUpdate):
       
        student = self.get_by_id(student_id)
        if not student:
            return None
        
        
        update_data = student_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(student, key, value)
            
        self.db.commit()
        self.db.refresh(student)
        return student

    def delete(self, student_id: str):
       
        student = self.get_by_id(student_id)
        if student:
            self.db.delete(student)
            self.db.commit()
            return True
        return False