from sqlalchemy.orm import Session
from app.modules.users.models import User, UserRole
from app.core.security import get_password_hash
from app.core.logger import LoggerSetup
from app.core.config import settings

# --- IMPORTS NUEVOS PARA PREGUNTAS ---
from app.modules.questions.repository import QuestionRepository
from app.modules.questions.schemas import QuestionCreate, OptionCreate
from app.modules.questions.models import DifficultyLevel

logger = LoggerSetup.get_logger(__name__)

def create_initial_data(db: Session):
    """
    Crea datos iniciales: Superusuario y Preguntas Demo.
    """
    # ----------------------------------------------------------------
    # 1. CREACIÓN DE SUPER ADMIN
    # ----------------------------------------------------------------
    FIRST_SUPERUSER_EMAIL = getattr(settings, "FIRST_SUPERUSER_EMAIL", "admin@talana.com")
    FIRST_SUPERUSER_PASSWORD = getattr(settings, "FIRST_SUPERUSER_PASSWORD", "admin123")
    
    user = db.query(User).filter(User.email == FIRST_SUPERUSER_EMAIL).first()
    
    if user:
        logger.info(f"El Super Admin ya existe ({FIRST_SUPERUSER_EMAIL}).")
    else:
        logger.info(f"Creando Super Admin inicial: {FIRST_SUPERUSER_EMAIL}")
        user = User(
            full_name="Super Admin",
            email=FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(FIRST_SUPERUSER_PASSWORD),
            role=UserRole.ADMIN
        )
        db.add(user)
        db.commit()
        logger.info("Super Admin creado exitosamente.")

    # ----------------------------------------------------------------
    # 2. CREACIÓN DE PREGUNTAS DEMO (1 de cada dificultad)
    # ----------------------------------------------------------------
    question_repo = QuestionRepository(db)

    demo_questions = [
        # --- FÁCIL ---
        QuestionCreate(
            text="¿Cuántos días hábiles de vacaciones tiene un trabajador tras un año de servicio?",
            difficulty=DifficultyLevel.EASY,
            options=[
                OptionCreate(text="15 días", is_correct=True),
                OptionCreate(text="10 días", is_correct=False),
                OptionCreate(text="20 días", is_correct=False),
            ]
        ),
        # --- MEDIO ---
        QuestionCreate(
            text="¿Cuál es el tope de años para la indemnización por años de servicio?",
            difficulty=DifficultyLevel.MEDIUM,
            options=[
                OptionCreate(text="Sin tope", is_correct=False),
                OptionCreate(text="11 años", is_correct=True),
                OptionCreate(text="5 años", is_correct=False),
            ]
        ),
        # --- DIFÍCIL ---
        QuestionCreate(
            text="¿Hasta cuándo se extiende el fuero maternal?",
            difficulty=DifficultyLevel.HARD,
            options=[
                OptionCreate(text="Hasta los 2 años del hijo", is_correct=False),
                OptionCreate(text="Hasta 1 año después de expirado el postnatal", is_correct=True),
                OptionCreate(text="Solo durante el embarazo", is_correct=False),
            ]
        )
    ]

    logger.info("Verificando preguntas demo...")
    
    for q_data in demo_questions:
        exists = question_repo.get_by_text(q_data.text)
        if not exists:
            try:
                question_repo.create(q_data)
                logger.info(f"Pregunta creada: '{q_data.text[:30]}...' ({q_data.difficulty.value})")
            except Exception as e:
                logger.error(f"Error creando pregunta demo: {e}")
        else:
            logger.info(f"La pregunta '{q_data.text[:30]}...' ya existe.")