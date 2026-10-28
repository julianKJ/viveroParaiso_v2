# Script de inicio rapido para Vivero El Paraiso
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Green
Write-Host "  Iniciando Vivero El Paraíso de las Plantas" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

if (-not (Test-Path ".env")) {
    Write-Host "[*] Creando archivo .env desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[*] Creando entorno virtual .venv..." -ForegroundColor Yellow
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        python -m venv .venv
    } else {
        Write-Error "No se encontró Python ni el lanzador 'py'. Instálelo desde https://www.python.org/"
    }
    Write-Host "[*] Instalando dependencias..." -ForegroundColor Yellow
    & .\.venv\Scripts\pip.exe install -r requirements.txt
}

Write-Host "`n[*] Servidor listo en: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "[*] Usuario de prueba: admin | Contraseña: admin123`n" -ForegroundColor Cyan

& .\.venv\Scripts\python.exe app.py
