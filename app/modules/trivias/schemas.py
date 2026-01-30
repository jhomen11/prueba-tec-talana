from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# Base
class TriviaBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Trivia Mensual RRHH"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Evaluación de conocimientos legales"})

# Create: Input del Admin
class TriviaCreate(TriviaBase):
    question_ids: List[int] = Field(..., min_length=1, description="IDs de las preguntas a incluir")
    user_ids: List[int] = Field(..., min_length=1, description="IDs de los usuarios a invitar")

# Update: Campos opcionales
class TriviaUpdate(BaseModel):
    """Schema para actualizar trivias. Todos los campos son opcionales."""
    name: Optional[str] = Field(None, json_schema_extra={"example": "Trivia Actualizada"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Nueva descripción"})
    question_ids: Optional[List[int]] = Field(None, min_length=1, description="Reemplaza las preguntas")

# Response: Lo que devolvemos
class TriviaResponse(TriviaBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)