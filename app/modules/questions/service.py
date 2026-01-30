from fastapi import HTTPException
from app.modules.questions.schemas import QuestionCreate, QuestionUpdate
from app.modules.questions.repository import QuestionRepository
from app.core.pagination import paginate, calculate_skip
from sqlalchemy.orm import Session
from app.modules.trivias.models import TriviaAssignment, AssignmentStatus

class QuestionService:
    def __init__(self, repository: QuestionRepository):
        self.repository = repository

    def get_questions(self, page: int = 1, per_page: int = 10):
        """Obtiene preguntas con paginación."""
        skip = calculate_skip(page, per_page)
        items = self.repository.get_all(skip=skip, limit=per_page)
        total = self.repository.count_all()
        return paginate(items, total, page, per_page)
    
    def get_question_by_id(self, question_id: int):
        question = self.repository.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Pregunta no encontrada")
        return question

    def create_question(self, question_data: QuestionCreate):
        # Validar pregunta duplicada
        if self.repository.get_by_text(question_data.text):
            raise HTTPException(
                status_code=409, 
                detail=f"La pregunta '{question_data.text}' ya existe en el sistema."
            )

        # Validar exactamente 1 respuesta correcta
        correct_answers = sum(1 for opt in question_data.options if opt.is_correct)
        
        if correct_answers == 0:
            raise HTTPException(status_code=422, detail="La pregunta debe tener al menos una respuesta correcta.")
        
        if correct_answers > 1:
            raise HTTPException(status_code=422, detail="La pregunta solo puede tener UNA respuesta correcta.")
            
        return self.repository.create(question_data)
    
    def update_question(self, question_id: int, update_data: QuestionUpdate):
        question = self.repository.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Pregunta no encontrada")
        
        # Validar texto único si se actualiza
        if update_data.text:
            existing = self.repository.get_by_text(update_data.text)
            if existing and existing.id != question_id:
                raise HTTPException(status_code=409, detail="Ya existe una pregunta con ese texto")
        
        # Validar opciones si se actualizan
        if update_data.options:
            correct_answers = sum(1 for opt in update_data.options if opt.is_correct)
            if correct_answers == 0:
                raise HTTPException(status_code=422, detail="Debe haber al menos una respuesta correcta")
            if correct_answers > 1:
                raise HTTPException(status_code=422, detail="Solo puede haber UNA respuesta correcta")
        
        return self.repository.update(question, update_data)
    
    def delete_question(self, question_id: int, db: Session):
        """Soft delete con validación de integridad."""
        question = self.repository.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Pregunta no encontrada")
        
        # Validar que no esté en trivias activas
        # Buscamos trivias con esta pregunta que tengan assignments pendientes
        from app.modules.trivias.models import Trivia, trivia_questions
        active_trivias = db.query(Trivia).join(
            trivia_questions, Trivia.id == trivia_questions.c.trivia_id
        ).join(
            TriviaAssignment, Trivia.id == TriviaAssignment.trivia_id
        ).filter(
            trivia_questions.c.question_id == question_id,
            Trivia.is_active == True,
            TriviaAssignment.status == AssignmentStatus.PENDING
        ).count()
        
        if active_trivias > 0:
            raise HTTPException(
                status_code=409,
                detail=f"No se puede eliminar pregunta usada en {active_trivias} trivia(s) activa(s)"
            )
        
        return self.repository.soft_delete(question)