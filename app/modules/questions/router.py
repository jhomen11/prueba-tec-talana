from typing import List
from app.core.deps import get_current_admin
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.pagination import PaginatedResponse
from app.modules.questions import schemas
from app.modules.questions.repository import QuestionRepository
from app.modules.questions.service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])

# Factory de Dependencias
def get_service(db: Session = Depends(get_db)) -> QuestionService:
    repository = QuestionRepository(db)
    return QuestionService(repository)

@router.get(
    "/",
    response_model=PaginatedResponse[schemas.QuestionResponse],
    summary="Listar preguntas",
    responses={
        200: {"description": "Lista de preguntas obtenida exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def list_questions(
    page: int = Query(1, ge=1, description="Número de página (1-indexed)"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    service: QuestionService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """Lista todas las preguntas con paginación."""
    return service.get_questions(page=page, per_page=per_page)

@router.post(
    "/",
    response_model=schemas.QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pregunta",
    responses={
        201: {"description": "Pregunta creada exitosamente"},
        409: {"description": "La pregunta ya existe"},
        422: {"description": "Validación fallida (debe tener exactamente 1 respuesta correcta)"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def create_question(
    question: schemas.QuestionCreate, 
    service: QuestionService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """
    Crea una pregunta con sus opciones.
    Valida que exista exactamente una respuesta correcta.

    Difficulty (opciones):
      - easy: 1 punto
      - medium: 2 puntos
      - hard: 3 puntos
    """
@router.get(
    "/{question_id}",
    response_model=schemas.QuestionResponse,
    summary="Obtener pregunta por ID",
    responses={
        200: {"description": "Pregunta encontrada"},
        404: {"description": "Pregunta no encontrada"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def get_question(
    question_id: int,
    service: QuestionService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """Obtiene una pregunta específica por ID."""
    return service.get_question_by_id(question_id)

@router.put(
    "/{question_id}",
    response_model=schemas.QuestionResponse,
    summary="Actualizar pregunta",
    responses={
        200: {"description": "Pregunta actualizada exitosamente"},
        404: {"description": "Pregunta no encontrada"},
        409: {"description": "Ya existe una pregunta con ese texto"},
        422: {"description": "Validación fallida (debe tener exactamente 1 respuesta correcta)"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def update_question(
    question_id: int,
    update_data: schemas.QuestionUpdate,
    service: QuestionService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """
    Actualiza una pregunta. Todos los campos son opcionales.
    Si se actualizan opciones, se reemplazan todas las anteriores.
    """
    return service.update_question(question_id, update_data)

@router.delete(
    "/{question_id}",
    response_model=schemas.QuestionResponse,
    summary="Eliminar pregunta (soft delete)",
    responses={
        200: {"description": "Pregunta eliminada exitosamente"},
        404: {"description": "Pregunta no encontrada"},
        409: {"description": "Pregunta usada en trivias activas"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    service: QuestionService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """
    Elimina una pregunta (soft delete). Solo admin.
    Valida que no esté en trivias activas antes de eliminar.
    """
    return service.delete_question(question_id, db)