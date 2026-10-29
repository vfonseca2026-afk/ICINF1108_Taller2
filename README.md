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
Este proyecto corresponde al Taller II de Desarrollo Backend, el cual consiste en migrar una API desarrollada en **FastAPI** (con almacenamiento temporal en memoria) hacia una arquitectura persistente utilizando **PostgreSQL** como base de datos relacional mediante **SQLAlchemy** y **Alembic** para las migraciones. Asimismo, toda la infraestructura se encuentra contenedorizada utilizando **Docker Compose**.

---

## Tecnologías Utilizadas
* [FastAPI](https://fastapi.tiangolo.com/) - Framework web asíncrono para Python.
* [PostgreSQL](https://www.postgresql.org/) - Sistema de gestión de bases de datos relacional.
* [SQLAlchemy](https://www.sqlalchemy.org/) - ORM (Object Relational Mapper).
* [Alembic](https://alembic.sqlalchemy.org/) - Herramienta de gestión de migraciones para SQLAlchemy.
* [Docker & Docker Compose](https://www.docker.com/) - Contenedorización de servicios.
* [uv](https://github.com/astral-sh/uv) - Gestor de paquetes y entorno virtual ultrarrápido para Python.

---

## Instrucciones de Configuración y Ejecución

### 1. Clonar el Repositorio
Clona el repositorio oficial en tu máquina local:
```bash
git clone [https://github.com/](https://github.com/)<tu-usuario>/<tu-repositorio>.git
cd <tu-repositorio>