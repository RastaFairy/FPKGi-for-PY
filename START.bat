@echo off
title FPKGi Manager - Windows
color 0B

echo ==========================================
echo    FPKGI MANAGER FOR WINDOWS
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no instalado
    pause
    exit /b 1
)

echo [*] Instalando dependencias...
pip install -r requirements.txt >nul 2>&1

echo [*] Iniciando FPKGi Manager...
echo.
python fpkgi_manager.py

pause
