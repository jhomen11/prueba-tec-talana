from sqlalchemy.orm import Session
from sqlalchemy import func
from app.modules.questions.models import Question, Option
from app.modules.questions.schemas import QuestionCreate, QuestionUpdate
from typing import Optional

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False):
        query = self.db.query(Question)
        if not include_deleted:
            query = query.filter(Question.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    def count_all(self, include_deleted: bool = False) -> int:
        """Cuenta el total de preguntas."""
        query = self.db.query(Question)
        if not include_deleted:
            query = query.filter(Question.is_active == True)
        return query.count()
    
    def get_by_id(self, question_id: int, include_deleted: bool = False) -> Question | None:
        query = self.db.query(Question).filter(Question.id == question_id)
        if not include_deleted:
            query = query.filter(Question.is_active == True)
        return query.first()

    def get_by_text(self, text: str, include_deleted: bool = False) -> Question | None:
        """
        Busca una pregunta ignorando mayúsculas/minúsculas y espacios.
        Ej: "HOLA" encuentra "Hola "
        """
        search_text = text.strip().lower()
        query = self.db.query(Question).filter(
            func.lower(Question.text) == search_text
        )
        if not include_deleted:
            query = query.filter(Question.is_active == True)
        return query.first()

    def create(self, question_data: QuestionCreate) -> Question:
        clean_text = question_data.text.strip()
        
        db_question = Question(
            text=clean_text, 
            difficulty=question_data.difficulty
        )
        self.db.add(db_question)
        self.db.flush()
        
        for opt in question_data.options:
            db_option = Option(
                text=opt.text.strip(),
                is_correct=opt.is_correct,
                question_id=db_question.id
            )
            self.db.add(db_option)
            
        self.db.commit()
        self.db.refresh(db_question)
        return db_question
    
    def update(self, question: Question, update_data: QuestionUpdate) -> Question:
        """Actualiza solo los campos proporcionados."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Si se actualizan opciones, eliminar las anteriores y crear nuevas
        if 'options' in update_dict and update_dict['options']:
            # Eliminar opciones anteriores
            self.db.query(Option).filter(Option.question_id == question.id).delete()
            
            # Crear nuevas opciones
            for opt_data in update_dict.pop('options'):
                db_option = Option(
                    text=opt_data.text.strip(),
                    is_correct=opt_data.is_correct,
                    question_id=question.id
                )
                self.db.add(db_option)
        
        # Actualizar campos restantes
        for field, value in update_dict.items():
            if field == 'text':
                value = value.strip()
            setattr(question, field, value)
        
        self.db.commit()
        self.db.refresh(question)
        return question
    
    def soft_delete(self, question: Question) -> Question:
        """Marca la pregunta como eliminada (soft delete)."""
        question.soft_delete()
        self.db.commit()
        self.db.refresh(question)
        return question