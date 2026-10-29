from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.shared.database import Base

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)