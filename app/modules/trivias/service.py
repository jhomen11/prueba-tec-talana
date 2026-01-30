from fastapi import HTTPException
from app.modules.trivias.schemas import TriviaCreate, TriviaUpdate
from app.modules.trivias.repository import TriviaRepository
from app.core.pagination import paginate, calculate_skip

class TriviaService:
    def __init__(self, repository: TriviaRepository):
        self.repository = repository

    def create_trivia(self, trivia_data: TriviaCreate):
        # Aquí podrías validar: len(found_questions) == len(input_ids)
        return self.repository.create(trivia_data)

    def get_trivias(self, page: int = 1, per_page: int = 10):
        """Obtiene trivias con paginación."""
        skip = calculate_skip(page, per_page)
        items = self.repository.get_all(skip=skip, limit=per_page)
        total = self.repository.count_all()
        return paginate(items, total, page, per_page)
    
    def get_trivia_by_id(self, trivia_id: int):
        trivia = self.repository.get_by_id(trivia_id)
        if not trivia:
            raise HTTPException(status_code=404, detail="Trivia no encontrada")
        return trivia
    
    def update_trivia(self, trivia_id: int, update_data: TriviaUpdate):
        trivia = self.repository.get_by_id(trivia_id)
        if not trivia:
            raise HTTPException(status_code=404, detail="Trivia no encontrada")
        
        return self.repository.update(trivia, update_data)
    
    def delete_trivia(self, trivia_id: int):
        """Soft delete - cancela assignments pendientes automáticamente."""
        trivia = self.repository.get_by_id(trivia_id)
        if not trivia:
            raise HTTPException(status_code=404, detail="Trivia no encontrada")
        
        return self.repository.soft_delete(trivia)