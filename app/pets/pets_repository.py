from sqlalchemy.orm import Session
from app.pets.pets_model import PetModel
from app.pets.pets_schemas import PetCreate, PetUpdate

class PetsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(PetModel).all()

    def get_by_id(self, pet_id: int):
        return self.db.query(PetModel).filter(PetModel.id == pet_id).first()

    def create(self, pet_data: PetCreate):
        new_pet = PetModel(**pet_data.model_dump())
        self.db.add(new_pet)
        self.db.commit()
        self.db.refresh(new_pet)
        return new_pet

    def update(self, pet_id: int, pet_data: PetUpdate):
        db_pet = self.get_by_id(pet_id)
        if not db_pet:
            return None
        
        
        update_data = pet_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_pet, key, value)
            
        self.db.commit()
        self.db.refresh(db_pet)
        return db_pet

    def delete(self, pet_id: int):
        db_pet = self.get_by_id(pet_id)
        if db_pet:
            self.db.delete(db_pet)
            self.db.commit()
            return True
        return False