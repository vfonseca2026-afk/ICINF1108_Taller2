from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.shared.database import get_db
from app.pets.pets_repository import PetsRepository
from app.pets.pets_schemas import PetCreate, PetUpdate, PetResponse

router = APIRouter(prefix="/pets", tags=["Pets"])

@router.get("/", response_model=list[PetResponse])
def get_pets(db: Session = Depends(get_db)):
    repo = PetsRepository(db)
    return repo.get_all()

@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(pet: PetCreate, db: Session = Depends(get_db)):
    repo = PetsRepository(db)
    return repo.create(pet)

@router.get("/{pet_id}", response_model=PetResponse)
def get_pet_by_id(pet_id: int, db: Session = Depends(get_db)):
    repo = PetsRepository(db)
    pet = repo.get_by_id(pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return pet

@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    repo = PetsRepository(db)
    if not repo.delete(pet_id):
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return None