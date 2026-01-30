import enum
from sqlalchemy import Column, String, Enum, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.models import IDMixin, TimestampMixin, SoftDeleteMixin

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"     # 1 punto
    MEDIUM = "medium" # 2 puntos
    HARD = "hard"     # 3 puntos

# Preguntas
class Question(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "questions"

    text = Column(String, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    
    # Relación One-to-Many: Una pregunta tiene muchas opciones
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")

#  Opciones de respuesta para las preguntas
class Option(Base, IDMixin):
    __tablename__ = "options"

    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False) # Solo una debe ser True [cite: 29]
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    question = relationship("Question", back_populates="options")