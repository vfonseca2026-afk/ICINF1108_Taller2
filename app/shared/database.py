import os
from collections.abc import Iterator
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")

    if not url:
        raise RuntimeError(
            "DATABASE_URL no está definida. Copia .env.example a .env y revísala."
        )

    return url


class Base(DeclarativeBase):
    pass


engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


def get_db() -> Iterator[Session]:
    """Una sesión por request (dependencia de FastAPI)."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@contextmanager
def transaction(db: Session) -> Iterator[None]:
    """Unidad de trabajo: commit si todo sale bien, rollback ante cualquier error."""
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise
