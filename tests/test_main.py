"""
Test del endpoint de health check.
Archivo: tests/test_main.py

Este es el test MÁS SIMPLE posible para entender cómo funciona.
"""


def test_health_check(client):
    """
    Prueba que el endpoint raíz funcione.
    
    ¿Qué hace este test?
    1. Hace un GET a "/"
    2. Verifica que responda con 200 OK
    3. Verifica que el JSON contenga "status": "ok"
    
    El parámetro 'client' es la fixture que creamos en conftest.py
    """
    # Hacer request
    response = client.get("/")
    
    # Validar código de estado
    assert response.status_code == 200
    
    # Validar contenido
    json_data = response.json()
    assert json_data["status"] == "ok"
    assert "TalaTrivia API is running" in json_data["message"]
    
    print("Test pasó correctamente!")
