import importlib
import os
import pkgutil
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

ALEMBIC_DIR = Path(__file__).resolve().parent
ROOT_DIR = ALEMBIC_DIR.parent
PROJECT_DIR = ROOT_DIR / "ICINF1108-templates2026"

sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(ROOT_DIR))

for env_file in (PROJECT_DIR / ".env", ROOT_DIR / ".env"):
    if env_file.exists():
        load_dotenv(env_file)

from app.shared.database import Base # type: ignore


def import_all_models() -> None:
    import app # type: ignore

    for module_info in pkgutil.walk_packages(app.__path__, prefix="app."):
        if "model" in module_info.name.lower():
            try:
                importlib.import_module(module_info.name)
            except Exception as exc:
                print(f"[alembic] No se pudo importar {module_info.name}: {exc}")


import_all_models()


def running_in_docker() -> bool:
    return os.path.exists("/.dockerenv")


def get_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        raise RuntimeError("DATABASE_URL no está definida. Revisa tu archivo .env.")

    url = make_url(raw_url)

    if not running_in_docker() and url.host == "db":
        host_port = int(os.getenv("POSTGRES_HOST_PORT", url.port or 5432))
        url = url.set(host="localhost", port=host_port)

    return url.render_as_string(hide_password=False)


config = context.config
config.set_main_option("sqlalchemy.url", get_database_url().replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()