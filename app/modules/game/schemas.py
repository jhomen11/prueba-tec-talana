from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.modules.trivias.models import AssignmentStatus

# --- Para listar trivias pendientes ---
class MyTriviaResponse(BaseModel):
    id: int = Field(..., description="ID de la asignación (Úsalo para jugar)")
    trivia_name: str = Field(..., description="Nombre de la Trivia")
    status: AssignmentStatus = Field(..., description="Estado actual (pending/completed)")
    
    model_config = ConfigDict(from_attributes=True)

# --- Para jugar (Ver preguntas) ---
class GameOption(BaseModel):
    id: int
    text: str

class GameQuestion(BaseModel):
    id: int
    text: str
    options: List[GameOption]

class GamePlayResponse(BaseModel):
    assignment_id: int
    trivia_name: str
    questions: List[GameQuestion]

# --- INPUT: Para enviar respuestas (¡Aquí está la mejora clave!) ---
class AnswerSubmit(BaseModel):
    question_id: int = Field(..., description="ID de la pregunta que se responde", json_schema_extra={"example": 1})
    option_id: int = Field(..., description="ID de la opción seleccionada por el usuario", json_schema_extra={"example": 2})

class GameSubmission(BaseModel):
    answers: List[AnswerSubmit]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answers": [
                    {
                        "question_id": 1,
                        "option_id": 5
                    },
                    {
                        "question_id": 2,
                        "option_id": 9
                    }
                ]
            }
        }
    )

# --- OUTPUT: Resultado final ---
class GameResult(BaseModel):
    total_score: int = Field(..., description="Puntaje total obtenido (suma de dificultades)")
    correct_count: int = Field(..., description="Cantidad de respuestas correctas")
    message: str