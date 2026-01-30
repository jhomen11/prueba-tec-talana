import enum
from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.models import IDMixin, TimestampMixin, SoftDeleteMixin

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PLAYER = "player"

class User(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PLAYER, nullable=False)

    # Relaciones (se activarán cuando creemos el módulo de Trivias)
    # assignments = relationship("TriviaAssignment", back_populates="user")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"