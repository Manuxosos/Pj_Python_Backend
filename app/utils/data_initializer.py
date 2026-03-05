"""
INICIALIZADOR DE DATOS
========================
Equivale al DataInitializer.java de Spring Boot (@Component + CommandLineRunner).

Se ejecuta al arrancar la aplicación y crea datos de prueba
si la base de datos está vacía.

DATOS CREADOS:
  Usuarios:
    - admin@taskflow.com      / Admin1234     (ADMIN)
    - laura@taskflow.com      / Manager1234   (MANAGER)
    - roberto@taskflow.com    / Manager1234   (MANAGER)
    - carlos@taskflow.com     / Dev1234       (DESARROLLADOR)
    - ana@taskflow.com        / Dev1234       (DESARROLLADOR)
    - miguel@taskflow.com     / Dev1234       (DESARROLLADOR)

  Proyectos:
    - Portal de Clientes (ACTIVO)
    - App Móvil Interna (EN_PAUSA)
    - Microservicios Backend (PLANIFICACION)

  Tareas con varios estados y prioridades
  Comentarios en las tareas
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.usuario import Usuario, RolUsuario
from app.models.proyecto import Proyecto, EstadoProyecto
from app.models.tarea import Tarea, EstadoTarea, PrioridadTarea
from app.models.comentario import Comentario
from app.services.auth_service import hash_password


def inicializar_datos(db: Session) -> None:
    """
    Crea datos de prueba si no existen usuarios en la BD.
    Es idempotente: si ya hay datos, no hace nada.
    """

    # Si ya hay usuarios, no hacer nada
    if db.query(Usuario).count() > 0:
        print("✅ Base de datos ya contiene datos. Saltando inicialización.")
        return

    print("🚀 Inicializando base de datos con datos de prueba...")

    # ==============================================================
    # 1. CREAR USUARIOS
    # ==============================================================
    admin = Usuario(
        email="admin@taskflow.com",
        nombre="Administrador Sistema",
        hashed_password=hash_password("Admin1234"),
        rol=RolUsuario.ADMIN
    )

    laura = Usuario(
        email="laura@taskflow.com",
        nombre="Laura Martínez",
        hashed_password=hash_password("Manager1234"),
        rol=RolUsuario.MANAGER
    )

    roberto = Usuario(
        email="roberto@taskflow.com",
        nombre="Roberto Sánchez",
        hashed_password=hash_password("Manager1234"),
        rol=RolUsuario.MANAGER
    )

    carlos = Usuario(
        email="carlos@taskflow.com",
        nombre="Carlos López",
        hashed_password=hash_password("Dev1234"),
        rol=RolUsuario.DESARROLLADOR
    )

    ana = Usuario(
        email="ana@taskflow.com",
        nombre="Ana García",
        hashed_password=hash_password("Dev1234"),
        rol=RolUsuario.DESARROLLADOR
    )

    miguel = Usuario(
        email="miguel@taskflow.com",
        nombre="Miguel Torres",
        hashed_password=hash_password("Dev1234"),
        rol=RolUsuario.DESARROLLADOR
    )

    db.add_all([admin, laura, roberto, carlos, ana, miguel])
    db.commit()

    # ==============================================================
    # 2. CREAR PROYECTOS
    # ==============================================================
    ahora = datetime.now(timezone.utc)

    proyecto1 = Proyecto(
        nombre="Portal de Clientes B2B",
        descripcion="Sistema web completo para gestión de clientes empresariales. "
                    "Incluye autenticación, dashboard, reportes y API REST.",
        estado=EstadoProyecto.ACTIVO,
        fecha_inicio=ahora - timedelta(days=30),
        fecha_fin_estimada=ahora + timedelta(days=90),
        owner_id=laura.id
    )

    proyecto2 = Proyecto(
        nombre="App Móvil para Empleados",
        descripcion="Aplicación móvil (iOS y Android) para que los empleados "
                    "gestionen sus tareas, vacaciones y nóminas.",
        estado=EstadoProyecto.EN_PAUSA,
        fecha_inicio=ahora - timedelta(days=60),
        fecha_fin_estimada=ahora + timedelta(days=120),
        owner_id=roberto.id
    )

    proyecto3 = Proyecto(
        nombre="Migración a Microservicios",
        descripcion="Refactorización del monolito existente a arquitectura de "
                    "microservicios con Docker y Kubernetes.",
        estado=EstadoProyecto.PLANIFICACION,
        fecha_inicio=ahora + timedelta(days=15),
        fecha_fin_estimada=ahora + timedelta(days=180),
        owner_id=laura.id
    )

    db.add_all([proyecto1, proyecto2, proyecto3])
    db.commit()

    # ==============================================================
    # 3. CREAR TAREAS
    # ==============================================================
    tareas = [
        # --- Proyecto 1: Portal de Clientes ---
        Tarea(
            titulo="Diseño del sistema de autenticación JWT",
            descripcion="Implementar login con JWT, refresh tokens y manejo de sesiones.",
            estado=EstadoTarea.COMPLETADA,
            prioridad=PrioridadTarea.CRITICA,
            proyecto_id=proyecto1.id,
            asignado_a_id=carlos.id,
            creado_por_id=laura.id,
            fecha_limite=ahora - timedelta(days=10),
            fecha_completada=ahora - timedelta(days=12)
        ),
        Tarea(
            titulo="Implementar dashboard de métricas",
            descripcion="Panel con gráficos de ventas, usuarios activos y KPIs principales.",
            estado=EstadoTarea.EN_PROGRESO,
            prioridad=PrioridadTarea.ALTA,
            proyecto_id=proyecto1.id,
            asignado_a_id=ana.id,
            creado_por_id=laura.id,
            fecha_limite=ahora + timedelta(days=7)
        ),
        Tarea(
            titulo="Integración con CRM externo",
            descripcion="Conectar con Salesforce API para sincronizar datos de clientes.",
            estado=EstadoTarea.PENDIENTE,
            prioridad=PrioridadTarea.MEDIA,
            proyecto_id=proyecto1.id,
            asignado_a_id=miguel.id,
            creado_por_id=laura.id,
            fecha_limite=ahora + timedelta(days=21)
        ),
        Tarea(
            titulo="Pruebas de rendimiento y carga",
            descripcion="Tests con Locust para validar que el sistema soporta 1000 usuarios simultáneos.",
            estado=EstadoTarea.PENDIENTE,
            prioridad=PrioridadTarea.ALTA,
            proyecto_id=proyecto1.id,
            asignado_a_id=carlos.id,
            creado_por_id=laura.id,
            fecha_limite=ahora + timedelta(days=45)
        ),

        # --- Proyecto 2: App Móvil ---
        Tarea(
            titulo="Definir wireframes de la aplicación",
            descripcion="Crear prototipos de las pantallas principales en Figma.",
            estado=EstadoTarea.COMPLETADA,
            prioridad=PrioridadTarea.ALTA,
            proyecto_id=proyecto2.id,
            asignado_a_id=ana.id,
            creado_por_id=roberto.id,
            fecha_completada=ahora - timedelta(days=20)
        ),
        Tarea(
            titulo="Setup del proyecto React Native",
            descripcion="Configurar el proyecto con TypeScript, navegación y estado global.",
            estado=EstadoTarea.EN_REVISION,
            prioridad=PrioridadTarea.MEDIA,
            proyecto_id=proyecto2.id,
            asignado_a_id=miguel.id,
            creado_por_id=roberto.id
        ),

        # --- Proyecto 3: Microservicios ---
        Tarea(
            titulo="Análisis del monolito actual",
            descripcion="Mapear todos los módulos del sistema y sus dependencias.",
            estado=EstadoTarea.PENDIENTE,
            prioridad=PrioridadTarea.ALTA,
            proyecto_id=proyecto3.id,
            asignado_a_id=carlos.id,
            creado_por_id=laura.id
        ),
    ]

    db.add_all(tareas)
    db.commit()

    # ==============================================================
    # 4. CREAR COMENTARIOS
    # ==============================================================
    comentarios = [
        Comentario(
            contenido="He implementado el sistema JWT con refresh tokens. "
                      "Los tokens de acceso duran 30 min y los refresh 7 días.",
            tarea_id=tareas[0].id,
            autor_id=carlos.id
        ),
        Comentario(
            contenido="Code review completado. Todo correcto. "
                      "Marcando como completada. ✅",
            tarea_id=tareas[0].id,
            autor_id=laura.id
        ),
        Comentario(
            contenido="Empezando con los gráficos de ventas usando Chart.js. "
                      "¿Alguien ha usado Recharts? ¿Lo recomendáis?",
            tarea_id=tareas[1].id,
            autor_id=ana.id
        ),
        Comentario(
            contenido="Yo usé Recharts en el proyecto anterior, funciona genial con React.",
            tarea_id=tareas[1].id,
            autor_id=carlos.id
        ),
        Comentario(
            contenido="Los wireframes están en Figma: [link]. "
                      "Incluye flujo de login, home, tareas y perfil.",
            tarea_id=tareas[4].id,
            autor_id=ana.id
        ),
    ]

    db.add_all(comentarios)
    db.commit()

    print("✅ Base de datos inicializada correctamente!")
    print("\n📋 Usuarios creados:")
    print("   admin@taskflow.com    / Admin1234    (ADMIN)")
    print("   laura@taskflow.com    / Manager1234  (MANAGER)")
    print("   roberto@taskflow.com  / Manager1234  (MANAGER)")
    print("   carlos@taskflow.com   / Dev1234      (DESARROLLADOR)")
    print("   ana@taskflow.com      / Dev1234      (DESARROLLADOR)")
    print("   miguel@taskflow.com   / Dev1234      (DESARROLLADOR)")
    print(f"\n📁 Proyectos creados: 3")
    print(f"✅ Tareas creadas: {len(tareas)}")
    print(f"💬 Comentarios creados: {len(comentarios)}")
