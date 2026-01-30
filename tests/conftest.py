"""
Configuración global de pytest.
Este archivo se ejecuta ANTES de todos los tests.

Fixtures = Funciones que preparan el entorno de prueba.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app

# BASE DE DATOS DE PRUEBA (EN MEMORIA)

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture(scope="function")
def db_session():
    """
    Crea una sesión de base de datos limpia para cada test.
    
    scope="function": Se ejecuta ANTES de cada test y se destruye DESPUÉS.
    
    ¿Qué hace?
    1. Crea todas las tablas vacías
    2. Devuelve la sesión para el test
    3. Al terminar el test, borra todo (rollback)
    4. Elimina las tablas
    """
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    db = TestingSessionLocal()
    
    try:
        yield db  # El test usa esta sesión
    finally:
        db.rollback()  # Deshacer cambios
        db.close()     # Cerrar conexión
        Base.metadata.drop_all(bind=engine)  # Borrar tablas


@pytest.fixture(scope="function")
def client(db_session):
    """
    Cliente HTTP para hacer requests a la API en tests.
    
    Usa la base de datos de prueba en lugar de la real.
    """
    # Sobreescribir la dependencia get_db() con nuestra sesión de test
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Crear cliente de test
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiar override
    app.dependency_overrides.clear()
