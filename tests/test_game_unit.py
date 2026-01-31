import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException

from app.modules.game.service import GameService
from app.modules.game.schemas import GameSubmission, AnswerSubmit
from app.modules.trivias.models import TriviaAssignment, Trivia, AssignmentStatus
from app.modules.questions.models import Question, Option, DifficultyLevel


class TestCalculoPuntaje:
    """
    Test 1: Verificar que el cálculo de puntaje funcione correctamente.
    
    Regla de negocio:
    - Easy = 1 punto
    - Medium = 2 puntos
    - Hard = 3 puntos
    - Respuesta incorrecta = 0 puntos
    """
    
    def test_puntaje_respuesta_correcta_easy(self):
        """Una respuesta correcta en pregunta EASY debe dar 1 punto."""
        # Arrange: Configurar mocks
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        # Simular datos
        mock_assignment = Mock(spec=TriviaAssignment)
        mock_assignment.id = 1
        mock_assignment.status = AssignmentStatus.PENDING
        
        mock_question = Mock(spec=Question)
        mock_question.id = 10
        mock_question.difficulty = DifficultyLevel.EASY
        
        mock_option = Mock(spec=Option)
        mock_option.id = 20
        mock_option.question_id = 10
        mock_option.is_correct = True
        
        # Configurar comportamiento del repositorio
        mock_repo.get_assignment.return_value = mock_assignment
        mock_repo.get_question.return_value = mock_question
        mock_repo.get_option.return_value = mock_option
        mock_repo.save_answer.return_value = None
        mock_repo.complete_assignment.return_value = None
        mock_repo.commit.return_value = None
        
        submission = GameSubmission(answers=[
            AnswerSubmit(question_id=10, option_id=20)
        ])
        
        # Act: Ejecutar
        result = service.submit_answers(
            assignment_id=1,
            user_id=100,
            submission=submission
        )
        
        # Assert: Verificar
        assert result["total_score"] == 1
        assert result["correct_count"] == 1
        assert "éxito" in result["message"].lower()
    
    def test_puntaje_respuesta_correcta_medium(self):
        """Una respuesta correcta en pregunta MEDIUM debe dar 2 puntos."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        mock_assignment = Mock(spec=TriviaAssignment)
        mock_assignment.id = 1
        mock_assignment.status = AssignmentStatus.PENDING
        
        mock_question = Mock(spec=Question)
        mock_question.id = 10
        mock_question.difficulty = DifficultyLevel.MEDIUM
        
        mock_option = Mock(spec=Option)
        mock_option.id = 20
        mock_option.question_id = 10
        mock_option.is_correct = True
        
        mock_repo.get_assignment.return_value = mock_assignment
        mock_repo.get_question.return_value = mock_question
        mock_repo.get_option.return_value = mock_option
        mock_repo.save_answer.return_value = None
        mock_repo.complete_assignment.return_value = None
        mock_repo.commit.return_value = None
        
        submission = GameSubmission(answers=[
            AnswerSubmit(question_id=10, option_id=20)
        ])
        
        result = service.submit_answers(1, 100, submission)
        
        assert result["total_score"] == 2
        assert result["correct_count"] == 1
    
    def test_puntaje_respuesta_correcta_hard(self):
        """Una respuesta correcta en pregunta HARD debe dar 3 puntos."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        mock_assignment = Mock(spec=TriviaAssignment)
        mock_assignment.id = 1
        mock_assignment.status = AssignmentStatus.PENDING
        
        mock_question = Mock(spec=Question)
        mock_question.id = 10
        mock_question.difficulty = DifficultyLevel.HARD
        
        mock_option = Mock(spec=Option)
        mock_option.id = 20
        mock_option.question_id = 10
        mock_option.is_correct = True
        
        mock_repo.get_assignment.return_value = mock_assignment
        mock_repo.get_question.return_value = mock_question
        mock_repo.get_option.return_value = mock_option
        mock_repo.save_answer.return_value = None
        mock_repo.complete_assignment.return_value = None
        mock_repo.commit.return_value = None
        
        submission = GameSubmission(answers=[
            AnswerSubmit(question_id=10, option_id=20)
        ])
        
        result = service.submit_answers(1, 100, submission)
        
        assert result["total_score"] == 3
        assert result["correct_count"] == 1
    
    def test_puntaje_respuesta_incorrecta(self):
        """Una respuesta incorrecta debe dar 0 puntos."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        mock_assignment = Mock(spec=TriviaAssignment)
        mock_assignment.id = 1
        mock_assignment.status = AssignmentStatus.PENDING
        
        mock_question = Mock(spec=Question)
        mock_question.id = 10
        mock_question.difficulty = DifficultyLevel.HARD  # Aunque sea difícil
        
        mock_option = Mock(spec=Option)
        mock_option.id = 20
        mock_option.question_id = 10
        mock_option.is_correct = False  # Respuesta incorrecta
        
        mock_repo.get_assignment.return_value = mock_assignment
        mock_repo.get_question.return_value = mock_question
        mock_repo.get_option.return_value = mock_option
        mock_repo.save_answer.return_value = None
        mock_repo.complete_assignment.return_value = None
        mock_repo.commit.return_value = None
        
        submission = GameSubmission(answers=[
            AnswerSubmit(question_id=10, option_id=20)
        ])
        
        result = service.submit_answers(1, 100, submission)
        
        assert result["total_score"] == 0
        assert result["correct_count"] == 0
    
    def test_puntaje_multiple_respuestas_mixtas(self):
        """Calcular puntaje con múltiples respuestas (correctas e incorrectas)."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        mock_assignment = Mock(spec=TriviaAssignment)
        mock_assignment.id = 1
        mock_assignment.status = AssignmentStatus.PENDING
        
        # Pregunta 1: EASY, correcta (1 punto)
        q1 = Mock(spec=Question)
        q1.id = 10
        q1.difficulty = DifficultyLevel.EASY
        
        o1 = Mock(spec=Option)
        o1.id = 20
        o1.question_id = 10
        o1.is_correct = True
        
        # Pregunta 2: MEDIUM, incorrecta (0 puntos)
        q2 = Mock(spec=Question)
        q2.id = 11
        q2.difficulty = DifficultyLevel.MEDIUM
        
        o2 = Mock(spec=Option)
        o2.id = 21
        o2.question_id = 11
        o2.is_correct = False
        
        # Pregunta 3: HARD, correcta (3 puntos)
        q3 = Mock(spec=Question)
        q3.id = 12
        q3.difficulty = DifficultyLevel.HARD
        
        o3 = Mock(spec=Option)
        o3.id = 22
        o3.question_id = 12
        o3.is_correct = True
        
        # Configurar side_effect para devolver diferentes valores según el argumento
        mock_repo.get_assignment.return_value = mock_assignment
        mock_repo.get_question.side_effect = [q1, q2, q3]
        mock_repo.get_option.side_effect = [o1, o2, o3]
        mock_repo.save_answer.return_value = None
        mock_repo.complete_assignment.return_value = None
        mock_repo.commit.return_value = None
        
        submission = GameSubmission(answers=[
            AnswerSubmit(question_id=10, option_id=20),
            AnswerSubmit(question_id=11, option_id=21),
            AnswerSubmit(question_id=12, option_id=22),
        ])
        
        result = service.submit_answers(1, 100, submission)
        
        # Total: 1 + 0 + 3 = 4 puntos
        assert result["total_score"] == 4
        assert result["correct_count"] == 2


class TestValidacionesSeguridad:
    """
    Test 2: Verificar validaciones de seguridad.
    
    Estas validaciones previenen trampa o errores:
    - No se puede enviar opción de otra pregunta
    - No se puede completar trivia ya finalizada
    - Validar que existan pregunta y opción
    """
    
    def test_rechaza_opcion_de_otra_pregunta(self):
        """Debe rechazar si la opción no pertenece a la pregunta enviada."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        mock_assignment = Mock(spec=TriviaAssignment)
        mock_assignment.id = 1
        mock_assignment.status = AssignmentStatus.PENDING
        
        mock_question = Mock(spec=Question)
        mock_question.id = 10
        
        mock_option = Mock(spec=Option)
        mock_option.id = 20
        mock_option.question_id = 99  # Pertenece a otra pregunta
        
        mock_repo.get_assignment.return_value = mock_assignment
        mock_repo.get_question.return_value = mock_question
        mock_repo.get_option.return_value = mock_option
        
        submission = GameSubmission(answers=[
            AnswerSubmit(question_id=10, option_id=20)
        ])
        
        # Debe lanzar HTTPException 422
        with pytest.raises(HTTPException) as exc_info:
            service.submit_answers(1, 100, submission)
        
        assert exc_info.value.status_code == 422
        assert "no pertenece" in exc_info.value.detail.lower()
    
    def test_rechaza_trivia_ya_completada(self):
        """No se debe poder enviar respuestas a una trivia ya completada."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        mock_assignment = Mock(spec=TriviaAssignment)
        mock_assignment.id = 1
        mock_assignment.status = AssignmentStatus.COMPLETED  # Ya completada
        
        mock_repo.get_assignment.return_value = mock_assignment
        
        submission = GameSubmission(answers=[
            AnswerSubmit(question_id=10, option_id=20)
        ])
        
        with pytest.raises(HTTPException) as exc_info:
            service.submit_answers(1, 100, submission)
        
        assert exc_info.value.status_code == 409
        assert "completada" in exc_info.value.detail.lower()
    
    def test_rechaza_opcion_inexistente(self):
        """Debe rechazar si la opción no existe."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        mock_assignment = Mock(spec=TriviaAssignment)
        mock_assignment.id = 1
        mock_assignment.status = AssignmentStatus.PENDING
        
        mock_repo.get_assignment.return_value = mock_assignment
        mock_repo.get_option.return_value = None  # Opción no existe
        
        submission = GameSubmission(answers=[
            AnswerSubmit(question_id=10, option_id=999)
        ])
        
        with pytest.raises(HTTPException) as exc_info:
            service.submit_answers(1, 100, submission)
        
        assert exc_info.value.status_code == 404
        assert "opción" in exc_info.value.detail.lower()


class TestObtenerTriviasPendientes:
    """
    Test 3: Obtener trivias asignadas al usuario.
    """
    
    def test_retorna_trivias_pendientes(self):
        """Debe retornar las trivias asignadas al usuario."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        # Simular 2 asignaciones
        trivia1 = Mock(spec=Trivia)
        trivia1.name = "Trivia de Python"
        
        trivia2 = Mock(spec=Trivia)
        trivia2.name = "Trivia de SQL"
        
        assignment1 = Mock(spec=TriviaAssignment)
        assignment1.id = 1
        assignment1.trivia = trivia1
        assignment1.status = AssignmentStatus.PENDING
        
        assignment2 = Mock(spec=TriviaAssignment)
        assignment2.id = 2
        assignment2.trivia = trivia2
        assignment2.status = AssignmentStatus.PENDING
        
        mock_repo.get_pending_assignments.return_value = [assignment1, assignment2]
        
        # Act
        result = service.get_my_trivias(user_id=100)
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["trivia_name"] == "Trivia de Python"
        assert result[1]["id"] == 2
        assert result[1]["trivia_name"] == "Trivia de SQL"
    
    def test_retorna_lista_vacia_sin_asignaciones(self):
        """Si no tiene trivias, debe retornar lista vacía."""
        mock_repo = Mock()
        service = GameService(mock_repo)
        
        mock_repo.get_pending_assignments.return_value = []
        
        result = service.get_my_trivias(user_id=100)
        
        assert result == []
