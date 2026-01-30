from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.modules.users.models import UserRole

# Base: Campos comunes
class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, json_schema_extra={"example": "Jhonny Mendoza"})
    email: EmailStr = Field(..., json_schema_extra={"example": "jhonny@correo.com"})
    role: UserRole = Field(default=UserRole.ADMIN, json_schema_extra={"example": "admin"})

# Create: Input del cliente
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, json_schema_extra={"example": "secret123"})

# Update: Campos opcionales para actualización
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, json_schema_extra={"example": "Jhonny Mendoza"})
    email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "jhonny@correo.com"})
    password: Optional[str] = Field(None, min_length=6, json_schema_extra={"example": "newsecret123"})
    role: Optional[UserRole] = Field(None, json_schema_extra={"example": "player"})

# Response: Output de la API
class UserResponse(UserBase):
    id: int
    created_at: datetime
    # role ya viene heredado de UserBase

    model_config = ConfigDict(from_attributes=True)

# Signup: Registro público de usuarios     
class UserSignup(BaseModel):
    full_name: str = Field(..., min_length=3, json_schema_extra={"example": "Juan Perez"})
    email: EmailStr = Field(..., json_schema_extra={"example": "juan@gmail.com"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "secret123"})