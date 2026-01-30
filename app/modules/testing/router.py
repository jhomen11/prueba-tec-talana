from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.logger import LoggerSetup

# Importamos todos los modelos necesarios
from app.modules.users.models import User, UserRole
from app.modules.questions.models import Question, Option, DifficultyLevel
from app.modules.trivias.models import Trivia, TriviaAssignment, AssignmentStatus

router = APIRouter(prefix="/testing", tags=["Testing & Seeding"])
logger = LoggerSetup.get_logger(__name__)

@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_database(db: Session = Depends(get_db)):
    """
    Ruta Mágica: Crea usuarios, preguntas y trivias de prueba.
    Idempotente: Si los datos ya existen, no los duplica.
    """
    logger.info("Iniciando proceso de Seed Manual...")

    # ------------------------------------------------------------------
    # 1. CREAR USUARIOS (PLAYERS)
    # ------------------------------------------------------------------
    players_data = [
        {"name": "Ana Player", "email": "ana@talana.com"},
        {"name": "Beto Player", "email": "beto@talana.com"},
        {"name": "Carla Player", "email": "carla@talana.com"},
    ]
    
    created_users = []
    default_pass = get_password_hash("123456") # Contraseña fácil para pruebas

    for p in players_data:
        user = db.query(User).filter(User.email == p["email"]).first()
        if not user:
            user = User(
                full_name=p["name"],
                email=p["email"],
                hashed_password=default_pass,
                role=UserRole.PLAYER
            )
            db.add(user)
            db.commit() # Commit individual para obtener el ID rápido
            db.refresh(user)
            logger.info(f"Usuario creado: {p['email']}")
        created_users.append(user)

    # ------------------------------------------------------------------
    # 2. CREAR PREGUNTAS (9 en total)
    # ------------------------------------------------------------------
    # Lista de preguntas (Texto, Dificultad, Opciones[Texto, Correcta])
    questions_data = [
        # --- FÁCILES ---
        ("¿Cuál es el feriado irrenunciable de septiembre?", DifficultyLevel.EASY, [
            ("18 de Septiembre", True), ("12 de Octubre", False), ("21 de Mayo", False)
        ]),
        ("¿Cuántas horas semanales es la jornada ordinaria máxima actual (2025)?", DifficultyLevel.EASY, [
            ("45 Horas", False), ("44 Horas", True), ("40 Horas", False)
        ]),
        ("¿Quién paga la licencia médica por enfermedad común?", DifficultyLevel.EASY, [
            ("El Empleador", False), ("FONASA o ISAPRE", True), ("La AFC", False)
        ]),
        # --- MEDIAS ---
        ("¿Qué porcentaje de la remuneración es el tope para el descuento de Isapre?", DifficultyLevel.MEDIUM, [
            ("7%", True), ("10%", False), ("No tiene tope", False)
        ]),
        ("¿Cuántos días de permiso tiene el padre por nacimiento de un hijo?", DifficultyLevel.MEDIUM, [
            ("5 días pagados", True), ("3 días pagados", False), ("10 días sin goce", False)
        ]),
        ("En el contrato a plazo fijo, ¿cuántas veces se puede renovar?", DifficultyLevel.MEDIUM, [
            ("Indefinidamente", False), ("Solo 1 vez", True), ("Hasta 3 veces", False)
        ]),
        # --- DIFÍCILES ---
        ("¿Cuál es el tope imponible para el Seguro de Cesantía (2025 estimado)?", DifficultyLevel.HARD, [
            ("122.6 UF", True), ("81.6 UF", False), ("90 UF", False)
        ]),
        ("¿Qué indemnización corresponde si el empleador pone término al contrato por 'Necesidades de la Empresa'?", DifficultyLevel.HARD, [
            ("Años de servicio + Mes de aviso", True), ("Solo vacaciones proporcionales", False), ("Solo Años de servicio", False)
        ]),
        ("¿Qué trabajadores están excluidos de la limitación de jornada (Artículo 22)?", DifficultyLevel.HARD, [
            ("Gerentes y quienes trabajan sin fiscalización superior inmediata", True),
            ("Todos los profesionales", False),
            ("Quienes hacen teletrabajo", False)
        ]),
    ]

    all_questions_objs = []
    
    for q_text, diff, opts_data in questions_data:
        # Verificar existencia
        q_exists = db.query(Question).filter(Question.text == q_text).first()
        if not q_exists:
            new_q = Question(text=q_text, difficulty=diff)
            db.add(new_q)
            db.flush() # Generar ID
            
            for opt_text, is_corr in opts_data:
                db.add(Option(text=opt_text, is_correct=is_corr, question_id=new_q.id))
            
            db.commit()
            db.refresh(new_q)
            all_questions_objs.append(new_q)
        else:
            all_questions_objs.append(q_exists)

    # ------------------------------------------------------------------
    # 3. CREAR TRIVIAS Y ASIGNARLAS
    # ------------------------------------------------------------------
    # Trivia 1: Mix General (Para Ana y Beto)
    trivia1_name = "Mix Laboral Semanal"
    trivia1 = db.query(Trivia).filter(Trivia.name == trivia1_name).first()
    
    if not trivia1:
        trivia1 = Trivia(
            name=trivia1_name, 
            description="Preguntas variadas para calentar motores."
        )
        # Asignamos las primeras 5 preguntas
        trivia1.questions = all_questions_objs[:5] 
        db.add(trivia1)
        db.flush()
        
        # Asignar a Ana y Beto
        for user in created_users[:2]: # Ana y Beto
            assignment = TriviaAssignment(
                trivia_id=trivia1.id, 
                user_id=user.id, 
                status=AssignmentStatus.PENDING
            )
            db.add(assignment)
        
        db.commit()
        logger.info(f"Trivia creada: {trivia1_name}")

    # Trivia 2: Desafío Experto (Para Beto y Carla)
    trivia2_name = "Desafío Experto Legislativo"
    trivia2 = db.query(Trivia).filter(Trivia.name == trivia2_name).first()
    
    if not trivia2:
        trivia2 = Trivia(
            name=trivia2_name, 
            description="Solo preguntas de nivel Medio y Difícil."
        )
        # Asignamos solo las últimas 4 preguntas (Medias/Dificiles)
        trivia2.questions = all_questions_objs[5:] 
        db.add(trivia2)
        db.flush()
        
        # Asignar a Beto y Carla
        for user in created_users[1:]: # Beto y Carla
            assignment = TriviaAssignment(
                trivia_id=trivia2.id, 
                user_id=user.id, 
                status=AssignmentStatus.PENDING
            )
            db.add(assignment)
            
        db.commit()
        logger.info(f"Trivia creada: {trivia2_name}")

    return {"message": "Seed completado con éxito. Usuarios, preguntas y trivias listas."}