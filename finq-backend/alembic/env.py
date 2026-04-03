from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy import engine_from_config

from alembic import context

# Import Base and ALL models so autogenerate sees the full schema
from app.database import Base
from app.models import (  # noqa: F401 — side-effect imports register metadata
    Insight,
    Post, PostLike, PostComment,
    Friend, FriendStatus,
    User,
    ChatSession, ChatMessage,
)
from app.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with our settings (ignores the placeholder in alembic.ini)
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    We build the engine directly from settings so that DATABASE_URL is
    always honoured (including Supabase pooler URLs).
    """
    db_url = settings.database_url

    # Ensure SSL for any non-SQLite database (Supabase requires it)
    if not db_url.startswith("sqlite"):
        if "sslmode" not in db_url:
            separator = "&" if "?" in db_url else "?"
            db_url = f"{db_url}{separator}sslmode=require"

    connectable = create_engine(
        db_url,
        poolclass=pool.NullPool,  # NullPool is correct for migration scripts
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,          # detect column type changes
            compare_server_default=True,  # detect default value changes
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

