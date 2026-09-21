@echo off
title Vielma Moto-Repuestos - Sistema de Presupuestos
cd /d C:\vielma-moto-repuestos
call venv\Scripts\activate.bat
echo.
echo ============================================
echo   VIELMA MOTO-REPUESTOS
echo   Sistema de Presupuestos
echo ============================================
echo.
echo El sistema esta iniciando...
echo.
echo Acceder desde esta PC:
echo   http://127.0.0.1
echo   http://vielma-presupuestos.com (si configuraste el nombre)
echo.
echo Acceder desde celular o tablet (misma red WiFi):
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    echo   http://%%a
)
echo.
echo NO CIERRES ESTA VENTANA mientras uses el sistema.
echo Para apagar el sistema presiona Ctrl+C
echo.
start http://127.0.0.1
python app.py
