from app.core.security import get_password_hash
from app.modules.users.models import UserRole
from app.modules.users.schemas import UserCreate, UserSignup, UserUpdate
from app.modules.users.repository import BaseUserRepository
from app.core.pagination import paginate, calculate_skip
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.modules.trivias.models import TriviaAssignment, AssignmentStatus

class UserService:
    def __init__(self, repository: BaseUserRepository):
        self.repository = repository

    def get_user_by_email(self, email: str):
        return self.repository.get_by_email(email)
    
    def get_all_users(self, page: int = 1, per_page: int = 10, include_deleted: bool = False):
        """Obtiene usuarios con paginación."""
        skip = calculate_skip(page, per_page)
        items = self.repository.get_all(skip=skip, limit=per_page, include_deleted=include_deleted)
        total = self.repository.count_all(include_deleted=include_deleted)
        return paginate(items, total, page, per_page)
    
    def get_deleted_users(self):
        """Obtiene SOLO usuarios eliminados (sin paginación)."""
        return self.repository.get_all_deleted()
    
    def get_user_by_id(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    def create_user(self, user: UserCreate):
        # Validar email único
        if self.repository.get_by_email(user.email):
            raise HTTPException(status_code=409, detail="El email ya está registrado")
        
        hashed_pwd = get_password_hash(user.password)
        return self.repository.create(user, hashed_pwd)
    
    def update_user(self, user_id: int, update_data: UserUpdate):
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Validar email único si se está actualizando
        if update_data.email:
            existing = self.repository.get_by_email(update_data.email)
            if existing and existing.id != user_id:
                raise HTTPException(status_code=409, detail="El email ya está en uso")
        
        # Hashear nueva contraseña si se proporciona
        hashed_pwd = None
        if update_data.password:
            hashed_pwd = get_password_hash(update_data.password)
        
        return self.repository.update(user, update_data, hashed_pwd)
    
    def delete_user(self, user_id: int, db: Session):
        """Soft delete con validación de integridad."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Validar que no tenga trivias pendientes
        pending_trivias = db.query(TriviaAssignment).filter(
            TriviaAssignment.user_id == user_id,
            TriviaAssignment.status == AssignmentStatus.PENDING
        ).count()
        
        if pending_trivias > 0:
            raise HTTPException(
                status_code=409,
                detail=f"No se puede eliminar usuario con {pending_trivias} trivia(s) pendiente(s)"
            )
        
        return self.repository.soft_delete(user)
    
    def restore_user(self, user_id: int):
        """Restaura un usuario eliminado."""
        user = self.repository.get_by_id(user_id, include_deleted=True)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if user.is_active:
            raise HTTPException(status_code=400, detail="El usuario no está eliminado")
        
        return self.repository.restore(user)
    
    def register_player(self, signup_data: UserSignup):
        if self.repository.get_by_email(signup_data.email):
             raise HTTPException(status_code=409, detail="El email ya está registrado")

        secure_user_data = UserCreate(
            full_name=signup_data.full_name,
            email=signup_data.email,
            password=signup_data.password,
            role=UserRole.PLAYER
        )
        
        hashed_pwd = get_password_hash(secure_user_data.password)
        return self.repository.create(secure_user_data, hashed_pwd)