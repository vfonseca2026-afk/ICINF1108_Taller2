from sqlalchemy import Column, Integer, String
from app.shared.database import Base 

class PetModel(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    owner_name = Column(String(100), nullable=True)