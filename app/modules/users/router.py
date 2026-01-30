from app.core.deps import get_current_admin, get_current_user
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.pagination import PaginatedResponse
from app.modules.users import schemas
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService
from app.core.logger import LoggerSetup
from app.modules.users.schemas import UserSignup
from app.modules.users.models import User

router = APIRouter(prefix="/users", tags=["Users"])
logger = LoggerSetup.get_logger(__name__)

# Inyección de Dependencias
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)

@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: schemas.UserSignup,
    service: UserService = Depends(get_user_service)
):
    """
    Registro público de nuevos jugadores.
    * No requiere autenticación.
    * El usuario siempre se crea con rol **PLAYER**.
    """
    return service.register_player(user_data)

@router.get(
    "/",
    response_model=PaginatedResponse[schemas.UserResponse],
    summary="Listar usuarios",
    responses={
        200: {"description": "Lista de usuarios obtenida exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def list_users(
    page: int = Query(1, ge=1, description="Número de página (1-indexed)"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    service: UserService = Depends(get_user_service),
    current_admin = Depends(get_current_admin)
):
    """Lista todos los usuarios con paginación (solo activos)."""
    return service.get_all_users(page=page, per_page=per_page)

@router.get(
    "/deleted",
    response_model=List[schemas.UserResponse],
    summary="Listar usuarios eliminados",
    responses={
        200: {"description": "Lista de usuarios eliminados"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def list_deleted_users(
    service: UserService = Depends(get_user_service),
    current_admin = Depends(get_current_admin)
):
    """Lista SOLO usuarios eliminados (is_active=False) sin paginación."""
    return service.get_deleted_users()

@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Obtener usuario por ID",
    responses={
        200: {"description": "Usuario encontrado"},
        404: {"description": "Usuario no encontrado"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos"}
    }
)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """Obtiene un usuario por ID. Admin puede ver cualquiera, usuario normal solo sí mismo."""
    user = service.get_user_by_id(user_id)
    
    # Validar permisos: admin o el propio usuario
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este usuario")
    
    return user

@router.post(
    "/", 
    response_model=schemas.UserResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Crear usuario administrativo (Solo Admin)",
    responses={
        201: {"description": "Usuario creado exitosamente"},
        409: {"description": "Email ya registrado"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def create_user(
    user: schemas.UserCreate, 
    service: UserService = Depends(get_user_service),
    current_admin = Depends(get_current_admin)
):
    """
    Endpoint exclusivo para administradores. Permite crear usuarios con cualquier rol.
    
    ### Permisos
    * Requiere estar autenticado.
    * Requiere tener el rol **ADMIN**.

    ### Funcionalidad
    * A diferencia del registro público (`/signup`), aquí **SÍ** puedes especificar el rol (`admin` o `player`) en el JSON.
    * Para crear otros administradores o dar de alta usuarios manualmente.
    """
    logger.info(f"Registrando usuario: {user.email} con rol: {user.role}")
    
    try:
        new_user = service.create_user(user)
        logger.info(f"Usuario creado ID: {new_user.id}")
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Actualizar usuario",
    responses={
        200: {"description": "Usuario actualizado exitosamente"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "Email ya en uso"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos"}
    }
)
def update_user(
    user_id: int,
    update_data: schemas.UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un usuario. Admin puede actualizar cualquiera, usuario normal solo sí mismo.
    Solo admin puede cambiar roles.
    """
    # Validar permisos
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para actualizar este usuario")
    
    # Solo admin puede cambiar roles
    if update_data.role and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden cambiar roles")
    
    return service.update_user(user_id, update_data)

@router.delete(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Eliminar usuario (soft delete)",
    responses={
        200: {"description": "Usuario eliminado exitosamente"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "Usuario tiene trivias pendientes"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
    current_admin = Depends(get_current_admin)
):
    """
    Elimina un usuario (soft delete). Solo admin.
    Valida que no tenga trivias pendientes antes de eliminar.
    """
    return service.delete_user(user_id, db)

@router.put(
    "/{user_id}/restore",
    response_model=schemas.UserResponse,
    summary="Restaurar usuario eliminado",
    responses={
        200: {"description": "Usuario restaurado exitosamente"},
        404: {"description": "Usuario no encontrado"},
        400: {"description": "El usuario no está eliminado"},
        401: {"description": "No autenticado"},
        403: {"description": "No tienes permisos de administrador"}
    }
)
def restore_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_admin = Depends(get_current_admin)
):
    """Restaura un usuario que fue eliminado (soft delete). Solo admin."""
    return service.restore_user(user_id)