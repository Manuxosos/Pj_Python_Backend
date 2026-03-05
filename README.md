# TaskFlow API - Python Backend Educativo

> **Sistema de gestión de proyectos y tareas** construido con FastAPI.
> Proyecto diseñado para aprender desarrollo backend en Python con las mismas
> tecnologías que se usan en el mundo laboral real.

---

## ¿Qué es un backend y para qué sirve?

Un **backend** es el servidor que procesa la lógica de negocio, gestiona la base de datos
y expone una **API REST** que el frontend (web, móvil) consume.

```
[Usuario]  →  [Frontend: React/Angular/Vue]  →  [Backend: FastAPI]  →  [Base de datos: PostgreSQL]
```

Cuando usas una app como Jira, Trello o Notion:
- Lo que ves en pantalla = **Frontend**
- El servidor que guarda tus datos = **Backend** (esto es lo que aprendemos aquí)

---

## Stack tecnológico (y comparación con Java/Spring)

| Concepto | Java / Spring Boot | Python / FastAPI |
|---|---|---|
| Framework web | Spring Boot | **FastAPI** |
| ORM (acceso a BD) | JPA / Hibernate | **SQLAlchemy** |
| Validación de datos | Bean Validation | **Pydantic** |
| Serialización JSON | Jackson | **Pydantic** |
| Autenticación JWT | jjwt | **python-jose** |
| Hashing contraseñas | BCryptPasswordEncoder | **passlib[bcrypt]** |
| Servidor HTTP | Tomcat (embebido) | **Uvicorn** |
| Documentación API | Springdoc OpenAPI | **FastAPI (automático)** |
| DTOs | Clases DTO manuales | **Pydantic schemas** |
| Controller | @RestController | **APIRouter** |
| Service | @Service | **Módulo de funciones** |
| Repositorio | JpaRepository | **SQLAlchemy Session** |
| Inyección de dependencias | @Autowired / @Bean | **Depends()** |
| Config | application.properties | **Pydantic Settings + .env** |

---

## Arquitectura del proyecto

```
taskflow-api/
│
├── app/
│   ├── main.py              # Punto de entrada (como @SpringBootApplication)
│   │
│   ├── config/
│   │   ├── settings.py      # Configuración (como application.properties)
│   │   └── database.py      # Conexión a BD (como DataSource en Spring)
│   │
│   ├── models/              # Entidades de BD (como @Entity en JPA)
│   │   ├── usuario.py       # Tabla usuarios + enum RolUsuario
│   │   ├── proyecto.py      # Tabla proyectos + enum EstadoProyecto
│   │   ├── tarea.py         # Tabla tareas + enums Estado, Prioridad
│   │   └── comentario.py    # Tabla comentarios
│   │
│   ├── schemas/             # DTOs con validación (como DTO + @Valid en Java)
│   │   ├── auth.py          # LoginRequest, TokenResponse
│   │   ├── usuario.py       # UsuarioCreate, UsuarioUpdate, UsuarioResponse
│   │   ├── proyecto.py      # ProyectoCreate, ProyectoUpdate, ProyectoResponse
│   │   ├── tarea.py         # TareaCreate, TareaEstadoUpdate, TareaResponse
│   │   └── comentario.py    # ComentarioCreate, ComentarioResponse
│   │
│   ├── routers/             # Controllers / Endpoints HTTP
│   │   ├── auth.py          # POST /api/auth/login, GET /api/auth/me
│   │   ├── usuarios.py      # CRUD /api/usuarios
│   │   ├── proyectos.py     # CRUD /api/proyectos
│   │   ├── tareas.py        # CRUD /api/tareas + PATCH estado
│   │   └── comentarios.py   # CRUD /api/tareas/{id}/comentarios
│   │
│   ├── services/            # Lógica de negocio (como @Service en Spring)
│   │   ├── auth_service.py
│   │   ├── usuario_service.py
│   │   ├── proyecto_service.py
│   │   ├── tarea_service.py
│   │   └── comentario_service.py
│   │
│   ├── security/            # JWT y autorización
│   │   ├── jwt.py           # Crear/verificar tokens JWT
│   │   └── dependencies.py  # get_usuario_actual, require_admin, etc.
│   │
│   ├── utils/
│   │   └── data_initializer.py  # Datos de prueba (como DataInitializer.java)
│   │
│   └── exceptions/
│       └── handlers.py      # Manejo global de errores (@ControllerAdvice)
│
├── requirements.txt         # Dependencias (como pom.xml / build.gradle)
├── .env.example             # Variables de entorno de ejemplo
└── README.md
```

### Patrón de capas (3-tier architecture)

```
HTTP Request
     ↓
┌──────────────┐
│   Router     │  Recibe la petición, valida el schema Pydantic
│  (Controller)│  Llama al service correspondiente
└──────┬───────┘
       ↓
┌──────────────┐
│   Service    │  Contiene la lógica de negocio
│              │  Verifica permisos, aplica reglas
└──────┬───────┘
       ↓
┌──────────────┐
│  SQLAlchemy  │  Accede a la base de datos
│    (ORM)     │  SELECT, INSERT, UPDATE, DELETE
└──────┬───────┘
       ↓
┌──────────────┐
│  Base de     │  SQLite (dev) o PostgreSQL (producción)
│    datos     │
└──────────────┘
       ↓
HTTP Response (JSON)
```

---

## Instalación y ejecución

### Requisitos previos
- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Manuxosos/Pj_Python_Backend.git
cd Pj_Python_Backend

# 2. Crear entorno virtual (SIEMPRE usar entorno virtual en Python)
python -m venv venv

# 3. Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Copiar el archivo de variables de entorno
cp .env.example .env

# 6. Ejecutar el servidor
uvicorn app.main:app --reload
```

### El servidor está listo cuando ves:
```
==================================================
  TaskFlow API v1.0.0
==================================================
  Modo debug: True
  Base de datos: sqlite:///./taskflow.db
==================================================

✅ Tablas creadas/verificadas en la base de datos
🚀 Inicializando base de datos con datos de prueba...
✅ Base de datos inicializada correctamente!

🚀 Servidor listo en http://localhost:8000
📚 Swagger UI: http://localhost:8000/docs
```

---

## URLs importantes

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000` | API raíz |
| `http://localhost:8000/docs` | **Swagger UI** (documentación interactiva) |
| `http://localhost:8000/redoc` | ReDoc (documentación alternativa) |
| `http://localhost:8000/health` | Health check |

---

## Usuarios de prueba

| Email | Password | Rol | Permisos |
|-------|----------|-----|----------|
| `admin@taskflow.com` | `Admin1234` | ADMIN | Todo |
| `laura@taskflow.com` | `Manager1234` | MANAGER | Crear proyectos, gestionar equipo |
| `roberto@taskflow.com` | `Manager1234` | MANAGER | Crear proyectos, gestionar equipo |
| `carlos@taskflow.com` | `Dev1234` | DESARROLLADOR | Ver y trabajar en tareas asignadas |
| `ana@taskflow.com` | `Dev1234` | DESARROLLADOR | Ver y trabajar en tareas asignadas |
| `miguel@taskflow.com` | `Dev1234` | DESARROLLADOR | Ver y trabajar en tareas asignadas |

---

## Endpoints de la API

### Autenticación
```
POST   /api/auth/login     → Obtener JWT token
GET    /api/auth/me        → Ver mi perfil (requiere JWT)
```

### Usuarios (requiere JWT)
```
GET    /api/usuarios/          → Listar usuarios (solo ADMIN)
POST   /api/usuarios/          → Crear usuario (solo ADMIN)
GET    /api/usuarios/{id}      → Ver usuario
PUT    /api/usuarios/{id}      → Actualizar usuario
DELETE /api/usuarios/{id}      → Desactivar usuario (solo ADMIN)
```

### Proyectos (requiere JWT)
```
GET    /api/proyectos/              → Listar proyectos
POST   /api/proyectos/              → Crear proyecto (MANAGER/ADMIN)
GET    /api/proyectos/{id}          → Ver proyecto
PUT    /api/proyectos/{id}          → Actualizar proyecto
DELETE /api/proyectos/{id}          → Eliminar proyecto
GET    /api/proyectos/{id}/tareas   → Tareas del proyecto
```

### Tareas (requiere JWT)
```
GET    /api/tareas/mis-tareas        → Mis tareas asignadas
POST   /api/tareas/                  → Crear tarea
GET    /api/tareas/{id}              → Ver tarea
PUT    /api/tareas/{id}              → Actualizar tarea
PATCH  /api/tareas/{id}/estado       → Cambiar estado
DELETE /api/tareas/{id}              → Eliminar tarea
```

### Comentarios (requiere JWT)
```
GET    /api/tareas/{id}/comentarios/       → Ver comentarios
POST   /api/tareas/{id}/comentarios/       → Añadir comentario
PUT    /api/tareas/{id}/comentarios/{cid}  → Editar comentario
DELETE /api/tareas/{id}/comentarios/{cid}  → Eliminar comentario
```

---

## Cómo probar la API

### Opción 1: Swagger UI (recomendado para aprender)

1. Abre http://localhost:8000/docs
2. Expande `POST /api/auth/login`
3. Haz clic en "Try it out"
4. Introduce las credenciales y ejecuta
5. Copia el `access_token` de la respuesta
6. Haz clic en el botón **Authorize** 🔒 (arriba a la derecha)
7. Escribe `Bearer <tu_token>` y confirma
8. ¡Ahora todos los endpoints están autorizados!

### Opción 2: curl (línea de comandos)

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@taskflow.com", "password": "Admin1234"}'

# 2. Usar el token (reemplaza TU_TOKEN)
curl http://localhost:8000/api/proyectos/ \
  -H "Authorization: Bearer TU_TOKEN"

# 3. Crear una tarea
curl -X POST http://localhost:8000/api/tareas/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Mi primera tarea",
    "prioridad": "ALTA",
    "proyecto_id": 1
  }'
```

### Opción 3: Postman / Insomnia
Importa la especificación OpenAPI desde: `http://localhost:8000/openapi.json`

---

## Conceptos clave para aprender

### 1. ¿Qué es una API REST?
Una API REST define cómo el frontend se comunica con el backend:
- **URL** = Identifica el recurso (`/api/proyectos/1`)
- **Método HTTP** = La acción (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`)
- **Body JSON** = Los datos que se envían
- **Código HTTP** = El resultado (`200 OK`, `201 Created`, `404 Not Found`)

### 2. ¿Qué es JWT?
Un **JSON Web Token** es como un "carnet de identidad digital":
```
eyJhbGciOiJIUzI1NiJ9  ←  Header (algoritmo)
.
eyJzdWIiOiJhZG1pbkB  ←  Payload (datos: email, rol, expiración)
.
FIRMA_DIGITAL         ←  Signature (garantiza que no fue manipulado)
```

Flujo completo:
```
1. Login con email+password → Server devuelve JWT
2. Cliente guarda el JWT
3. En cada petición → Cliente envía: Authorization: Bearer <JWT>
4. Server verifica el JWT → Si es válido, procesa la petición
```

### 3. ¿Por qué separar en capas?

**Sin capas** (código spaguetti):
```python
@app.post("/proyectos")
def crear_proyecto(data: dict):
    # Validación mezclada con lógica de BD mezclada con negocio
    if not data.get("nombre"):
        return {"error": "nombre requerido"}
    db.execute("INSERT INTO proyectos...")  # SQL directo
    # ...es difícil de mantener, testear y escalar
```

**Con capas** (limpio y mantenible):
```python
# Router: solo recibe la petición y llama al service
@router.post("/proyectos")
def crear_proyecto(data: ProyectoCreate, db = Depends(get_db)):
    return proyecto_service.create(db, data, usuario_actual)

# Service: solo lógica de negocio
def create(db, data, owner):
    if owner.rol not in [MANAGER, ADMIN]:
        raise PermisoDenegado()
    proyecto = Proyecto(**data.model_dump())
    db.add(proyecto)
    db.commit()
    return proyecto
```

### 4. ¿Qué es Pydantic y por qué es importante?

Pydantic valida automáticamente los datos de entrada:
```python
class TareaCreate(BaseModel):
    titulo: str = Field(..., min_length=3)  # Requerido, mínimo 3 chars
    prioridad: PrioridadTarea = "MEDIA"     # Debe ser un valor del enum
    proyecto_id: int                         # Debe ser número entero

# Si el cliente envía:
{"titulo": "A", "prioridad": "URGENTE", "proyecto_id": "abc"}

# FastAPI automáticamente responde:
{
  "error": "Error de validación",
  "detalle": [
    {"campo": "titulo", "mensaje": "String should have at least 3 characters"},
    {"campo": "prioridad", "mensaje": "Input should be 'BAJA', 'MEDIA', 'ALTA' or 'CRITICA'"},
    {"campo": "proyecto_id", "mensaje": "Input should be a valid integer"}
  ]
}
```

### 5. ORM vs SQL puro

**SQL puro** (frágil, difícil de mantener):
```python
cursor.execute("""
    SELECT u.id, u.nombre, u.email
    FROM usuarios u
    WHERE u.id = ? AND u.activo = 1
""", (usuario_id,))
resultado = cursor.fetchone()
```

**SQLAlchemy ORM** (seguro, expresivo, tipo-seguro):
```python
usuario = db.query(Usuario)\
    .filter(Usuario.id == usuario_id, Usuario.activo == True)\
    .first()
```

### 6. Seguridad basada en roles

```
ADMIN      → Puede hacer todo
MANAGER    → Puede crear proyectos, gestionar su equipo
DESARROLLADOR → Solo puede ver y trabajar en sus tareas

Implementación con FastAPI:
@router.delete("/{id}")
def eliminar(id: int, admin = Depends(require_admin)):
    # Solo llega aquí si el usuario es ADMIN
    # Si no, FastAPI devuelve 403 Forbidden automáticamente
```

---

## De SQLite a PostgreSQL (para producción)

El proyecto usa **SQLite** para simplificar el desarrollo.
Para usar PostgreSQL en producción, solo cambia el `.env`:

```bash
# Instalar driver de PostgreSQL
pip install psycopg2-binary

# Cambiar en .env
DATABASE_URL=postgresql://usuario:password@localhost:5432/taskflow
```

**No cambia nada más del código** gracias a SQLAlchemy.

---

## Para seguir aprendiendo

### Próximos pasos con este proyecto
1. **Añadir paginación** → Los endpoints de lista deberían paginar resultados
2. **Tests automáticos** → Escribir tests con pytest y httpx
3. **Migraciones con Alembic** → Gestionar cambios en el esquema de BD
4. **Docker** → Contenerizar la aplicación
5. **PostgreSQL** → Cambiar a base de datos de producción
6. **Deploy** → Subir a Railway, Render o AWS

### Recursos recomendados
- [Documentación oficial FastAPI](https://fastapi.tiangolo.com/) - Excelente tutorial
- [SQLAlchemy docs](https://docs.sqlalchemy.org/) - ORM completo
- [Real Python](https://realpython.com/) - Tutoriales Python avanzados
- [Pydantic docs](https://docs.pydantic.dev/) - Validación de datos

### Proyectos Python backend usados en el mundo real
| Empresa/Proyecto | Framework | Para qué |
|---|---|---|
| Netflix | FastAPI | Microservicios internos |
| Uber | Django | Backend de operaciones |
| Instagram | Django | Backend original |
| Spotify | Flask/FastAPI | Servicios de música |
| Dropbox | Python | Backend de almacenamiento |

---

## Comparación directa con el proyecto Java

Este proyecto es equivalente al proyecto **Biblioteca Digital** en Java/Spring Boot,
pero construido con Python/FastAPI. Las mismas ideas, diferente sintaxis:

| Concepto | Biblioteca (Java) | TaskFlow (Python) |
|---|---|---|
| Inicio | `@SpringBootApplication` | `uvicorn app.main:app` |
| Controller | `@RestController` | `APIRouter` |
| Endpoint | `@GetMapping("/libros")` | `@router.get("/libros")` |
| Body request | `@RequestBody LibroDTO` | `libro: LibroCreate` |
| Validación | `@Valid @NotNull @Size` | `Field(..., min_length=3)` |
| Seguridad | `@PreAuthorize("hasRole...")` | `Depends(require_admin)` |
| BD query | `libroRepo.findById(id)` | `db.query(Libro).filter(...).first()` |
| Datos prueba | `DataInitializer.java` | `data_initializer.py` |
| JWT | jjwt library | python-jose library |
| Docs API | Springdoc + Swagger | FastAPI nativo |

---

*Proyecto educativo creado para aprender desarrollo backend con Python.*
*Stack equivalente al proyecto Java Spring Boot: Biblioteca Digital.*
