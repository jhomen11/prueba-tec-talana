from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.logger import LoggerSetup # <--- Importamos nuestro centralizador

# Obtenemos el logger con el nombre de este archivo
logger = LoggerSetup.get_logger(__name__)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Conexión a la Base de Datos exitosa.")
    except Exception as e:
        logger.error(f" Error conectando a la Base de Datos: {e}")
        raise e