"""
Esquemas y utilidades para paginación consistente.
"""
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field, ConfigDict
from math import ceil

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta paginada genérica.
    
    Example:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "per_page": 10,
            "total_pages": 10
        }
    """
    items: List[T] = Field(..., description="Lista de elementos en esta página")
    total: int = Field(..., description="Total de elementos en la base de datos")
    page: int = Field(..., description="Número de página actual (1-indexed)")
    per_page: int = Field(..., description="Cantidad de elementos por página")
    total_pages: int = Field(..., description="Total de páginas disponibles")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "per_page": 10,
                "total_pages": 10
            }
        }
    )


def paginate(
    items: List[T],
    total: int,
    page: int = 1,
    per_page: int = 10
) -> PaginatedResponse[T]:
    """
    Helper para crear respuestas paginadas.
    
    Args:
        items: Lista de elementos de la página actual
        total: Total de elementos en la base de datos
        page: Número de página actual (1-indexed)
        per_page: Elementos por página
    
    Returns:
        PaginatedResponse con metadata calculada
    """
    total_pages = ceil(total / per_page) if per_page > 0 else 0
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


def calculate_skip(page: int, per_page: int) -> int:
    """
    Calcula el offset (skip) basado en página y tamaño.
    
    Args:
        page: Número de página (1-indexed)
        per_page: Elementos por página
    
    Returns:
        Offset para la query
    """
    return (page - 1) * per_page
