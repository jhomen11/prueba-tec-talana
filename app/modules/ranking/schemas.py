from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List

class RankingEntry(BaseModel):
    position: int = Field(..., description="Lugar en el ranking (1, 2, 3...)")
    player_name: str = Field(..., description="Nombre del jugador")
    total_score: int = Field(..., description="Suma total de puntos de todas las trivias completadas")
    trivias_played: int = Field(..., description="Cantidad de trivias finalizadas")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "position": 1,
                "player_name": "Beto Player",
                "total_score": 150,
                "trivias_played": 3
            }
        }
    )
 

# Detalle de una partida jugada        
class MatchHistoryItem(BaseModel):
    trivia_name: str
    score: int
    played_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Reporte completo del jugador
class PlayerStatsResponse(BaseModel):
    player_name: str
    total_score: int
    trivias_played: int
    average_score: float
    history: List[MatchHistoryItem]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_name": "Beto Player",
                "total_score": 150,
                "trivias_played": 3,
                "average_score": 50.0,
                "history": [
                    {"trivia_name": "Mix Laboral", "score": 50, "played_at": "2026-01-29T10:00:00"}
                ]
            }
        }
    )