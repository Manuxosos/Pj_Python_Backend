# ShopFlow API — Backend de Tienda Online

> Backend completo de un e-commerce real, construido con **FastAPI + SQLAlchemy**.
> Diseñado para conectarse con un frontend React en el futuro.

---

## Qué es este proyecto

Una API REST que alimenta una tienda online. Imagina que es el backend de una tienda como Zara o MediaMarkt:

- **Catálogo de productos** con filtros, búsqueda y paginación
- **Carrito de compra** persistente en base de datos
- **Proceso de checkout** transaccional (todo o nada)
- **Gestión de pedidos** con estados (Pendiente → Enviado → Entregado)
- **Autenticación JWT** con roles (ADMIN / CLIENTE)

El frontend (React/Vue) aún no existe. **Este es exactamente el momento correcto para empezar**: primero el backend, luego el frontend.

---

## Instalación y ejecución

```bash
# 1. Clonar
git clone https://github.com/Manuxosos/Pj_Python_Backend.git
cd Pj_Python_Backend

# 2. Entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env

# 5. Arrancar
uvicorn app.main:app --reload
```

Cuando veas esto, el servidor está listo:
```
🚀 Servidor listo: http://localhost:8000
📚 Swagger UI:    http://localhost:8000/docs
```

---

## Cómo explorar la API

1. Abre **http://localhost:8000/docs**
2. En `POST /api/auth/login`, prueba con `admin@shopflow.com` / `Admin1234`
3. Copia el `access_token` de la respuesta
4. Haz clic en el botón **Authorize** 🔒 → pega el token
5. Ya tienes acceso a todos los endpoints

**Usuarios de prueba:**

| Email | Password | Rol | Estado |
|-------|----------|-----|--------|
| `admin@shopflow.com` | `Admin1234` | ADMIN | — |
| `cliente1@email.com` | `Cliente1234` | CLIENTE | Tiene carrito con 3 items |
| `cliente2@email.com` | `Cliente1234` | CLIENTE | Tiene 1 pedido entregado |

---

## Estructura del proyecto

```
app/
├── main.py                  ← Punto de entrada, registra todo
├── config/
│   ├── settings.py          ← Configuración (como application.properties)
│   └── database.py          ← Conexión a la BD (Engine + Session)
├── models/                  ← Tablas de la BD (SQLAlchemy ORM)
│   ├── usuario.py           ← Tabla usuarios + enum RolUsuario
│   ├── categoria.py         ← Tabla categorias
│   ├── producto.py          ← Tabla productos (precio, stock, descuento)
│   ├── carrito.py           ← Tablas carritos + carrito_items
│   └── pedido.py            ← Tablas pedidos + pedido_items
├── schemas/                 ← DTOs (validación y serialización JSON)
│   ├── auth.py
│   ├── usuario.py
│   ├── categoria.py
│   ├── producto.py          ← Incluye campos calculados: precio_final, %descuento
│   ├── carrito.py
│   └── pedido.py
├── routers/                 ← Endpoints HTTP (controllers)
│   ├── auth.py              ← /api/auth/login, /registro, /me
│   ├── usuarios.py          ← /api/usuarios/ (CRUD admin)
│   ├── categorias.py        ← /api/categorias/ (público para GET)
│   ├── productos.py         ← /api/productos/ (catálogo público + CRUD admin)
│   ├── carrito.py           ← /api/carrito/ (carrito del usuario)
│   └── pedidos.py           ← /api/pedidos/ (checkout + historial)
├── services/                ← Lógica de negocio
│   ├── auth_service.py      ← Login, hashing, JWT
│   ├── usuario_service.py   ← Registro, CRUD
│   ├── categoria_service.py
│   ├── producto_service.py  ← Catálogo con filtros
│   ├── carrito_service.py   ← Gestión del carrito
│   └── pedido_service.py    ← Checkout transaccional
├── security/
│   ├── jwt.py               ← Crear/verificar tokens JWT
│   └── dependencies.py      ← Dependencias de autenticación/autorización
├── utils/
│   └── data_initializer.py  ← Datos de prueba al iniciar
└── exceptions/
    └── handlers.py          ← Manejo global de errores
```

---

## Endpoints de la API

### Públicos (sin autenticación)
```
POST   /api/auth/login                  → Iniciar sesión
POST   /api/auth/registro               → Crear cuenta de cliente
GET    /api/categorias/                 → Listar categorías (menú de la tienda)
GET    /api/productos/                  → Catálogo con filtros
GET    /api/productos/{id}              → Detalle de producto
```

### Cliente (requieren JWT)
```
GET    /api/auth/me                     → Mi perfil
GET    /api/carrito/                    → Ver mi carrito
POST   /api/carrito/items               → Añadir producto al carrito
PUT    /api/carrito/items/{producto_id} → Cambiar cantidad
DELETE /api/carrito/items/{producto_id} → Quitar producto
DELETE /api/carrito/                    → Vaciar carrito
POST   /api/pedidos/                    → Confirmar pedido (checkout)
GET    /api/pedidos/mis-pedidos         → Mi historial de compras
GET    /api/pedidos/{id}                → Ver detalle de pedido
```

### Admin (requieren JWT + rol ADMIN)
```
GET    /api/usuarios/                   → Listar clientes
POST   /api/productos/                  → Añadir producto al catálogo
PUT    /api/productos/{id}              → Actualizar producto/precio/stock
DELETE /api/productos/{id}              → Eliminar producto
POST   /api/categorias/                 → Crear categoría
PATCH  /api/pedidos/{id}/estado         → Gestionar estado del pedido
GET    /api/pedidos/                    → Ver todos los pedidos
```

### Filtros del catálogo
```
GET /api/productos/?categoria_id=1&busqueda=iphone&min_precio=500&max_precio=2000&orden=precio_asc
GET /api/productos/?solo_destacados=true     → Para el home de la tienda
GET /api/productos/?solo_disponibles=true    → Solo con stock
```

---

## La base de datos

```
usuarios ←─── carritos ←─── carrito_items ───→ productos ←─── categorias
    │                                                │
    └────────────────── pedidos ←─── pedido_items ──┘
```

**Tablas:**
- `usuarios` — Cuentas de admin y clientes
- `categorias` — Electrónica, Ropa, Hogar...
- `productos` — Catálogo con precio, stock, imagen
- `carritos` — Un carrito por usuario (relación 1:1)
- `carrito_items` — Productos y cantidades en el carrito
- `pedidos` — Histórico de compras
- `pedido_items` — Snapshot de producto+precio en el momento de compra

---
---

# PRODUCCIÓN Y CONEXIÓN CON FRONTEND

## ¿Cómo funciona un proyecto backend en el mundo real?

En el mundo laboral, un proyecto backend pasa por estas etapas:

```
[Planificación] → [Desarrollo] → [Testing] → [Staging] → [Producción]
```

Vamos a explicar cada una con ejemplos reales.

---

## Etapa 1: Diseño del contrato API (API First)

Antes de escribir código, el equipo de backend y frontend se reúne y **acuerda los endpoints**.

```
Reunión de equipo:
  Backend: "El endpoint de productos devolverá esto:"
  {
    "id": 1,
    "nombre": "iPhone 15 Pro",
    "precio_final": 1099.00,
    "tiene_descuento": true,
    "porcentaje_descuento": 10.5
  }

  Frontend: "Perfecto, necesito también 'disponible' para deshabilitar el botón de compra"

  Backend: "Añadido. Empezamos a desarrollar en paralelo."
```

**Esto es "API First"**: el contrato (la especificación OpenAPI/Swagger) se diseña primero.
Así el frontend puede mockear los datos y trabajar sin esperar al backend.

---

## Etapa 2: El backend se desarrolla primero

Normalmente el backend va adelante porque:
- Define la estructura de datos
- Crea la base de datos
- Establece las reglas de negocio (quién puede comprar qué, cuándo)

**El frontend empieza cuando los primeros endpoints están listos**, no cuando todo está terminado.

Flujo típico de un sprint de 2 semanas:
```
Semana 1:
  Backend: Entidades + Auth + Catálogo de productos (endpoints básicos)
  Frontend: Diseño en Figma, setup del proyecto React

Semana 2:
  Backend: Carrito + Pedidos
  Frontend: Integra los endpoints del catálogo (ya disponibles)

Final del sprint:
  Pruebas de integración end-to-end
```

---

## Etapa 3: Cómo se conecta con el frontend (React)

El frontend (React/Vue/Angular) hace peticiones HTTP a esta API.

### Ejemplo en React con fetch:

```jsx
// Cargar el catálogo de productos
const [productos, setProductos] = useState([]);

useEffect(() => {
  fetch("http://localhost:8000/api/productos/?solo_destacados=true")
    .then(res => res.json())
    .then(data => setProductos(data));
}, []);

// Mostrar en la UI
return (
  <div>
    {productos.map(producto => (
      <ProductoCard
        key={producto.id}
        nombre={producto.nombre}
        precio={producto.precio_final}
        descuento={producto.porcentaje_descuento}
        imagen={producto.imagen_url}
      />
    ))}
  </div>
);
```

### Ejemplo de login con JWT:

```jsx
async function login(email, password) {
  const respuesta = await fetch("http://localhost:8000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const datos = await respuesta.json();

  // Guardar el token en localStorage (o en una cookie httpOnly más seguro)
  localStorage.setItem("token", datos.access_token);
}

// Usar el token en peticiones protegidas
async function verMiCarrito() {
  const token = localStorage.getItem("token");

  const respuesta = await fetch("http://localhost:8000/api/carrito/", {
    headers: {
      "Authorization": `Bearer ${token}`  // ← Así se envía el JWT
    }
  });

  return respuesta.json();
}
```

### Ejemplo de añadir al carrito:

```jsx
async function añadirAlCarrito(productoId, cantidad = 1) {
  const token = localStorage.getItem("token");

  const respuesta = await fetch("http://localhost:8000/api/carrito/items", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ producto_id: productoId, cantidad })
  });

  const carritoActualizado = await respuesta.json();
  // Actualizar el badge del carrito en el header: "🛒 (3)"
  setTotalItemsCarrito(carritoActualizado.total_items);
}
```

### Ejemplo de checkout:

```jsx
async function confirmarPedido(direccion, notas) {
  const token = localStorage.getItem("token");

  const respuesta = await fetch("http://localhost:8000/api/pedidos/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      direccion_envio: direccion,
      notas: notas
    })
  });

  if (respuesta.ok) {
    const pedido = await respuesta.json();
    // Redirigir a la página de confirmación
    navigate(`/pedido-confirmado/${pedido.id}`);
  }
}
```

---

## Etapa 4: Entornos de despliegue

En un proyecto real existen **3 entornos**:

```
┌──────────────────────────────────────────────────────────┐
│  LOCAL (tu ordenador)                                    │
│  python uvicorn app.main:app --reload                    │
│  Base de datos: SQLite                                   │
│  URL: http://localhost:8000                              │
└──────────────────────┬───────────────────────────────────┘
                       │ git push
┌──────────────────────▼───────────────────────────────────┐
│  STAGING (servidor de pruebas)                           │
│  URL: https://api-staging.tutienda.com                   │
│  Base de datos: PostgreSQL de pruebas                    │
│  Aquí se prueban los cambios antes de producción         │
└──────────────────────┬───────────────────────────────────┘
                       │ después de validar
┌──────────────────────▼───────────────────────────────────┐
│  PRODUCCIÓN (servidor real, usuarios reales)             │
│  URL: https://api.tutienda.com                           │
│  Base de datos: PostgreSQL en la nube (AWS RDS, etc.)    │
│  NUNCA se despliega código sin pasar por staging         │
└──────────────────────────────────────────────────────────┘
```

### Variables de entorno por entorno:

```bash
# Local (.env)
DATABASE_URL=sqlite:///./shopflow.db
DEBUG=True
SECRET_KEY=clave-de-desarrollo-no-importa

# Producción (variables del servidor, NUNCA en el repo)
DATABASE_URL=postgresql://user:pass@db.aws.com:5432/shopflow_prod
DEBUG=False
SECRET_KEY=clave-aleatoria-de-64-caracteres-muy-segura
```

---

## Etapa 5: De SQLite a PostgreSQL (producción)

En desarrollo usamos SQLite porque es simple (un solo archivo).
En producción se usa PostgreSQL porque:
- Soporta múltiples conexiones simultáneas
- Tiene mejor rendimiento con millones de registros
- Permite backups automáticos
- Es transaccional y ACID compliant

**Cambiar de SQLite a PostgreSQL: solo 1 línea en `.env`**
```bash
# Instalar driver
pip install psycopg2-binary

# Cambiar en .env
DATABASE_URL=postgresql://usuario:password@localhost:5432/shopflow
```

El código de la aplicación NO cambia. Eso es la ventaja del ORM.

---

## Etapa 6: Docker (contenedores)

En producción, el backend y la base de datos corren en contenedores Docker.

```yaml
# docker-compose.yml (ejemplo de cómo sería)
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:pass@db:5432/shopflow
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=shopflow
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  frontend:
    build: ./frontend  # El proyecto React
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://api:8000
```

Con un solo comando arranca todo:
```bash
docker-compose up
```

---

## Etapa 7: CI/CD (Integración y despliegue continuos)

En empresas reales existe un pipeline automático:

```
git push origin main
        ↓
  [GitHub Actions]
        ↓
  Ejecutar tests
        ↓
  ¿Tests ok?  →  NO → Notificación al developer. Deploy CANCELADO.
        ↓ SÍ
  Build de Docker
        ↓
  Deploy automático a Staging
        ↓
  Tests end-to-end en Staging
        ↓
  ¿Todo ok? → Aprobación manual del tech lead
        ↓
  Deploy a Producción
```

---

## Cuándo empieza el frontend

**No hay una regla fija**, pero el patrón más común en equipos ágiles:

| Momento | Estado del backend | Qué hace el frontend |
|---------|-------------------|---------------------|
| Día 1 | Solo las entidades diseñadas | Setup del proyecto React, diseño en Figma |
| Semana 1 | Auth + Catálogo de productos listos | Integra login y listado de productos |
| Semana 2 | Carrito + Pedidos listos | Integra carrito y checkout |
| Semana 3 | Todo completo | Pulir UX, tests, ajustes |

**La clave**: el frontend no espera a que TODO el backend esté listo. Trabaja con los endpoints disponibles y usa **mock data** para el resto.

```javascript
// Mientras el endpoint /api/pedidos/ no está listo, el frontend usa datos falsos:
const MOCK_PEDIDOS = [
  { id: 1, estado: "ENTREGADO", total: 299.99, created_at: "2024-01-15" }
];

// Cuando el backend lo implementa, solo cambia esta línea:
const pedidos = await fetch("/api/pedidos/mis-pedidos").then(r => r.json());
```

---

## El frontend que conectaría con esta API

La interfaz de usuario (que aún no existe) tendría estas páginas:

```
/ (Home)
  - Hero con productos destacados
  - Llama: GET /api/productos/?solo_destacados=true

/productos (Catálogo)
  - Grid de productos con filtros laterales
  - Llama: GET /api/productos/?categoria_id=X&min_precio=Y&busqueda=Z

/productos/:id (Detalle)
  - Foto, descripción, precio, botón "Añadir al carrito"
  - Llama: GET /api/productos/{id}
  - Al pulsar el botón: POST /api/carrito/items

/carrito (Carrito)
  - Lista de items con cantidades editables y total
  - Llama: GET /api/carrito/

/checkout (Confirmación de pedido)
  - Formulario de dirección + resumen del pedido
  - Al confirmar: POST /api/pedidos/

/mis-pedidos (Mi cuenta)
  - Historial de compras
  - Llama: GET /api/pedidos/mis-pedidos

/admin (Panel de administración)
  - Gestión de productos, categorías y pedidos
  - Solo accesible con rol ADMIN
```

---

## Resumen: Ciclo completo de desarrollo

```
1. DISEÑO
   Backend + Frontend deciden juntos los endpoints y los JSON
   Herramienta: OpenAPI spec, Swagger, Notion

2. BACKEND PRIMERO
   Models → Schemas → Services → Routers
   Pruebas con Swagger UI
   Base de datos: SQLite local

3. FRONTEND EN PARALELO (cuando hay endpoints básicos)
   Setup React + React Router + Axios/Fetch
   Componentes de UI
   Integración con la API real

4. TESTING
   Backend: pytest (tests de endpoints)
   Frontend: Jest + React Testing Library
   End-to-end: Playwright o Cypress

5. STAGING
   Deploy en servidor de pruebas
   Base de datos PostgreSQL
   URL: api-staging.tutienda.com

6. PRODUCCIÓN
   Deploy con Docker + CI/CD
   Monitoreo: logs, métricas, alertas
   URL: api.tutienda.com
```

---

*ShopFlow API — Proyecto educativo de backend Python con FastAPI.*
*Próximo paso: añadir el frontend con React.*
