from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("sqlite:///ticketdatabase.db", connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
