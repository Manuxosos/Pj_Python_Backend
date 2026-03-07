@echo off
title ShopFlow API - Entorno de Aprendizaje Python
color 0A

echo.
echo  ==========================================
echo   ShopFlow API - Entorno de Aprendizaje
echo  ==========================================
echo.

:: -----------------------------------------------
:: PASO 1: Verificar que Python esta instalado
:: -----------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado.
    echo.
    echo  Descargalo desde: https://www.python.org/downloads/
    echo  Asegurate de marcar "Add Python to PATH" al instalar.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado.

:: -----------------------------------------------
:: PASO 2: Crear el entorno virtual si no existe
:: -----------------------------------------------
if not exist "venv\" (
    echo [..] Creando entorno virtual por primera vez...
    python -m venv venv
    echo [OK] Entorno virtual creado.
) else (
    echo [OK] Entorno virtual encontrado.
)

:: -----------------------------------------------
:: PASO 3: Activar el entorno virtual
:: -----------------------------------------------
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado.

:: -----------------------------------------------
:: PASO 4: Instalar dependencias si faltan
:: -----------------------------------------------
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [..] Instalando dependencias (solo la primera vez, espera un momento)...
    pip install -r requirements.txt --quiet
    echo [OK] Dependencias instaladas.
) else (
    echo [OK] Dependencias ya instaladas.
)

:: -----------------------------------------------
:: PASO 5: Crear .env si no existe
:: -----------------------------------------------
if not exist ".env" (
    copy .env.example .env >nul
    echo [OK] Archivo .env creado desde .env.example.
) else (
    echo [OK] Archivo .env encontrado.
)

:: -----------------------------------------------
:: PASO 6: Abrir el navegador despues de 4 segundos
:: (tiempo para que el servidor arranque)
:: -----------------------------------------------
echo.
echo  Arrancando servidor...
echo  El navegador se abrira automaticamente en unos segundos.
echo.
echo  Para DETENER el servidor presiona: Ctrl + C
echo  ==========================================
echo.

start /B cmd /c "timeout /t 5 >nul && start http://localhost:8000/docs"

:: -----------------------------------------------
:: PASO 7: Arrancar el servidor (queda en primer plano)
:: -----------------------------------------------
uvicorn app.main:app --reload
