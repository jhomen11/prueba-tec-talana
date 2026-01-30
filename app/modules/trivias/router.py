from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_admin
from app.core.pagination import PaginatedResponse
from app.modules.trivias import schemas
from app.modules.trivias.repository import TriviaRepository
from app.modules.trivias.service import TriviaService

router = APIRouter(prefix="/trivias", tags=["Trivias"])

def get_service(db: Session = Depends(get_db)) -> TriviaService:
    repository = TriviaRepository(db)
    return TriviaService(repository)

@router.post(
    "/",
    response_model=schemas.TriviaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear trivia",
    responses={
        201: {"description": "Trivia creada y asignada exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"},
        422: {"description": "IDs de preguntas o usuarios inválidos"}
    }
)
def create_trivia(
    trivia: schemas.TriviaCreate, 
    service: TriviaService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """
    Crea una trivia, selecciona preguntas y asigna usuarios.
    
    Requiere:
    - Lista de IDs de preguntas existentes
    - Lista de IDs de usuarios a asignar
    """
    return service.create_trivia(trivia)

@router.get(
    "/{trivia_id}",
    response_model=schemas.TriviaResponse,
    summary="Obtener trivia por ID",
    responses={
        200: {"description": "Trivia encontrada"},
        404: {"description": "Trivia no encontrada"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def get_trivia(
    trivia_id: int,
    service: TriviaService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """Obtiene una trivia específica por ID."""
    return service.get_trivia_by_id(trivia_id)

@router.put(
    "/{trivia_id}",
    response_model=schemas.TriviaResponse,
    summary="Actualizar trivia",
    responses={
        200: {"description": "Trivia actualizada exitosamente"},
        404: {"description": "Trivia no encontrada"},
        422: {"description": "IDs de preguntas inválidos"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def update_trivia(
    trivia_id: int,
    update_data: schemas.TriviaUpdate,
    service: TriviaService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """
    Actualiza una trivia. Todos los campos son opcionales.
    Si se actualizan preguntas, se reemplazan todas las anteriores.
    """
    return service.update_trivia(trivia_id, update_data)

@router.delete(
    "/{trivia_id}",
    response_model=schemas.TriviaResponse,
    summary="Eliminar trivia (soft delete)",
    responses={
        200: {"description": "Trivia eliminada exitosamente"},
        404: {"description": "Trivia no encontrada"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def delete_trivia(
    trivia_id: int,
    service: TriviaService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """
    Elimina una trivia (soft delete). Solo admin.
    Automáticamente cancela los assignments pendientes.
    """
    return service.delete_trivia(trivia_id)

@router.get(
    "/",
    response_model=PaginatedResponse[schemas.TriviaResponse],
    summary="Listar trivias",
    responses={
        200: {"description": "Lista de trivias obtenida exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def list_trivias(
    page: int = Query(1, ge=1, description="Número de página (1-indexed)"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    service: TriviaService = Depends(get_service),
    current_admin = Depends(get_current_admin)
):
    """Lista todas las trivias con paginación."""
    return service.get_trivias(page=page, per_page=per_page)