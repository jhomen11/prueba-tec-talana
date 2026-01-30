from fastapi import HTTPException
from app.modules.game.repository import GameRepository
from app.modules.game.schemas import GameSubmission
from app.modules.trivias.models import UserAnswer, AssignmentStatus
from app.modules.questions.models import DifficultyLevel

class GameService:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def get_my_trivias(self, user_id: int):
        # Mapeamos manualmente para devolver estructura plana
        assignments = self.repository.get_pending_assignments(user_id)
        return [
            {"id": a.id, "trivia_name": a.trivia.name, "status": a.status}
            for a in assignments
        ]

    def get_game_details(self, assignment_id: int, user_id: int):
        assignment = self.repository.get_assignment_with_details(assignment_id, user_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Trivia no encontrada o no asignada.")
        
        if assignment.status == AssignmentStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Ya completaste esta trivia.")

        # Mapeo manual para asegurar que NO se envíen campos prohibidos
        return {
            "assignment_id": assignment.id,
            "trivia_name": assignment.trivia.name,
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "options": [{"id": o.id, "text": o.text} for o in q.options]
                }
                for q in assignment.trivia.questions
            ]
        }

    def submit_answers(self, assignment_id: int, user_id: int, submission: GameSubmission):
        assignment = self.repository.get_assignment(assignment_id, user_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Asignación no encontrada.")
        if assignment.status == AssignmentStatus.COMPLETED:
            raise HTTPException(status_code=409, detail="Esta trivia ya fue completada.")

        total_score = 0
        correct_count = 0
        
        try:
            # Procesar cada respuesta
            for ans_input in submission.answers:
                # Validar que la opción pertenezca a la pregunta (seguridad)
                option = self.repository.get_option(ans_input.option_id)
                question = self.repository.get_question(ans_input.question_id)
                
                if not option:
                    raise HTTPException(status_code=404, detail=f"Opción {ans_input.option_id} no encontrada.")
                if not question:
                    raise HTTPException(status_code=404, detail=f"Pregunta {ans_input.question_id} no encontrada.")
                if option.question_id != question.id:
                    raise HTTPException(status_code=422, detail=f"La opción {option.id} no pertenece a la pregunta {question.id}.")

                # Calcular puntos
                points = 0
                is_correct = option.is_correct
                
                if is_correct:
                    correct_count += 1
                    # Regla de Negocio: Puntaje por dificultad
                    if question.difficulty == DifficultyLevel.EASY:
                        points = 1
                    elif question.difficulty == DifficultyLevel.MEDIUM:
                        points = 2
                    elif question.difficulty == DifficultyLevel.HARD:
                        points = 3
                
                total_score += points

                # Guardar respuesta individual (Auditoría)
                user_answer = UserAnswer(
                    assignment_id=assignment.id,
                    question_id=question.id,
                    selected_option_id=option.id,
                    is_correct=is_correct,
                    points_awarded=points
                )
                self.repository.save_answer(user_answer)

            # Finalizar la trivia
            self.repository.complete_assignment(assignment, total_score)
            self.repository.commit()  # Commit explícito
            
            return {
                "total_score": total_score,
                "correct_count": correct_count,
                "message": "¡Trivia completada con éxito!"
            }
        except HTTPException:
            self.repository.rollback()
            raise
        except Exception as e:
            self.repository.rollback()
            raise HTTPException(status_code=500, detail=f"Error procesando respuestas: {str(e)}")