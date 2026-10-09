import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

load_dotenv()

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

# Los tests usan SU PROPIA base. En CI, DATABASE_URL ya apunta a riskflow_test.
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")

if not TEST_DATABASE_URL:
    pytest.exit(
        "Falta TEST_DATABASE_URL. Definila en el .env apuntando a una base de test "
        "(por ejemplo .../riskflow_test).",
        returncode=2,
    )

_db_name = make_url(TEST_DATABASE_URL).database or ""
if "test" not in _db_name.lower():
    pytest.exit(
        f"Por seguridad, los tests solo corren contra bases con 'test' en el nombre "
        f"(esta es '{_db_name}'). Los tests borran todas las tablas al terminar. "
        "Definí TEST_DATABASE_URL apuntando a una base de test.",
        returncode=2,
    )

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()