from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.modules.questions.models import DifficultyLevel

# --- Options ---
class OptionBase(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "Respuesta A"})

class OptionCreate(OptionBase):
    is_correct: bool = Field(False, description="Marca si esta es la opción correcta")

class OptionResponse(OptionBase):
    id: int
    # Nota: En el futuro, para el jugador, ocultaremos 'is_correct'.
    # Pero para este endpoint de gestión (Admin), necesitamos verlo.
    is_correct: bool 

    model_config = ConfigDict(from_attributes=True)

# --- Questions ---
class QuestionBase(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "¿Cuál es la capital de Chile?"})
    difficulty: DifficultyLevel = Field(..., json_schema_extra={"example": "easy"})

class QuestionCreate(QuestionBase):
    # Nested Write: Recibimos las opciones junto con la pregunta
    options: List[OptionCreate] = Field(..., min_length=2, description="Mínimo 2 opciones")

class QuestionUpdate(BaseModel):
    """Schema para actualizar preguntas. Todos los campos son opcionales."""
    text: Optional[str] = Field(None, json_schema_extra={"example": "¿Cuál es la capital de Perú?"})
    difficulty: Optional[DifficultyLevel] = Field(None, json_schema_extra={"example": "medium"})
    options: Optional[List[OptionCreate]] = Field(None, min_length=2, description="Reemplaza todas las opciones")

class QuestionResponse(QuestionBase):
    id: int
    options: List[OptionResponse]

    model_config = ConfigDict(from_attributes=True)