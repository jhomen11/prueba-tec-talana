from typing import List
from sqlalchemy.orm import Session
from app.modules.trivias.models import Trivia, TriviaAssignment, AssignmentStatus
from app.modules.trivias.schemas import TriviaCreate, TriviaUpdate
from app.modules.questions.models import Question
from app.modules.users.models import User

class TriviaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, trivia_data: TriviaCreate) -> Trivia:
        db_trivia = Trivia(
            name=trivia_data.name,
            description=trivia_data.description
        )
        
        # Buscar y asociar PREGUNTAS activas
        questions = self.db.query(Question).filter(
            Question.id.in_(trivia_data.question_ids),
            Question.is_active == True
        ).all()
        db_trivia.questions = questions 
        
        self.db.add(db_trivia)
        self.db.flush() 
        
        # Crear ASIGNACIONES para usuarios activos
        active_users = self.db.query(User).filter(
            User.id.in_(trivia_data.user_ids),
            User.is_active == True
        ).all()
        
        for user in active_users:
            assignment = TriviaAssignment(
                trivia_id=db_trivia.id,
                user_id=user.id,
                status=AssignmentStatus.PENDING,
                total_score=0
            )
            self.db.add(assignment)
            
        self.db.commit()
        self.db.refresh(db_trivia)
        return db_trivia

    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False):
        query = self.db.query(Trivia)
        if not include_deleted:
            query = query.filter(Trivia.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    def count_all(self, include_deleted: bool = False) -> int:
        """Cuenta el total de trivias."""
        query = self.db.query(Trivia)
        if not include_deleted:
            query = query.filter(Trivia.is_active == True)
        return query.count()
    
    def get_by_id(self, trivia_id: int, include_deleted: bool = False) -> Trivia | None:
        query = self.db.query(Trivia).filter(Trivia.id == trivia_id)
        if not include_deleted:
            query = query.filter(Trivia.is_active == True)
        return query.first()
    
    def update(self, trivia: Trivia, update_data: TriviaUpdate) -> Trivia:
        """Actualiza solo los campos proporcionados."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Si se actualizan preguntas, reemplazar las anteriores
        if 'question_ids' in update_dict and update_dict['question_ids']:
            questions = self.db.query(Question).filter(
                Question.id.in_(update_dict.pop('question_ids')),
                Question.is_active == True
            ).all()
            trivia.questions = questions
        
        # Actualizar campos restantes
        for field, value in update_dict.items():
            setattr(trivia, field, value)
        
        self.db.commit()
        self.db.refresh(trivia)
        return trivia
    
    def soft_delete(self, trivia: Trivia) -> Trivia:
        """Marca la trivia como eliminada y cancela assignments pendientes."""
        trivia.soft_delete()
        
        # Cancelar assignments pendientes
        self.db.query(TriviaAssignment).filter(
            TriviaAssignment.trivia_id == trivia.id,
            TriviaAssignment.status == AssignmentStatus.PENDING
        ).update({"status": AssignmentStatus.CANCELLED})
        
        self.db.commit()
        self.db.refresh(trivia)
        return trivia