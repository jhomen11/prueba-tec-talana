import enum
from sqlalchemy import Column, String, ForeignKey, Integer, Table, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.models import IDMixin, TimestampMixin, SoftDeleteMixin
from app.modules.questions.models import Option

# Tabla Pivote: Relación N-a-N entre Trivias y Preguntas
trivia_questions = Table(
    "trivia_questions",
    Base.metadata,
    Column("trivia_id", Integer, ForeignKey("trivias.id"), primary_key=True),
    Column("question_id", Integer, ForeignKey("questions.id"), primary_key=True)
)

class AssignmentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"  # Nuevo estado para trivias eliminadas

class Trivia(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "trivias"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Relación N-a-N: Una trivia tiene muchas preguntas seleccionadas [cite: 33]
    questions = relationship("Question", secondary=trivia_questions, backref="trivias")
    
    # Relación con las asignaciones de usuarios
    assignments = relationship("TriviaAssignment", back_populates="trivia")

class TriviaAssignment(Base, IDMixin, TimestampMixin):
    """
    Representa la participación de un usuario en una trivia específica.
    Aquí guardaremos el puntaje final para el Ranking[cite: 38].
    """
    __tablename__ = "trivia_assignments"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trivia_id = Column(Integer, ForeignKey("trivias.id"), nullable=False)
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.PENDING)
    total_score = Column(Integer, default=0) # Se calcula al finalizar

    # Relaciones
    user = relationship("User", backref="assignments") # Backref simple para no modificar User model ahora
    trivia = relationship("Trivia", back_populates="assignments")
    
    
class UserAnswer(Base, IDMixin, TimestampMixin):
    """
    Guarda cada respuesta individual de un usuario en una trivia.
    Permite auditar qué respondió y calcular el puntaje.
    """
    __tablename__ = "user_answers"

    assignment_id = Column(Integer, ForeignKey("trivia_assignments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=False)
    
    # Guardamos estos valores calculados para "congelar" el estado del juego
    is_correct = Column(Boolean, nullable=False)
    points_awarded = Column(Integer, default=0, nullable=False)

    # Relación
    assignment = relationship("TriviaAssignment", backref="answers")