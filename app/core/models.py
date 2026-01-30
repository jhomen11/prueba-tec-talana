from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import func

class TimestampMixin:
    # Mixin para añadir timestamps de creación y actualización automáticos.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class IDMixin:
    # Mixin para añadir ID estandarizado.
    id = Column(Integer, primary_key=True, index=True)

class SoftDeleteMixin:
    """
    Mixin para implementar soft delete (borrado lógico).
    Los registros no se eliminan de la DB, solo se marcan como inactivos.
    """
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        """Marca el registro como eliminado."""
        self.is_active = False
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restaura un registro eliminado."""
        self.is_active = True
        self.deleted_at = None