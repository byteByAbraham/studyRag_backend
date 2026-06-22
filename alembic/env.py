
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# ---------------------------------------------------------------------
# ARQUITECTURA: Importamos nuestra configuración y metadatos reales
# ---------------------------------------------------------------------
from app.core.config import settings
from app.db.base import Base

# Objeto de configuración de Alembic, que da acceso a los valores del alembic.ini
config = context.config

# Configurar el logging si el archivo ini está presente
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# REQUERIMIENTO: Pasamos la metadata de nuestros modelos para el "Autogenerate"
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Ejecuta las migraciones en modo 'offline'."""
    # Inyectamos dinámicamente la URL calculada de Pydantic Settings
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta las migraciones en modo 'online' (conectado a la BD)."""
    # Obtenemos la configuración de la sección actual
    configuration = config.get_section(config.config_ini_section) or {}
    # Sobrescribimos la URL vacía del .ini con la del archivo .env real
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()