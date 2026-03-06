"""
INICIALIZADOR DE DATOS
========================
Crea datos de prueba al iniciar la aplicación por primera vez.

DATOS CREADOS:
  Usuarios:
    - admin@shopflow.com    / Admin1234    (ADMIN)
    - cliente1@email.com   / Cliente1234  (CLIENTE)
    - cliente2@email.com   / Cliente1234  (CLIENTE)

  Categorías: Electrónica, Ropa, Hogar, Deportes, Libros

  Productos (varios por categoría, algunos con descuento)

  Carrito de cada cliente con algunos productos añadidos

  Un pedido de ejemplo
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.usuario import Usuario, RolUsuario
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.carrito import Carrito, CarritoItem
from app.models.pedido import Pedido, PedidoItem, EstadoPedido
from app.services.auth_service import hash_password


def inicializar_datos(db: Session) -> None:
    """Idempotente: si ya hay datos, no hace nada."""
    if db.query(Usuario).count() > 0:
        print("✅ Base de datos ya contiene datos.")
        return

    print("🚀 Inicializando base de datos con datos de prueba...")

    # ==============================================================
    # 1. USUARIOS
    # ==============================================================
    admin = Usuario(
        email="admin@shopflow.com",
        nombre="Admin",
        apellido="ShopFlow",
        hashed_password=hash_password("Admin1234"),
        rol=RolUsuario.ADMIN
    )
    cliente1 = Usuario(
        email="cliente1@email.com",
        nombre="María",
        apellido="García",
        hashed_password=hash_password("Cliente1234"),
        rol=RolUsuario.CLIENTE
    )
    cliente2 = Usuario(
        email="cliente2@email.com",
        nombre="Carlos",
        apellido="López",
        hashed_password=hash_password("Cliente1234"),
        rol=RolUsuario.CLIENTE
    )
    db.add_all([admin, cliente1, cliente2])
    db.flush()

    # Crear carritos vacíos para los clientes
    carrito1 = Carrito(usuario_id=cliente1.id)
    carrito2 = Carrito(usuario_id=cliente2.id)
    db.add_all([carrito1, carrito2])

    # ==============================================================
    # 2. CATEGORÍAS
    # ==============================================================
    electronica = Categoria(nombre="Electrónica", descripcion="Tecnología y dispositivos", icono="laptop")
    ropa = Categoria(nombre="Ropa", descripcion="Moda y complementos", icono="shirt")
    hogar = Categoria(nombre="Hogar", descripcion="Para tu casa", icono="home")
    deportes = Categoria(nombre="Deportes", descripcion="Equipación y material deportivo", icono="dumbbell")
    libros = Categoria(nombre="Libros", descripcion="Libros y ebooks", icono="book")
    db.add_all([electronica, ropa, hogar, deportes, libros])
    db.flush()

    # ==============================================================
    # 3. PRODUCTOS
    # ==============================================================
    productos = [
        # --- Electrónica ---
        Producto(
            nombre="MacBook Pro M3 14\"",
            descripcion="El portátil más potente de Apple. Chip M3, 18GB RAM, 512GB SSD, batería de 18h.",
            precio=2199.99,
            stock=15,
            imagen_url="https://store.storeimages.cdn-apple.com/macbook-pro.jpg",
            categoria_id=electronica.id,
            destacado=True
        ),
        Producto(
            nombre="iPhone 15 Pro 256GB",
            descripcion="Titanio. Chip A17 Pro. Sistema de cámaras Pro de 48MP. USB-C.",
            precio=1229.00,
            precio_descuento=1099.00,  # En oferta
            stock=30,
            imagen_url="https://store.storeimages.cdn-apple.com/iphone15pro.jpg",
            categoria_id=electronica.id,
            destacado=True
        ),
        Producto(
            nombre='Samsung Galaxy S24 Ultra 512GB',
            descripcion="6.8\" AMOLED, 200MP, S Pen integrado, batería 5000mAh.",
            precio=1399.00,
            stock=20,
            imagen_url="https://images.samsung.com/galaxy-s24-ultra.jpg",
            categoria_id=electronica.id
        ),
        Producto(
            nombre="AirPods Pro 2ª generación",
            descripcion="Cancelación activa de ruido. Audio espacial personalizado. Chip H2.",
            precio=279.00,
            precio_descuento=249.00,
            stock=50,
            imagen_url="https://store.storeimages.cdn-apple.com/airpods-pro.jpg",
            categoria_id=electronica.id,
            destacado=True
        ),
        Producto(
            nombre="Sony WH-1000XM5",
            descripcion="Los mejores auriculares con cancelación de ruido del mercado. 30h batería.",
            precio=349.99,
            stock=25,
            categoria_id=electronica.id
        ),
        Producto(
            nombre='Monitor LG UltraWide 34"',
            descripcion='34" Curved WQHD 3440x1440, 144Hz, HDR10, 1ms, USB-C 90W.',
            precio=599.99,
            precio_descuento=499.99,
            stock=10,
            categoria_id=electronica.id
        ),

        # --- Ropa ---
        Producto(
            nombre="Zapatillas Nike Air Max 90",
            descripcion="Icónicas zapatillas con amortiguación Air. Tallas 36-47.",
            precio=129.99,
            precio_descuento=99.99,
            stock=100,
            categoria_id=ropa.id,
            destacado=True
        ),
        Producto(
            nombre="Camiseta Levi's Original",
            descripcion="100% algodón. Corte recto. Disponible en blanco, negro y azul marino.",
            precio=29.99,
            stock=200,
            categoria_id=ropa.id
        ),
        Producto(
            nombre="Vaqueros Levi's 501 Original",
            descripcion="El vaquero clásico desde 1873. Corte recto. Tallas 28-40.",
            precio=99.99,
            precio_descuento=79.99,
            stock=80,
            categoria_id=ropa.id
        ),

        # --- Hogar ---
        Producto(
            nombre="Robot Aspirador Roomba j9+",
            descripcion="Aspirado y fregado. Vaciado automático. Compatible con Alexa y Google.",
            precio=799.99,
            stock=12,
            categoria_id=hogar.id,
            destacado=True
        ),
        Producto(
            nombre="Cafetera Nespresso Vertuo",
            descripcion="Café barista en casa. Compatible con cápsulas Vertuo. 1500W.",
            precio=149.99,
            precio_descuento=119.99,
            stock=35,
            categoria_id=hogar.id
        ),

        # --- Deportes ---
        Producto(
            nombre="Bicicleta de montaña Trek Marlin 5",
            descripcion="Cuadro aluminio Alpha Gold. Horquilla SR Suntour XCT. 21 velocidades.",
            precio=649.99,
            stock=8,
            categoria_id=deportes.id
        ),
        Producto(
            nombre="Esterilla de Yoga Manduka PRO",
            descripcion="La esterilla más usada por instructores de yoga. 6mm. 100% libre de PVC.",
            precio=129.99,
            precio_descuento=99.99,
            stock=40,
            categoria_id=deportes.id
        ),

        # --- Libros ---
        Producto(
            nombre="Clean Code - Robert C. Martin",
            descripcion="El manual definitivo para escribir código limpio y mantenible.",
            precio=39.99,
            stock=60,
            categoria_id=libros.id,
            destacado=True
        ),
        Producto(
            nombre="Diseño de Sistemas (System Design Interview)",
            descripcion="Aprende a diseñar sistemas escalables como lo hacen en Google y Amazon.",
            precio=44.99,
            stock=45,
            categoria_id=libros.id
        ),
        Producto(
            nombre="Python Crash Course",
            descripcion="La guía más completa para aprender Python desde cero.",
            precio=34.99,
            precio_descuento=27.99,
            stock=70,
            categoria_id=libros.id
        ),
    ]

    db.add_all(productos)
    db.flush()

    # ==============================================================
    # 4. AÑADIR ITEMS AL CARRITO DE CLIENTE1
    # ==============================================================
    # Simular que cliente1 tiene productos en su carrito
    iphone = next(p for p in productos if "iPhone" in p.nombre)
    airpods = next(p for p in productos if "AirPods" in p.nombre)
    clean_code = next(p for p in productos if "Clean Code" in p.nombre)

    db.add_all([
        CarritoItem(carrito_id=carrito1.id, producto_id=iphone.id, cantidad=1),
        CarritoItem(carrito_id=carrito1.id, producto_id=airpods.id, cantidad=1),
        CarritoItem(carrito_id=carrito1.id, producto_id=clean_code.id, cantidad=2),
    ])

    # ==============================================================
    # 5. CREAR UN PEDIDO COMPLETADO DE CLIENTE2
    # ==============================================================
    macbook = next(p for p in productos if "MacBook" in p.nombre)
    python_book = next(p for p in productos if "Python" in p.nombre)

    pedido = Pedido(
        usuario_id=cliente2.id,
        total=round(macbook.precio_final + python_book.precio_final * 2, 2),
        estado=EstadoPedido.ENTREGADO,
        direccion_envio="Calle Mayor 15, 3ºB, 28001 Madrid, España"
    )
    db.add(pedido)
    db.flush()

    db.add_all([
        PedidoItem(
            pedido_id=pedido.id,
            producto_id=macbook.id,
            cantidad=1,
            precio_unitario=macbook.precio_final,
            nombre_producto=macbook.nombre
        ),
        PedidoItem(
            pedido_id=pedido.id,
            producto_id=python_book.id,
            cantidad=2,
            precio_unitario=python_book.precio_final,
            nombre_producto=python_book.nombre
        ),
    ])

    db.commit()

    print("✅ Base de datos inicializada correctamente!")
    print("\n👤 Usuarios creados:")
    print("   admin@shopflow.com    / Admin1234    (ADMIN)")
    print("   cliente1@email.com   / Cliente1234  (CLIENTE) ← tiene carrito con 3 items")
    print("   cliente2@email.com   / Cliente1234  (CLIENTE) ← tiene 1 pedido ENTREGADO")
    print(f"\n📂 Categorías: 5  |  🛍️ Productos: {len(productos)}  |  📦 Pedidos: 1")
