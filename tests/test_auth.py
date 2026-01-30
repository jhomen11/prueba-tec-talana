"""
Tests de Autenticación (Auth).
Archivo: tests/test_auth.py

Aquí probamos el flujo completo de registro y login.
"""
import pytest


def test_signup_new_user(client):
    """
    Test 1: Registrar un nuevo jugador.
    
    ¿Qué hace?
    1. Envía POST a /users/signup con datos de un nuevo usuario
    2. Verifica que responda 201 (Created)
    3. Verifica que el JSON contenga el email y rol=player
    """
    # Datos del nuevo usuario
    new_user = {
        "full_name": "Test Player",
        "email": "test@player.com",
        "password": "password123"
    }
    
    # Hacer el registro
    response = client.post("/users/signup", json=new_user)
    
    # Validar código de estado
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    # Validar contenido de la respuesta
    data = response.json()
    assert data["email"] == "test@player.com"
    assert data["full_name"] == "Test Player"
    assert data["role"] == "player"  # Siempre debe ser player en signup
    assert "id" in data  # Debe tener un ID asignado
    
    print(f"Usuario registrado con ID: {data['id']}")


def test_signup_duplicate_email(client):
    """
    Test 2: Intentar registrar el mismo email dos veces.
    
    ¿Qué debe pasar?
    - Primer registro: 201 OK
    - Segundo registro: 409 Conflict (email duplicado)
    """
    user_data = {
        "full_name": "John Doe",
        "email": "duplicate@test.com",
        "password": "secret123"
    }
    
    # Primer registro (debe funcionar)
    response1 = client.post("/users/signup", json=user_data)
    assert response1.status_code == 201
    
    # Segundo registro con el mismo email (debe fallar)
    response2 = client.post("/users/signup", json=user_data)
    assert response2.status_code == 409  # Conflict
    assert "email ya está registrado" in response2.json()["detail"].lower()
    
    print("Validación de email duplicado funciona correctamente")


def test_login_success(client):
    """
    Test 3: Login exitoso con cookie.
    
    Flujo:
    1. Registrar usuario
    2. Hacer login
    3. Verificar que se establezca la cookie 'access_token'
    """
    # Paso 1: Registrar usuario
    signup_data = {
        "full_name": "Ana Player",
        "email": "ana@login.com",
        "password": "mypassword"
    }
    client.post("/users/signup", json=signup_data)
    
    # Paso 2: Hacer login
    login_data = {
        "email": "ana@login.com",
        "password": "mypassword"
    }
    response = client.post("/auth/login", json=login_data)
    
    # Paso 3: Validar respuesta
    assert response.status_code == 200
    assert response.json()["message"] == "Login exitoso"
    
    # Paso 4: Validar que la cookie se estableció
    assert "access_token" in response.cookies
    assert response.cookies["access_token"] != ""
    
    print(f"Login exitoso, cookie establecida: {response.cookies['access_token'][:20]}...")


def test_login_wrong_password(client):
    """
    Test 4: Login con contraseña incorrecta.
    
    Debe retornar 401 Unauthorized.
    """
    # Registrar usuario
    client.post("/users/signup", json={
        "full_name": "User Test",
        "email": "user@test.com",
        "password": "correct_password"
    })
    
    # Intentar login con contraseña incorrecta
    response = client.post("/auth/login", json={
        "email": "user@test.com",
        "password": "wrong_password"
    })
    
    assert response.status_code == 401
    assert "inválidas" in response.json()["detail"].lower()
    
    print("Validación de contraseña incorrecta funciona")


def test_login_nonexistent_user(client):
    """
    Test 5: Login con usuario que no existe.
    
    Debe retornar 401 Unauthorized.
    """
    response = client.post("/auth/login", json={
        "email": "noexiste@test.com",
        "password": "anypassword"
    })
    
    assert response.status_code == 401
    assert "inválidas" in response.json()["detail"].lower()
    
    print("Validación de usuario inexistente funciona")


def test_logout(client):
    """
    Test 6: Logout (eliminar cookie).
    
    Flujo:
    1. Login
    2. Logout
    3. Verificar que se haya limpiado la cookie
    """
    # Login primero
    client.post("/users/signup", json={
        "full_name": "Logout User",
        "email": "logout@test.com",
        "password": "pass123"
    })
    
    client.post("/auth/login", json={
        "email": "logout@test.com",
        "password": "pass123"
    })
    
    # Hacer logout
    response = client.post("/auth/logout")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Logout exitoso"
    
    print("Logout funciona correctamente")
