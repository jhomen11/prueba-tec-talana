# TalaTrivia API

API REST para gestión de trivias empresariales, construida con FastAPI y PostgreSQL.

## Descripción del Proyecto

TalaTrivia es una aplicación que permite a administradores crear trivias con preguntas de opción múltiple y asignarlas a jugadores. Los jugadores pueden responder las trivias asignadas y competir en un ranking global.

### Características Principales

- **Autenticación con JWT**: Sistema de login con cookies seguras
- **Roles de usuario**: Admin (crear trivias/preguntas) y Player (jugar trivias)
- **CRUD completo**: Gestión de usuarios, preguntas y trivias
- **Sistema de juego**: Asignación de trivias, respuestas y puntuación
- **Ranking global**: Clasificación de jugadores por puntaje total
- **Paginación**: Endpoints con paginación configurable
- **Soft Delete**: Eliminación lógica de registros
- **Rate Limiting**: Protección contra abuso de endpoints

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Docker**: [Instalar Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Docker Compose**: Incluido con Docker Desktop
- **Git**: Para clonar el repositorio

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/jhomen11/prueba-tec-talana.git
cd prueba_talana
```

### 2. Configurar Variables de Entorno

El archivo `.env` ya está incluido con valores por defecto para desarrollo local:

```env
DB_USER=talana_user
DB_PASSWORD=secretpassword
DB_NAME=talatrivia_db
FIRST_SUPERUSER_EMAIL=admin@talana.com
FIRST_SUPERUSER_PASSWORD=admin123
SECRET_KEY=your-secret-key-here-change-in-production-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ IMPORTANTE**: El archivo `.env` está incluido en el repositorio **únicamente porque esto es una prueba técnica**. En un proyecto real, este archivo **NUNCA** debe subirse a Git. Debe estar en `.gitignore` y cada desarrollador debe crear su propio `.env` local basándose en un archivo `.env.example`.


### 3. Levantar la Aplicación

```bash
docker compose up --build
```

Este comando:
- Construye la imagen Docker de la API
- Descarga PostgreSQL 15
- Crea la base de datos
- Ejecuta las migraciones automáticas
- Levanta la API en `http://localhost:8000`

### 4. Verificar que Funciona

Abre tu navegador en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs

Deberías ver un mensaje: `"TalaTrivia API is running"`

## Generar Datos de Prueba (Seed)

Para facilitar las pruebas, la aplicación incluye rutas para generar y eliminar datos de ejemplo.

### Crear Datos Completos

```bash
curl -X POST http://localhost:8000/testing/seed
```

O desde Swagger UI: `POST /testing/seed`

**Esto crea:**
- 5 jugadores (ana@talana.com, beto@talana.com, carla@talana.com, diego@talana.com, elena@talana.com)
  - Contraseña de todos: `123456`
- 12 preguntas (4 fáciles, 4 medias, 4 difíciles)
- 3 trivias diferentes con distintas dificultades
- 6 partidas completadas simuladas con respuestas y puntajes

**Partidas simuladas:**
- Ana: 3 puntos (1 trivia completada)
- Beto: 8 puntos (2 trivias completadas) - Líder del ranking
- Carla: 2 puntos (1 trivia completada)
- Diego: 7 puntos (2 trivias completadas)
- Elena: Sin partidas (solo trivias pendientes)

Esto te permite ver datos reales en:
- `GET /ranking/` - Ranking global con puntajes
- `GET /game/my-trivias` - Trivias asignadas (login como cualquier jugador)
- `GET /ranking/my-stats` - Estadísticas personales

### Limpiar Datos de Prueba

```bash
curl -X DELETE http://localhost:8000/testing/reset
```

O desde Swagger UI: `DELETE /testing/reset`

**Esto elimina:**
- Todos los jugadores de prueba
- Todas las preguntas y opciones
- Todas las trivias y asignaciones
- Todas las respuestas

**⚠️ NO elimina:** El usuario admin inicial

## Uso de la Aplicación

### Usuario Admin por Defecto

Al iniciar la aplicación, se crea automáticamente un usuario administrador:

- **Email**: `admin@talana.com`
- **Password**: `admin123`

### Usuarios de Prueba (después del seed)

Si ejecutaste el seed, puedes usar cualquiera de estos usuarios para probar como jugador:

- **Email**: `ana@talana.com` / **Password**: `123456`
- **Email**: `beto@talana.com` / **Password**: `123456`
- **Email**: `carla@talana.com` / **Password**: `123456`
- **Email**: `diego@talana.com` / **Password**: `123456`
- **Email**: `elena@talana.com` / **Password**: `123456`

### Flujo de Trabajo Básico

1. **Login como Admin**:
   - Ve a `/docs` (Swagger UI)
   - Ejecuta `POST /auth/login` con las credenciales del admin
   - La cookie se establecerá automáticamente

2. **Crear Preguntas**:
   - `POST /questions/` - Crear preguntas con opciones

3. **Crear Trivia**:
   - `POST /trivias/` - Asignar preguntas y jugadores

4. **Registro de Jugador**:
   - `POST /users/signup` - Cualquiera puede registrarse como jugador

5. **Jugar Trivia (como jugador)**:
   - `GET /game/my-trivias` - Ver trivias asignadas
   - `GET /game/play/{assignment_id}` - Ver preguntas
   - `POST /game/submit/{assignment_id}` - Enviar respuestas

6. **Ver Ranking**:
   - `GET /ranking/` - Clasificación global

## Modelo de Base de Datos

### Tablas Principales

#### **users**
Información de usuarios del sistema.

**Campos:**
- `id`, `full_name`, `email`, `hashed_password`, `role`, `created_at`, `deleted_at`

**Relaciones:**
- Tiene muchas asignaciones de trivias (`trivia_assignments`)

#### **questions**
Preguntas para las trivias.

**Campos:**
- `id`, `text`, `difficulty` (easy/medium/hard), `created_at`, `deleted_at`

**Relaciones:**
- Tiene muchas opciones (`options`)
- Está en muchas trivias (N:M a través de `trivia_questions`)

#### **options**
Opciones de respuesta para cada pregunta.

**Campos:**
- `id`, `text`, `is_correct`, `question_id`

**Relaciones:**
- Pertenece a una pregunta (`questions`)

#### **trivias**
Conjunto de preguntas agrupadas.

**Campos:**
- `id`, `name`, `description`, `created_at`, `deleted_at`

**Relaciones:**
- Tiene muchas preguntas (N:M a través de `trivia_questions`)
- Tiene muchas asignaciones a usuarios (`trivia_assignments`)

#### **trivia_questions**
Tabla intermedia para relacionar trivias con preguntas.

**Campos:**
- `trivia_id`, `question_id`

#### **trivia_assignments**
Asignación de una trivia a un usuario (partida).

**Campos:**
- `id`, `user_id`, `trivia_id`, `status` (pending/completed/cancelled), `total_score`, `created_at`

**Relaciones:**
- Pertenece a un usuario (`users`)
- Pertenece a una trivia (`trivias`)
- Tiene muchas respuestas (`user_answers`)

#### **user_answers**
Cada respuesta individual del usuario en una partida.

**Campos:**
- `id`, `assignment_id`, `question_id`, `selected_option_id`, `is_correct`, `points_awarded`, `created_at`

**Relaciones:**
- Pertenece a una asignación (`trivia_assignments`)

### Enums

- **UserRole**: `admin`, `player`
- **DifficultyLevel**: `easy` (1 punto), `medium` (2 puntos), `hard` (3 puntos)
- **AssignmentStatus**: `pending`, `completed`, `cancelled`

## Ejecutar Tests

La aplicación incluye tests automatizados con pytest. Se implementan dos tipos de tests:

### Tipos de Tests

#### **Tests de Integración**
Prueban el flujo completo de la API (HTTP → Base de datos → HTTP). Usan base de datos SQLite en memoria.

**Archivos:**
- `test_main.py` - Health check
- `test_auth.py` - Autenticación (signup, login, logout)

#### **Tests Unitarios**
Prueban funciones aisladas sin base de datos usando mocks. Son mucho más rápidos.

**Archivos:**
- `test_game_unit.py` - Lógica de negocio del módulo game:
  - Cálculo de puntaje por dificultad
  - Validaciones de seguridad (anti-trampa)
  - Obtención de trivias pendientes

### Comandos de Ejecución

#### Ejecutar Todos los Tests

```bash
docker compose exec api pytest tests/ -v
```

#### Ejecutar Tests con Cobertura

```bash
docker compose exec api pytest tests/ --cov=app --cov-report=html
```

El reporte HTML se genera en `htmlcov/index.html`. Ábrelo con:
```bash
open htmlcov/index.html
```

#### Ejecutar Solo Tests de Integración

```bash
docker compose exec api pytest tests/test_auth.py -v
```

#### Ejecutar Solo Tests Unitarios

```bash
docker compose exec api pytest tests/test_game_unit.py -v
```

### Resultado Actual

Al ejecutar todos los tests deberías ver:
- **17 tests pasando** (7 integración + 10 unitarios)
- Tiempo de ejecución: ~2-3 segundos
- 1 warning de librería externa (passlib)

## Estructura del Proyecto

```
prueba_talana/
├── app/
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── core/
│   │   ├── config.py          # Configuración y variables de entorno
│   │   ├── database.py        # Conexión a PostgreSQL
│   │   ├── logger.py          # Sistema de logs
│   │   └── pagination.py      # Utilidades de paginación
│   └── modules/
│       ├── users/             # Gestión de usuarios
│       ├── auth/              # Autenticación y JWT
│       ├── questions/         # CRUD de preguntas
│       ├── trivias/           # CRUD de trivias
│       ├── game/              # Lógica del juego
│       ├── ranking/           # Sistema de ranking
│       └── testing/           # Endpoints para generar/limpiar datos de prueba
├── tests/
│   ├── conftest.py            # Fixtures de pytest
│   ├── test_main.py           # Test de health check
│   ├── test_auth.py           # Tests de autenticación (integración)
│   └── test_game_unit.py      # Tests unitarios del módulo game
├── docker-compose.yaml        # Configuración de servicios
├── Dockerfile                 # Imagen de la API
├── requirements.txt           # Dependencias de Python
├── .env                       # Variables de entorno (solo para prueba técnica)
├── .env.example               # Plantilla de variables de entorno
└── README.md                  # Este archivo
```

## Endpoints Principales

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/logout` - Cerrar sesión
- `POST /users/signup` - Registro público (siempre crea rol player)

### Usuarios (Admin)
- `GET /users/` - Listar usuarios (paginado)
- `POST /users/` - Crear usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario (soft delete)
- `GET /users/deleted` - Listar usuarios eliminados

### Preguntas (Admin)
- `GET /questions/` - Listar preguntas (paginado)
- `POST /questions/` - Crear pregunta con opciones
- `PUT /questions/{id}` - Actualizar pregunta
- `DELETE /questions/{id}` - Eliminar pregunta

### Trivias (Admin)
- `GET /trivias/` - Listar trivias (paginado)
- `POST /trivias/` - Crear trivia y asignar a usuarios
- `PUT /trivias/{id}` - Actualizar trivia
- `DELETE /trivias/{id}` - Eliminar trivia

### Juego (Player)
- `GET /game/my-trivias` - Mis trivias asignadas
- `GET /game/play/{assignment_id}` - Ver preguntas de una trivia
- `POST /game/submit/{assignment_id}` - Enviar respuestas

### Ranking (Público)
- `GET /ranking/` - Ranking global de jugadores
- `GET /ranking/my-stats` - Mis estadísticas (requiere login)

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **PostgreSQL 15**: Base de datos relacional
- **SQLAlchemy**: ORM para Python
- **Pydantic**: Validación de datos
- **JWT**: Autenticación con JSON Web Tokens
- **Docker & Docker Compose**: Containerización
- **Pytest**: Framework de testing
- **Uvicorn**: Servidor ASGI

## Comandos Útiles

### Ver Logs de la Aplicación
```bash
docker compose logs -f api
```

### Ver Logs de la Base de Datos
```bash
docker compose logs -f db
```

### Acceder al Contenedor de la API
```bash
docker compose exec api bash
```

### Acceder a PostgreSQL
```bash
docker compose exec db psql -U talana_user -d talatrivia_db
```

### Detener la Aplicación
```bash
docker compose down
```

### Reiniciar con Base de Datos Limpia
```bash
docker compose down -v  # Elimina volúmenes
docker compose up --build
```

## Solución de Problemas

### La API no se conecta a la base de datos
- Verifica que el contenedor `db` esté saludable: `docker compose ps`
- Revisa los logs: `docker compose logs db`

### Puerto 8000 ya está en uso
- Cambia el puerto en `docker-compose.yaml`: `"8001:8000"`

### Los cambios en el código no se reflejan
- Asegúrate de que los volúmenes estén montados correctamente
- Reinicia el contenedor: `docker compose restart api`

## Desarrollo

### Hot Reload
Los cambios en el código se reflejan automáticamente sin reiniciar gracias al volumen montado en `docker-compose.yaml`

### Agregar Dependencias
1. Agrega el paquete a `requirements.txt`
2. Reconstruye la imagen: `docker compose up --build`

### Modificar la Base de Datos
La aplicación usa SQLAlchemy para crear tablas automáticamente. Si modificas los modelos:
1. Los cambios se aplican al reiniciar: `docker compose restart api`
2. Para datos limpios: `docker compose down -v && docker compose up --build`

## Contribuir

1. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
2. Realiza tus cambios
3. Ejecuta los tests: `docker compose exec api pytest tests/ -v`
4. Commit: `git commit -m "Descripción del cambio"`
5. Push: `git push origin feature/nueva-funcionalidad`
6. Crea un Pull Request
