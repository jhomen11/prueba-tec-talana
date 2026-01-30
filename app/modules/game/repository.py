from sqlalchemy.orm import Session, joinedload
from app.modules.trivias.models import TriviaAssignment, AssignmentStatus, UserAnswer, Trivia
from app.modules.questions.models import Question, Option, DifficultyLevel

class GameRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_assignment(self, assignment_id: int, user_id: int) -> TriviaAssignment | None:
        """Busca una trivia específica del usuario."""
        return self.db.query(TriviaAssignment).filter(
            TriviaAssignment.id == assignment_id,
            TriviaAssignment.user_id == user_id
        ).first()

    def get_pending_assignments(self, user_id: int):
        """Lista trivias asignadas al usuario."""
        return self.db.query(TriviaAssignment).join(Trivia).filter(
            TriviaAssignment.user_id == user_id,
            TriviaAssignment.status == AssignmentStatus.PENDING
        ).all()

    def get_assignment_with_details(self, assignment_id: int, user_id: int):
        """Carga la Trivia, Preguntas y Opciones para jugar."""
        return self.db.query(TriviaAssignment).options(
            joinedload(TriviaAssignment.trivia)
            .joinedload(Trivia.questions)
            .joinedload(Question.options)
        ).filter(
            TriviaAssignment.id == assignment_id,
            TriviaAssignment.user_id == user_id
        ).first()

    def get_option(self, option_id: int) -> Option | None:
        return self.db.query(Option).filter(Option.id == option_id).first()

    def get_question(self, question_id: int) -> Question | None:
        return self.db.query(Question).filter(Question.id == question_id).first()

    def save_answer(self, answer: UserAnswer):
        self.db.add(answer)

    def complete_assignment(self, assignment: TriviaAssignment, score: int):
        assignment.status = AssignmentStatus.COMPLETED
        assignment.total_score = score
        self.db.add(assignment)
    
    def commit(self):
        """Confirma la transacción actual."""
        self.db.commit()
    
    def rollback(self):
        """Revierte la transacción actual."""
        self.db.rollback()