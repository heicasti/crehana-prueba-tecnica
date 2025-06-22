# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.infrastructure.database.connection import Base, get_db
import os
from dotenv import load_dotenv

# Variables de entorno
load_dotenv(".env")

# URL de la base de datos de prueba MySQL
SQLALCHEMY_DATABASE_URL_TEST = os.getenv("DATABASE_URL")

# Motor de SQLAlchemy para las pruebas
engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST
)

# Sesión local para las pruebas
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(name="db_session")
def db_session_fixture():
    # *** IMPORTANTE: Elimina todas las tablas y las recrea en cada test. ***
    # Esto asegura que cada prueba tenga un estado de base de datos limpio.
    # base de datos de PRUEBA!!!!!!
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    db = TestingSessionLocal()
    try:
        yield db # Sesión de DB a la prueba
    finally:
        db.close()
        # Opcional: Base.metadata.drop_all(bind=engine_test)

@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    # Sobrescribe la dependencia get_db para que use la sesión de DB de prueba
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Limpia las sobrescrituras después de la prueba
    app.dependency_overrides = {}