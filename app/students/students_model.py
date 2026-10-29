from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base


class StudentModel(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), nullable=False
    )

    pets: Mapped[list["PetModel"]] = relationship(  # noqa: F821
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
