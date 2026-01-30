from app.modules.ranking.repository import RankingRepository
from app.modules.ranking.schemas import PlayerStatsResponse, RankingEntry
from app.modules.users.repository import UserRepository
from fastapi import HTTPException

class RankingService:
    def __init__(self, repository: RankingRepository, user_repo: UserRepository):
        self.repository = repository
        self.user_repo = user_repo

    def get_top_players(self, limit: int = 10):
        
        data = self.repository.get_global_ranking(limit)
        
        results = []
        for index, row in enumerate(data):
            
            results.append(RankingEntry(
                position=index + 1,
                player_name=row.full_name,
                total_score=row.total_score or 0,
                trivias_played=row.trivias_played
            ))
            
        return results
    
    def get_player_stats(self, user_id: int) -> PlayerStatsResponse:
        # 1. Obtener datos del usuario
        user = self.user_repo.get_by_id(user_id)
        if not user:
             raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # 2. Obtener historial de partidas
        assignments = self.repository.get_user_performance(user_id)
        
        # 3. Calcular métricas
        total_score = sum(a.total_score for a in assignments)
        count = len(assignments)
        average = round(total_score / count, 1) if count > 0 else 0.0
        
        # 4. Formatear historial
        history = [
            {
                "trivia_name": a.trivia.name,
                "score": a.total_score,
                "played_at": a.updated_at or a.created_at
            }
            for a in assignments
        ]

        return PlayerStatsResponse(
            player_name=user.full_name,
            total_score=total_score,
            trivias_played=count,
            average_score=average,
            history=history
        )