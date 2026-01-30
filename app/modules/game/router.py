from typing import List
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.users.models import User
from app.modules.game import schemas
from app.modules.game.repository import GameRepository
from app.modules.game.service import GameService

router = APIRouter(prefix="/game", tags=["Game (Jugadores)"])

def get_service(db: Session = Depends(get_db)) -> GameService:
    return GameService(GameRepository(db))

@router.get(
    "/my-trivias", 
    response_model=List[schemas.MyTriviaResponse],
    summary="Listar mis trivias pendientes"
)
def list_my_pending_trivias(
    current_user: User = Depends(get_current_user),
    service: GameService = Depends(get_service)
):
    """
    Devuelve la lista de trivias asignadas que el usuario aún debe responder.
    Usa el `id` de la respuesta para invocar los endpoints de juego.
    """
    return service.get_my_trivias(current_user.id)

@router.get(
    "/{assignment_id}/play", 
    response_model=schemas.GamePlayResponse,
    summary="Obtener el examen (Preguntas y Opciones)"
)
def get_trivia_content(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    service: GameService = Depends(get_service)
):
    """
    Descarga las preguntas y opciones para una trivia específica.
    * **Nota:** El campo `is_correct` se oculta intencionalmente.
    """
    return service.get_game_details(assignment_id, current_user.id)

# --- AQUÍ ESTÁ EL CAMBIO IMPORTANTE ---
@router.post(
    "/{assignment_id}/submit", 
    response_model=schemas.GameResult,
    summary="Enviar respuestas y finalizar",
    status_code=200
)
def submit_trivia(
    assignment_id: int,
    submission: schemas.GameSubmission,
    current_user: User = Depends(get_current_user),
    service: GameService = Depends(get_service)
):
    """
    Recibe las respuestas del usuario, calcula el puntaje y cierra la trivia.

    ### Payload Requerido (Lo que debes enviar)
    Debes enviar un JSON con una lista llamada `answers`. Cada elemento de la lista conecta una pregunta con su opción seleccionada.

    **Estructura exacta:**
    ```json
    {
      "answers": [
        {
          "question_id": 12,  // ID de la pregunta (Integer)
          "option_id": 45     // ID de la opción elegida (Integer)
        },
        {
          "question_id": 13,
          "option_id": 48
        }
      ]
    }
    ```

    ### Reglas:
    1. **Una sola vez:** Una vez enviadas, la trivia pasa a estado `COMPLETED` y no se puede editar.
    2. **Validación:** Si envías un ID de pregunta que no pertenece a esta trivia, esa respuesta se ignorará.
    3. **Cálculo:** * Fácil: 1 punto
       * Medio: 2 puntos
       * Difícil: 3 puntos
    """
    return service.submit_answers(assignment_id, current_user.id, submission)