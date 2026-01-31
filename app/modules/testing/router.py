from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.logger import LoggerSetup
from datetime import datetime, timedelta
import random

from app.modules.users.models import User, UserRole
from app.modules.questions.models import Question, Option, DifficultyLevel
from app.modules.trivias.models import Trivia, TriviaAssignment, AssignmentStatus, UserAnswer

router = APIRouter(prefix="/testing", tags=["Testing & Seeding"])
logger = LoggerSetup.get_logger(__name__)

@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_database(db: Session = Depends(get_db)):
    """
    Crea datos completos de prueba.
    
    Genera:
    - 5 jugadores
    - 12 preguntas (4 easy, 4 medium, 4 hard)
    - 3 trivias diferentes
    - Simula partidas completadas con respuestas
    - Genera estadísticas para el ranking
    
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
        {"name": "Diego Player", "email": "diego@talana.com"},
        {"name": "Elena Player", "email": "elena@talana.com"},
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
            db.commit()
            db.refresh(user)
            logger.info(f"Usuario creado: {p['email']}")
        created_users.append(user)

    # ------------------------------------------------------------------
    # 2. CREAR PREGUNTAS (12 en total: 4 fáciles, 4 medias, 4 difíciles)
    # ------------------------------------------------------------------
    questions_data = [
        # --- FÁCILES (1 punto cada una) ---
        ("¿Cuál es el feriado irrenunciable de septiembre?", DifficultyLevel.EASY, [
            ("18 de Septiembre", True), ("12 de Octubre", False), ("21 de Mayo", False)
        ]),
        ("¿Cuántas horas semanales es la jornada ordinaria máxima actual (2025)?", DifficultyLevel.EASY, [
            ("45 Horas", False), ("44 Horas", True), ("40 Horas", False)
        ]),
        ("¿Quién paga la licencia médica por enfermedad común?", DifficultyLevel.EASY, [
            ("El Empleador", False), ("FONASA o ISAPRE", True), ("La AFC", False)
        ]),
        ("¿Cuántos días de vacaciones anuales corresponden legalmente?", DifficultyLevel.EASY, [
            ("15 días hábiles", True), ("20 días corridos", False), ("10 días hábiles", False)
        ]),
        
        # --- MEDIAS (2 puntos cada una) ---
        ("¿Qué porcentaje de la remuneración es el tope para el descuento de Isapre?", DifficultyLevel.MEDIUM, [
            ("7%", True), ("10%", False), ("No tiene tope", False)
        ]),
        ("¿Cuántos días de permiso tiene el padre por nacimiento de un hijo?", DifficultyLevel.MEDIUM, [
            ("5 días pagados", True), ("3 días pagados", False), ("10 días sin goce", False)
        ]),
        ("En el contrato a plazo fijo, ¿cuántas veces se puede renovar?", DifficultyLevel.MEDIUM, [
            ("Indefinidamente", False), ("Solo 1 vez", True), ("Hasta 3 veces", False)
        ]),
        ("¿Cuál es el periodo de prueba máximo en un contrato indefinido?", DifficultyLevel.MEDIUM, [
            ("30 días", False), ("90 días", True), ("60 días", False)
        ]),
        
        # --- DIFÍCILES (3 puntos cada una) ---
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
        ("¿Cuánto tiempo tiene el trabajador para reclamar ante la Inspección del Trabajo?", DifficultyLevel.HARD, [
            ("60 días desde la separación", True), ("90 días desde la separación", False), ("30 días", False)
        ]),
    ]

    all_questions_objs = []
    
    for q_text, diff, opts_data in questions_data:
        q_exists = db.query(Question).filter(Question.text == q_text).first()
        if not q_exists:
            new_q = Question(text=q_text, difficulty=diff)
            db.add(new_q)
            db.flush()
            
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
    
    # Trivia 1: Mix Básico (preguntas fáciles) - Para todos
    trivia1_name = "Introducción Laboral"
    trivia1 = db.query(Trivia).filter(Trivia.name == trivia1_name).first()
    
    if not trivia1:
        trivia1 = Trivia(
            name=trivia1_name, 
            description="Preguntas básicas para comenzar."
        )
        trivia1.questions = all_questions_objs[0:4]  # 4 fáciles
        db.add(trivia1)
        db.flush()
        
        # Asignar a todos los usuarios
        for user in created_users:
            assignment = TriviaAssignment(
                trivia_id=trivia1.id, 
                user_id=user.id, 
                status=AssignmentStatus.PENDING
            )
            db.add(assignment)
        
        db.commit()
        logger.info(f"Trivia creada: {trivia1_name}")

    # Trivia 2: Nivel Intermedio (medias) - Para 3 usuarios
    trivia2_name = "Desafío Intermedio"
    trivia2 = db.query(Trivia).filter(Trivia.name == trivia2_name).first()
    
    if not trivia2:
        trivia2 = Trivia(
            name=trivia2_name, 
            description="Preguntas de dificultad media."
        )
        trivia2.questions = all_questions_objs[4:8]  # 4 medias
        db.add(trivia2)
        db.flush()
        
        # Asignar a Beto, Carla, Diego
        for user in created_users[1:4]:
            assignment = TriviaAssignment(
                trivia_id=trivia2.id, 
                user_id=user.id, 
                status=AssignmentStatus.PENDING
            )
            db.add(assignment)
            
        db.commit()
        logger.info(f"Trivia creada: {trivia2_name}")

    # Trivia 3: Expertos (difíciles) - Para 2 usuarios
    trivia3_name = "Solo Expertos"
    trivia3 = db.query(Trivia).filter(Trivia.name == trivia3_name).first()
    
    if not trivia3:
        trivia3 = Trivia(
            name=trivia3_name, 
            description="Máximo nivel de dificultad."
        )
        trivia3.questions = all_questions_objs[8:12]  # 4 difíciles
        db.add(trivia3)
        db.flush()
        
        # Asignar a Diego y Elena
        for user in created_users[3:5]:
            assignment = TriviaAssignment(
                trivia_id=trivia3.id, 
                user_id=user.id, 
                status=AssignmentStatus.PENDING
            )
            db.add(assignment)
            
        db.commit()
        logger.info(f"Trivia creada: {trivia3_name}")

    # ------------------------------------------------------------------
    # 4. SIMULAR PARTIDAS COMPLETADAS
    # ------------------------------------------------------------------
    logger.info("Simulando partidas completadas...")
    
    # Ana: Completa Trivia 1 con 3/4 correctas (3 puntos)
    simulate_game_completion(
        db, 
        user_email="ana@talana.com",
        trivia_name="Introducción Laboral",
        correct_answers=3,
        days_ago=5
    )
    
    # Beto: Completa Trivia 1 con 4/4 correctas (4 puntos)
    simulate_game_completion(
        db,
        user_email="beto@talana.com",
        trivia_name="Introducción Laboral",
        correct_answers=4,
        days_ago=4
    )
    
    # Beto: Completa Trivia 2 con 2/4 correctas (4 puntos - 2 medias)
    simulate_game_completion(
        db,
        user_email="beto@talana.com",
        trivia_name="Desafío Intermedio",
        correct_answers=2,
        days_ago=2
    )
    
    # Carla: Completa Trivia 1 con 2/4 correctas (2 puntos)
    simulate_game_completion(
        db,
        user_email="carla@talana.com",
        trivia_name="Introducción Laboral",
        correct_answers=2,
        days_ago=3
    )
    
    # Diego: Completa Trivia 1 con 4/4 correctas (4 puntos)
    simulate_game_completion(
        db,
        user_email="diego@talana.com",
        trivia_name="Introducción Laboral",
        correct_answers=4,
        days_ago=6
    )
    
    # Diego: Completa Trivia 3 con 1/4 correctas (3 puntos - 1 difícil)
    simulate_game_completion(
        db,
        user_email="diego@talana.com",
        trivia_name="Solo Expertos",
        correct_answers=1,
        days_ago=1
    )

    return {
        "message": "Seed completado con éxito",
        "users_created": len(created_users),
        "questions_created": len(all_questions_objs),
        "trivias_created": 3,
        "games_simulated": 6,
        "note": "Algunos jugadores ya tienen partidas completadas con estadísticas"
    }


def simulate_game_completion(
    db: Session,
    user_email: str,
    trivia_name: str,
    correct_answers: int,
    days_ago: int = 1
):
    """
    Simula que un usuario completó una trivia.
    
    Args:
        user_email: Email del jugador
        trivia_name: Nombre de la trivia
        correct_answers: Cuántas respuestas correctas tuvo
        days_ago: Hace cuántos días jugó
    """
    user = db.query(User).filter(User.email == user_email).first()
    trivia = db.query(Trivia).filter(Trivia.name == trivia_name).first()
    
    if not user or not trivia:
        logger.warning(f"No se pudo simular partida: usuario o trivia no encontrados")
        return
    
    # Buscar la asignación
    assignment = db.query(TriviaAssignment).filter(
        TriviaAssignment.user_id == user.id,
        TriviaAssignment.trivia_id == trivia.id,
        TriviaAssignment.status == AssignmentStatus.PENDING
    ).first()
    
    if not assignment:
        logger.warning(f"No hay asignación pendiente para {user_email} en {trivia_name}")
        return
    
    # Verificar que no haya respuestas previas
    existing_answers = db.query(UserAnswer).filter(
        UserAnswer.assignment_id == assignment.id
    ).first()
    
    if existing_answers:
        logger.info(f"Partida ya simulada para {user_email} en {trivia_name}")
        return
    
    # Obtener preguntas de la trivia
    questions = trivia.questions
    total_score = 0
    
    # Simular respuestas
    for i, question in enumerate(questions):
        # Decidir si esta respuesta será correcta
        is_correct_answer = (i < correct_answers)
        
        # Buscar la opción correcta o incorrecta
        if is_correct_answer:
            selected_option = next((opt for opt in question.options if opt.is_correct), None)
        else:
            selected_option = next((opt for opt in question.options if not opt.is_correct), None)
        
        if not selected_option:
            continue
        
        # Calcular puntos
        points = 0
        if is_correct_answer:
            if question.difficulty == DifficultyLevel.EASY:
                points = 1
            elif question.difficulty == DifficultyLevel.MEDIUM:
                points = 2
            elif question.difficulty == DifficultyLevel.HARD:
                points = 3
        
        total_score += points
        
        # Crear la respuesta
        user_answer = UserAnswer(
            assignment_id=assignment.id,
            question_id=question.id,
            selected_option_id=selected_option.id,
            is_correct=is_correct_answer,
            points_awarded=points
        )
        db.add(user_answer)
    
    # Marcar asignación como completada
    assignment.status = AssignmentStatus.COMPLETED
    assignment.total_score = total_score
    
    # Modificar created_at para simular que se jugó hace días
    fake_date = datetime.utcnow() - timedelta(days=days_ago)
    assignment.created_at = fake_date
    
    db.commit()
    logger.info(f"Partida simulada: {user_email} en {trivia_name} - {total_score} puntos")


@router.delete("/reset", status_code=status.HTTP_200_OK)
def reset_test_data(db: Session = Depends(get_db)):
    """
    Elimina TODA la data de testing.
    
    ADVERTENCIA: Esto borrará:
    - Todos los usuarios tipo PLAYER creados por el seed
    - Todas las preguntas
    - Todas las trivias
    - Todas las asignaciones y respuestas
    
    NO borra al usuario admin inicial.
    """
    logger.warning("Iniciando reset de data de testing...")
    
    try:
        # 1. Eliminar respuestas de usuarios
        deleted_answers = db.query(UserAnswer).delete()
        
        # 2. Eliminar asignaciones de trivias
        deleted_assignments = db.query(TriviaAssignment).delete()
        
        # 3. Limpiar tabla pivote trivia_questions manualmente
        db.execute(text("DELETE FROM trivia_questions"))
        
        # 4. Eliminar trivias (ahora sin referencias)
        deleted_trivias = db.query(Trivia).delete()
        
        # 5. Eliminar opciones
        deleted_options = db.query(Option).delete()
        
        # 6. Eliminar preguntas
        deleted_questions = db.query(Question).delete()
        
        # 7. Eliminar usuarios PLAYER de testing (mantener admin)
        deleted_users = db.query(User).filter(
            User.role == UserRole.PLAYER,
            User.email.in_([
                "ana@talana.com",
                "beto@talana.com",
                "carla@talana.com",
                "diego@talana.com",
                "elena@talana.com"
            ])
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info("Reset completado exitosamente")
        
        return {
            "message": "Data de testing eliminada",
            "deleted": {
                "users": deleted_users,
                "questions": deleted_questions,
                "options": deleted_options,
                "trivias": deleted_trivias,
                "assignments": deleted_assignments,
                "answers": deleted_answers
            }
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error en reset: {str(e)}")
        raise