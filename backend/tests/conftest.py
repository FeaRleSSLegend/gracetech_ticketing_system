"""Shared test setup.

Every test runs against a throwaway SQLite file, never the dev
ticketdatabase.db, so tests neither depend on nor destroy real data. This lives
in conftest so all test modules share one engine and one get_db override --
two modules each installing their own override would fight over which database
the app actually talks to.
"""

import os
import sys
import tempfile

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import models  # noqa: F401,E402  (registers every model on Base.metadata)
from core.dependencies import get_db  # noqa: E402
from database import Base  # noqa: E402
from main import app  # noqa: E402

TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "gracetech_test.db")
test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@event.listens_for(test_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
