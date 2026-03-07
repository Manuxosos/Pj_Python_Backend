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
python --version >nul 2>nul
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
:: PASO 4: Instalar/actualizar dependencias
:: (pip es inteligente: si ya estan instaladas las salta)
:: -----------------------------------------------
echo [..] Verificando dependencias...
pip install -r requirements.txt -q
echo [OK] Dependencias listas.

:: -----------------------------------------------
:: PASO 5: Crear .env si no existe
:: -----------------------------------------------
if not exist ".env" (
    copy .env.example .env >nul
    echo [OK] Archivo .env creado.
) else (
    echo [OK] Archivo .env encontrado.
)

:: -----------------------------------------------
:: PASO 6: Abrir navegador despues de 5 segundos
:: -----------------------------------------------
echo.
echo  Arrancando servidor...
echo  El navegador se abrira automaticamente en unos segundos.
echo.
echo  Para DETENER el servidor presiona: Ctrl + C
echo  ==========================================
echo.

start "" cmd /c "timeout /t 5 >nul && start http://localhost:8000/docs"

:: -----------------------------------------------
:: PASO 7: Arrancar el servidor
:: -----------------------------------------------
uvicorn app.main:app --reload
