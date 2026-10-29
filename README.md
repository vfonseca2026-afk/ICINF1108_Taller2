# Taller Evaluado II: Dockerización y Aplicación de ORM

**Asignatura:** ICINF1108 - Desarrollo Backend
**Universidad Católica de Temuco**

## Integrantes del Grupo

* **Vicente Fonseca** (Líder / DevOps)
* **Danna Ramirez** (Desarrollo Módulo Students / ORM)
* **Matías Manquelaf** (Desarrollo Módulo Pets / ORM)
* **Miguel Torres** (Gestión de Transacciones y QA)

---

## Descripción del Proyecto

Este proyecto corresponde al Taller II de Desarrollo Backend. Consiste en migrar una API desarrollada en **FastAPI** (con almacenamiento temporal en memoria) hacia una arquitectura persistente, usando **PostgreSQL** como base de datos relacional mediante **SQLAlchemy**, con **Alembic** para las migraciones. La infraestructura de base de datos está contenedorizada con **Docker Compose**.

---

## Tecnologías Utilizadas

* [FastAPI](https://fastapi.tiangolo.com/) - Framework web para Python.
* [PostgreSQL](https://www.postgresql.org/) - Base de datos relacional.
* [SQLAlchemy](https://www.sqlalchemy.org/) - ORM (Object Relational Mapper).
* [Alembic](https://alembic.sqlalchemy.org/) - Gestión de migraciones para SQLAlchemy.
* [Docker & Docker Compose](https://www.docker.com/) - Contenedorización de servicios.
* [uv](https://github.com/astral-sh/uv) - Gestor de paquetes y entornos virtuales para Python.

---

## Estructura del Proyecto

```
Taller2/
├── alembic/                    # Migraciones (env.py, versions/)
├── alembic.ini
├── compose.yml                 # PostgreSQL + Adminer
├── .env                        # Variables de entorno
└── ICINF1108-templates2026/    # Proyecto FastAPI
    ├── app/
    ├── .venv/
    └── pyproject.toml
```

---

## Instrucciones de Configuración y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/vfonseca2026-afk/ICINF1108_Taller2.git
cd ICINF1108_Taller2
```

### 2. Configurar las variables de entorno

Crea un archivo `.env` en la raíz del proyecto (junto a `compose.yml` y `alembic.ini`):

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secretpassword
POSTGRES_DB=taller_db
POSTGRES_HOST_PORT=5432
DATABASE_URL=postgresql+psycopg2://postgres:secretpassword@db:5432/taller_db
```

> **Nota:** `DATABASE_URL` usa el host `db`, que es el nombre del servicio dentro de la red de Docker. Cuando ejecutas Alembic desde tu máquina (fuera de Docker), `alembic/env.py` reemplaza automáticamente `db` por `localhost` y usa el puerto de `POSTGRES_HOST_PORT`. No necesitas cambiar el `.env` manualmente.

### 3. Levantar la base de datos con Docker

Con Docker abierto, ejecuta desde la raíz del proyecto:

```bash
docker compose up -d
docker compose ps
```

Los servicios `db` (PostgreSQL, puerto `5432`) y `adminer` (puerto `8080`) deben aparecer como `Up`.

### 4. Activar el entorno virtual e instalar dependencias

```powershell
# Windows (PowerShell)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\ICINF1108-templates2026\.venv\Scripts\Activate.ps1
```

Si es necesario sincronizar dependencias:

```bash
cd ICINF1108-templates2026
uv sync
cd ..
```

### 5. Generar y ejecutar las migraciones

Desde la raíz del proyecto, con el entorno virtual activo y la base de datos levantada:

```bash
# Generar la migración (solo la primera vez o cuando cambien los modelos)
alembic revision --autogenerate -m "Initial migration"

# Aplicar las migraciones
alembic upgrade head
```

Antes de aplicar, revisa el archivo generado en `alembic/versions/`: `upgrade()` debe contener instrucciones como `op.create_table(...)`. Si solo contiene `pass`, Alembic no encontró los modelos (ver sección de problemas comunes).

> `alembic/env.py` importa automáticamente los módulos dentro de `app/` cuyo nombre contenga "model" y que hereden de `Base` (definida en `app/shared/database.py`).

### 6. Ejecutar la aplicación

Desde la carpeta del proyecto:

```bash
cd ICINF1108-templates2026
uvicorn app.main:app --reload
```

* API: `http://localhost:8000`
* Documentación interactiva (Swagger): `http://localhost:8000/docs`

---

## Administración de la Base de Datos (Adminer)

Disponible en `http://localhost:8080` con los siguientes datos:

| Campo | Valor |
|---|---|
| Sistema | PostgreSQL |
| Servidor | `db` |
| Usuario | `postgres` |
| Contraseña | `secretpassword` |
| Base de datos | `taller_db` |

---

## Problemas Comunes

**`could not translate host name "db" to address`**
Estás ejecutando Alembic fuera de Docker con un `env.py` que no reemplaza el host. Usa el `alembic/env.py` del repositorio, o define `DATABASE_URL` con `localhost` en la terminal:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:secretpassword@localhost:5432/taller_db"
```

**La migración sale vacía (`pass` en `upgrade()`)**
Los modelos no están registrados en `Base.metadata`. Verifica que las clases hereden de `Base` y que estén en un módulo cuyo nombre contenga "model" (por ejemplo `app/students/models.py`), o impórtalos explícitamente en `alembic/env.py`. Borra la migración vacía antes de volver a generarla:

```powershell
Remove-Item alembic\versions\<id>_initial_migration.py
```

**El puerto 5432 está ocupado**
Si tienes otro PostgreSQL instalado en tu máquina, cambia el mapeo en `compose.yml` a `"5433:5432"` y define `POSTGRES_HOST_PORT=5433` en el `.env`.

**Aviso `the attribute version is obsolete`**
Es inofensivo. Puedes eliminar la línea `version: '3.8'` de `compose.yml`.

**Advertencia de Pylance `Import "app" could not be resolved`**
Es solo del editor. Agrega en `.vscode/settings.json`:

```json
{
  "python.analysis.extraPaths": ["./ICINF1108-templates2026"]
}
```

---

## Comandos Útiles

```bash
docker compose down        # Detener los servicios
docker compose down -v     # Detener y borrar los datos de la base
alembic current            # Ver la revisión aplicada
alembic history            # Ver el historial de migraciones
alembic downgrade -1       # Revertir la última migración
```