from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.database import check_db_connection, SessionLocal
from app.core.logger import LoggerSetup
from app.modules.users import models as user_models
from app.modules.questions import models as question_models
from app.modules.trivias import models as trivia_models
from app.core.database import engine, Base
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router
from app.core.bootstrap import create_initial_data
from app.modules.questions.router import router as questions_router
from app.modules.trivias.router import router as trivia_router
from app.modules.game.router import router as game_router
from app.modules.testing.router import router as testing_router
from app.modules.ranking.router import router as ranking_router

# 1. Configurar logs ANTES de que arranque la app
LoggerSetup.configure_logging()
logger = LoggerSetup.get_logger(__name__)

# 2. Configurar rate limiter
limiter = Limiter(key_func=get_remote_address) 

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando la app")
    
    # 1. Crear Tablas (Si no existen)
    logger.info("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Verificar Conexión
    try:
        check_db_connection()
    except Exception as e:
        logger.critical(f"Deteniendo inicio por fallo crítico en DB: {e}")
        raise e

    # 3. BOOTSTRAP: Crear datos iniciales (Admin)
    # Creamos una sesión temporal solo para esto
    db = SessionLocal()
    try:
        create_initial_data(db)
    finally:
        db.close() # Importante cerrar la sesión manual
    
    yield
    
    logger.info("Cerrando TalaTrivia API...")

app = FastAPI(
    title="TalaTrivia API",
    description="""
    **API de Trivias Interactivas**
    
    Sistema completo para gestionar trivias, preguntas y juegos de conocimiento.
    
    ## Características principales:
    
    * **Autenticación JWT**: Sistema seguro de login con tokens Bearer
    * **Gestión de Usuarios**: CRUD completo con soft delete y roles (admin/player)
    * **Banco de Preguntas**: Creación y administración de preguntas con múltiples opciones
    * **Rate Limiting**: Protección contra abuso con límites de peticiones por IP
    
    ## Roles:
    
    * **Admin**: Gestión completa de usuarios, preguntas y trivias
    * **Player**: Participación en trivias asignadas
    
    ## Autenticación:
    
    1. Hacer login en `/api/auth/login` con email y password
    2. El token JWT se envía automáticamente en una cookie HttpOnly
    3. Las siguientes peticiones incluyen la cookie automáticamente
    4. Usar `/api/auth/logout` para cerrar sesión
    
    ## Rate Limits:
    
    * **Login**: 5 intentos por minuto por IP
    * **General**: 100 peticiones por minuto por IP
    * **Health Check**: 10 peticiones por minuto
    """,
    version="1.0.0",
    contact={
        "name": "Jhonny Mendoza",
        "email": "jhomen11@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React/Next.js local
        "http://localhost:5173",  # Vite local
        "http://localhost:8080",  # Vue local
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Authorization, Content-Type, etc.
)

@app.get("/")
@limiter.limit("10/minute")
def health_check(request: Request):
    logger.info("Health check")
    return {"status": "ok", "message": "TalaTrivia API is running!"}

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(questions_router)
app.include_router(trivia_router)
app.include_router(game_router)
app.include_router(ranking_router)
app.include_router(testing_router)