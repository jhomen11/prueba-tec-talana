from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserUpdate
from typing import Optional

# Interfaz
class BaseUserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str, include_deleted: bool = False) -> User | None:
        pass

    @abstractmethod
    def create(self, user_data: UserCreate, hashed_password: str) -> User:
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False):
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int, include_deleted: bool = False) -> User | None:
        pass
    
    @abstractmethod
    def update(self, user: User, update_data: UserUpdate, hashed_password: Optional[str] = None) -> User:
        pass
    
    @abstractmethod
    def soft_delete(self, user: User) -> User:
        pass

# SQL
class UserRepository(BaseUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str, include_deleted: bool = False) -> User | None:
        query = self.db.query(User).filter(User.email == email)
        if not include_deleted:
            query = query.filter(User.is_active == True)
        return query.first()
    
    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False):
        query = self.db.query(User)
        if not include_deleted:
            query = query.filter(User.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    def count_all(self, include_deleted: bool = False) -> int:
        """Cuenta el total de usuarios."""
        query = self.db.query(User)
        if not include_deleted:
            query = query.filter(User.is_active == True)
        return query.count()
    
    def get_all_deleted(self):
        """Obtiene TODOS los usuarios eliminados (is_active=False) sin paginación."""
        return self.db.query(User).filter(User.is_active == False).all()
    
    def get_by_id(self, user_id: int, include_deleted: bool = False) -> User | None:
        query = self.db.query(User).filter(User.id == user_id)
        if not include_deleted:
            query = query.filter(User.is_active == True)
        return query.first()

    def create(self, user_data: UserCreate, hashed_password) -> User:
        db_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            role=user_data.role,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update(self, user: User, update_data: UserUpdate, hashed_password: Optional[str] = None) -> User:
        """Actualiza solo los campos proporcionados."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            if field != 'password':  # Password se maneja aparte
                setattr(user, field, value)
        
        if hashed_password:
            user.hashed_password = hashed_password
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def soft_delete(self, user: User) -> User:
        """Marca el usuario como eliminado (soft delete)."""
        user.soft_delete()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def restore(self, user: User) -> User:
        """Restaura un usuario eliminado."""
        user.restore()
        self.db.commit()
        self.db.refresh(user)
        return user