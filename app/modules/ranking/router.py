from typing import List
from app.modules.users.repository import UserRepository
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user # Cualquier usuario autenticado puede ver el ranking
from app.modules.ranking import schemas
from app.modules.ranking.repository import RankingRepository
from app.modules.ranking.service import RankingService
from app.core.deps import get_current_admin

router = APIRouter(prefix="/ranking", tags=["Stats & Ranking"])

def get_service(db: Session = Depends(get_db)) -> RankingService:
    ranking_repo = RankingRepository(db)
    user_repo = UserRepository(db)
    return RankingService(ranking_repo, user_repo)

@router.get(
    "/global",
    response_model=List[schemas.RankingEntry],
    summary="Obtener Tabla de Posiciones Global",
    description="Muestra los mejores jugadores basados en la suma de puntajes de todas sus trivias completadas."
)
def get_global_ranking(
    limit: int = 10,
    service: RankingService = Depends(get_service),
    current_user = Depends(get_current_user) 
):
    """
    Retorna el TOP 10 (por defecto) de jugadores activos.
    """
    return service.get_top_players(limit)


@router.get(
    "/my-stats",
    response_model=schemas.PlayerStatsResponse,
    summary="Mi Rendimiento"
)
def get_my_stats(
    service: RankingService = Depends(get_service),
    current_user = Depends(get_current_user)
):
    """
    Muestra el historial y estadísticas del usuario logueado.
    """
    return service.get_player_stats(current_user.id)

@router.get(
    "/users/{user_id}",
    response_model=schemas.PlayerStatsResponse,
    summary="Rendimiento de un Jugador (Solo Admin)"
)
def get_user_stats(
    user_id: int,
    service: RankingService = Depends(get_service),
    admin = Depends(get_current_admin)
):
    """
    Permite al administrador auditar el rendimiento de cualquier jugador específico.
    """
    return service.get_player_stats(user_id)