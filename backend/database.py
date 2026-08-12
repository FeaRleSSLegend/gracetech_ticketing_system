import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ticketdatabase.db")

# Render hands out URLs with the legacy "postgres://" prefix, which SQLAlchemy 2.x
# no longer recognises as a dialect name.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# SQLite needs to be told to enforce foreign keys on every connection.
# Postgres enforces them natively and has no such pragma.
if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def init_db() -> None:
    import models.attachment  # noqa: F401
    import models.comment  # noqa: F401
    import models.notification  # noqa: F401
    import models.ticket  # noqa: F401
    import models.user  # noqa: F401

    Base.metadata.create_all(bind=engine)
