# Taller Evaluado II · Dockerización y ORM (FastAPI + PostgreSQL)

ICINF1108 - Desarrollo Backend · Universidad Católica de Temuco

API CRUD de **Students** y **Pets** (relación 1:N) persistida en **PostgreSQL** con
**SQLAlchemy** y migraciones versionadas con **Alembic**. La BD y su admin visual (Adminer)
corren en Docker.

## Arranque rápido (todo en Docker)

```bash
cp .env.example .env
docker compose up -d --build
```

- API + frontend: http://localhost:3000 (Swagger en `/docs`)
- Adminer: http://localhost:8080 (Sistema: PostgreSQL · Servidor: `db` · usuario/clave/BD del `.env`)

La API aplica `alembic upgrade head` al iniciar.

## Desarrollo local (solo la BD en Docker)

```bash
cp .env.example .env
make install     # uv sync
make db          # levanta postgres + adminer
make migrate     # alembic upgrade head
make dev         # http://localhost:3000
make test        # pytest (requiere la BD levantada y migrada)
```

## Modelo de datos

- `students (id, name, username*, email*, age, created_at, updated_at)`
- `pets (id, student_id → students.id ON DELETE CASCADE, name, species, age, created_at, updated_at)`
- `*` = único. Además `UNIQUE (student_id, name)` en `pets`.

## Transacciones

Los repositorios solo hacen `add/flush`; **los servicios controlan la transacción** con
`transaction(db)` (`app/shared/database.py`): commit si todo sale bien, rollback ante cualquier error.

- `POST /api/students` con `pets`: estudiante + mascotas en **una sola transacción**. Si una mascota
  falla (nombre repetido, error de BD) no queda nada guardado.
- `DELETE /api/students/{id}`: borra estudiante y mascotas en una operación (FK con `CASCADE`).

Los rollbacks están verificados en `tests/test_persistence_and_transactions.py`.

## Migraciones

```bash
uv run alembic revision --autogenerate -m "mensaje"   # tras cambiar modelos
uv run alembic upgrade head
```

## Flujo de Git

Cada integrante trabaja en su rama (`git checkout -b <usuario>`), hace `git push -u origin <usuario>`
y abre un Pull Request hacia `main`. Nadie hace push directo a `main`.
