from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.shared.database import get_db
from app.students.students_repository import StudentsRepository
from app.students.students_schemas import StudentResponse, StudentCreate, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/", response_model=List[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    
    repo = StudentsRepository(db)
    return repo.get_all()

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: str, db: Session = Depends(get_db)):
    
    repo = StudentsRepository(db)
    student = repo.get_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {student_id} no encontrado"
        )
    return student

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
   
    repo = StudentsRepository(db)
    
    existing = repo.get_by_email(student_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
        
    return repo.create(student_in)

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: str, student_in: StudentUpdate, db: Session = Depends(get_db)):
    
    repo = StudentsRepository(db)
    updated_student = repo.update(student_id, student_in)
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {student_id} no encontrado para actualizar"
        )
    return updated_student

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: str, db: Session = Depends(get_db)):

    repo = StudentsRepository(db)
    success = repo.delete(student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {student_id} no encontrado para eliminar"
        )
    return None