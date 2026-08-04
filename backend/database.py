from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_engine("sqlite:///ticketdatabase.db", connect_args={"check_same_thread": False})


def init_db() -> None:
    import models.attachment  # noqa: F401
    import models.comment  # noqa: F401
    import models.ticket  # noqa: F401
    import models.user  # noqa: F401

    Base.metadata.create_all(bind=engine)

