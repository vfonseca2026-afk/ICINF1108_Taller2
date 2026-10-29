# Taller Evaluado II · Dockerización y ORM (FastAPI + PostgreSQL)

ICINF1108 - Desarrollo Backend · Universidad Católica de Temuco

API CRUD de **Students** y **Pets** (relación 1:N) persistida en **PostgreSQL** con
**SQLAlchemy** y migraciones versionadas con **Alembic**. La BD y su admin visual (Adminer)
corren en Docker, igual que la API.

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) abierto y en ejecución.
- Git.
- Solo para desarrollo local sin Docker para la API: [uv](https://docs.astral.sh/uv/) y Python 3.13.

## Arranque rápido (todo en Docker)

**1. Crear el archivo de variables de entorno**

```bash
# Linux / macOS / Git Bash
cp .env.example .env
```

```powershell
# Windows (PowerShell)
Copy-Item .env.example .env
```

El `.env` real **no se sube al repositorio** (está en `.gitignore`); solo se versiona `.env.example`.

**2. Levantar los servicios**

```bash
docker compose up -d --build
docker compose ps
```

La primera vez tarda un poco porque descarga las imágenes y construye la de la API.
Deberías ver tres contenedores:

| Contenedor | Servicio | Estado esperado | Puerto |
|---|---|---|---|
| `postgres_db` | PostgreSQL 16 | `Up (healthy)` | 5432 |
| `postgres_adminer` | Adminer (admin visual) | `Up` | 8080 |
| `students_api` | API FastAPI + frontend | `Up` | 3000 |

**3. Abrir la aplicación**

- API + frontend: http://localhost:3000
- Documentación Swagger: http://localhost:3000/docs
- Adminer: http://localhost:8080

La API aplica `alembic upgrade head` automáticamente al iniciar, así que las tablas se crean solas.

## Variables de entorno (`.env`)

| Variable | Valor por defecto | Uso |
|---|---|---|
| `POSTGRES_USER` | `postgres` | Usuario de la BD |
| `POSTGRES_PASSWORD` | `secretpassword` | Contraseña de la BD (cámbiala si la reutilizas fuera del taller) |
| `POSTGRES_DB` | `taller_db` | Nombre de la BD |
| `POSTGRES_HOST_PORT` | `5432` | Puerto de la BD publicado en tu máquina |
| `ADMINER_PORT` | `8080` | Puerto de Adminer en tu máquina |
| `DATABASE_URL` | `postgresql+psycopg2://postgres:secretpassword@localhost:5432/taller_db` | Conexión para ejecutar la API/Alembic **desde tu máquina** |

> Dentro de Docker la API **no** usa `localhost`: `compose.yml` sobreescribe `DATABASE_URL`
> con el host `db` (el nombre del servicio en la red de Docker).

## Entrar a Adminer (administrador visual de la BD)

Abre http://localhost:8080 y completa el login:

| Campo | Valor |
|---|---|
| **Motor de base de datos** | **PostgreSQL** (por defecto aparece MySQL/MariaDB, hay que cambiarlo) |
| Servidor | `db` |
| Usuario | `postgres` |
| Contraseña | `secretpassword` |
| Base de datos | `taller_db` |

Dentro verás las tablas `students`, `pets` y `alembic_version` (esta última confirma que la
migración se aplicó).

## Cómo comprobar que todo funciona

**1. La migración corrió y la API está arriba**

```bash
docker compose logs api
```

Debe aparecer `Running upgrade -> d59fc79f9351, create students and pets tables` y luego
`Uvicorn running on http://0.0.0.0:3000`.

**2. Los datos se guardan en PostgreSQL**
Crea un estudiante y una mascota desde http://localhost:3000 y revisa que aparezcan en las tablas
`students` y `pets` en Adminer.

**3. Persistencia real (no es memoria)**

```bash
docker compose restart api
```

Recarga el frontend: los datos siguen ahí. También sobreviven a `docker compose down`
(el volumen `pgdata` conserva la información).

**4. Rollback de la transacción**
En http://localhost:3000/docs ejecuta `POST /api/students` con una mascota repetida:

```json
{
  "name": "Test Rollback",
  "username": "testrollback",
  "email": "rollback@alu.uct.cl",
  "age": 22,
  "pets": [
    { "name": "Rex", "species": "Perro" },
    { "name": "Rex", "species": "Gato" }
  ]
}
```

Debe responder **409** y, en Adminer, el estudiante `testrollback` **no debe existir**
(la transacción se revirtió completa).

## Comandos útiles de Docker

```bash
docker compose ps                 # estado de los contenedores
docker compose logs api           # logs de la API
docker compose logs db            # logs de PostgreSQL
docker compose restart api        # reiniciar solo la API
docker compose down               # detener (conserva los datos)
docker compose down -v            # detener Y BORRAR los datos (volumen pgdata)
docker compose up -d --build      # reconstruir y levantar tras cambiar código
```

## Problemas comunes

**`postgres_db is unhealthy` / `database files are incompatible with server`**
El volumen `pgdata` quedó creado con otra versión de PostgreSQL (por ejemplo la 15) y ahora el
contenedor usa la 16. Si solo tienes datos de prueba, borra el volumen y vuelve a levantar:

```bash
docker compose down -v
docker compose up -d --build
```

**El login de Adminer falla**
Revisa que el *Motor de base de datos* sea **PostgreSQL** y no MySQL/MariaDB, y que el servidor
sea `db` (no `localhost`).

**El puerto 5432, 3000 u 8080 ya está en uso**
Probablemente tienes un PostgreSQL instalado en tu PC u otro programa usando ese puerto.
Cambia `POSTGRES_HOST_PORT` (por ejemplo a `5433`) o `ADMINER_PORT` en el `.env` y ejecuta de nuevo
`docker compose up -d`. Para el puerto 3000, edita el mapeo `"3000:3000"` del servicio `api` en
`compose.yml`.

**`students_api` se reinicia o no aparece**
Mira `docker compose logs api`. Los motivos habituales son que la BD aún no estaba lista, un error
en la migración o un `.env` mal copiado.

**Cambié el código y no veo los cambios**
La imagen de la API se construye al levantar: usa `docker compose up -d --build`.

## Desarrollo local (solo la BD en Docker)

Útil para desarrollar con recarga automática sin reconstruir la imagen:

```bash
cp .env.example .env     # (PowerShell: Copy-Item .env.example .env)
make install             # uv sync
make db                  # levanta postgres + adminer
make migrate             # alembic upgrade head
make dev                 # http://localhost:3000 (con --reload)
make test                # pytest (requiere la BD levantada y migrada)
```

> **Ojo:** los tests **vacían** las tablas `students` y `pets` de la base que tengan configurada.
> Ejecútalos al final, o contra una base distinta, si no quieres perder los datos de prueba.

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

Antes de aplicar una migración generada, revisa el archivo en `alembic/versions/`:
`upgrade()` debe contener instrucciones como `op.create_table(...)` y no solo `pass`.

## Flujo de Git

Cada integrante trabaja en su rama (`git checkout -b <usuario>`), hace `git push -u origin <usuario>`
y abre un Pull Request hacia `main`. Nadie hace push directo a `main`.
No se versionan `.env`, `.venv`, `__pycache__` ni archivos `.db`.