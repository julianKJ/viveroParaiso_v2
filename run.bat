@echo off
setlocal
title Vivero El Paraiso de las Plantas
cd /d "%~dp0"

echo ========================================================
echo   Iniciando Vivero El Paraiso de las Plantas
echo ========================================================
echo.

if not exist ".env" (
    echo [*] Creando archivo .env desde .env.example...
    copy ".env.example" ".env" >nul
)

if not exist ".venv\Scripts\python.exe" (
    echo [*] Creando entorno virtual .venv...
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        py -m venv .venv
    ) else (
        where python >nul 2>nul
        if %errorlevel% equ 0 (
            python -m venv .venv
        ) else (
            echo.
            echo [ERROR] No se encontro 'py' ni 'python'.
            echo Por favor instale Python 3.11+ desde https://www.python.org/downloads/
            pause
            exit /b 1
        )
    )
    echo [*] Instalando dependencias de requirements.txt...
    .\.venv\Scripts\pip install -r requirements.txt
)

echo.
echo [*] Servidor listo.
echo [*] Acceso en navegador:  http://127.0.0.1:5000
echo [*] Usuario de prueba:    admin
echo [*] Contrasena de prueba: admin123
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.

.\.venv\Scripts\python.exe app.py
pause
