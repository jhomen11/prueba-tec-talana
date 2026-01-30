import os
from dotenv import load_dotenv

# Carga las variables del archivo .env en local (fuera de docker)
load_dotenv()

class Settings:
    PROJECT_NAME: str = "TalaTrivia API"
    PROJECT_VERSION: str = "1.0.0"

    # Database
    # Lee la URL completa desde el entorno si existe (p. ej. `DATABASE_URL` desde docker-compose)
    ENV_DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db") # "db" es el nombre del servicio en docker-compose
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "talatrivia_db")
    # Superuser inicial
    FIRST_SUPERUSER_EMAIL: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@talana.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin123")
    
    # Security (JWT)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-CHANGE-IN-PRODUCTION-USE-OPENSSL-RAND")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    @property
    def DATABASE_URL(self) -> str:
        
        if self.ENV_DATABASE_URL:
            return self.ENV_DATABASE_URL
       
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()