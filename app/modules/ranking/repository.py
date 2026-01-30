from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from app.modules.users.models import User
from app.modules.trivias.models import TriviaAssignment, AssignmentStatus

class RankingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_global_ranking(self, limit: int = 10):
        """
        Calcula el puntaje total sumando todas las asignaciones COMPLETADAS.
        Filtra a los usuarios eliminados (Soft Delete).
        """
        return self.db.query(
            User.full_name,
            func.sum(TriviaAssignment.total_score).label("total_score"),
            func.count(TriviaAssignment.id).label("trivias_played")
        ).join(
            TriviaAssignment, User.id == TriviaAssignment.user_id
        ).filter(
            TriviaAssignment.status == AssignmentStatus.COMPLETED,
            User.is_active == True,   
            User.role == "player"     
        ).group_by(
            User.id
        ).order_by(
            desc("total_score")   
        ).limit(limit).all()
        
    
    def get_user_performance(self, user_id: int):
        """
        Obtiene todas las partidas completadas de un usuario específico.
        Carga la relación con Trivia para obtener el nombre.
        """
        return self.db.query(TriviaAssignment).options(
            joinedload(TriviaAssignment.trivia)
        ).filter(
            TriviaAssignment.user_id == user_id,
            TriviaAssignment.status == AssignmentStatus.COMPLETED
        ).order_by(
            TriviaAssignment.updated_at.desc()
        ).all()