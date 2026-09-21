@echo off
title Configurar nombre vielma-presupuestos.com
echo ============================================
echo  Configurando vielma-presupuestos.com
echo ============================================
echo.
echo Este script agrega "vielma-presupuestos.com" al archivo hosts
echo para que puedas acceder al sistema con ese nombre en vez de la IP.
echo.
echo IMPORTANTE: Se necesita ejecutar como Administrador.
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Debes ejecutar este archivo como Administrador.
    echo Clic derecho sobre el archivo - Ejecutar como administrador.
    echo.
    pause
    exit /b 1
)

:: Obtener la IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%

echo Se detectó la IP local: %IP%
echo.

:: Verificar si ya existe la entrada
findstr /c:"vielma-presupuestos.com" %windir%\System32\drivers\etc\hosts >nul 2>&1
if %errorlevel% equ 0 (
    echo La entrada "vielma-presupuestos.com" ya existe en el archivo hosts.
    echo.
    pause
    exit /b 0
)

:: Agregar entrada al hosts
echo %IP%    vielma-presupuestos.com >> %windir%\System32\drivers\etc\hosts
echo.
echo Se agregó correctamente:
echo %IP%    vielma-presupuestos.com
echo.
echo Ahora puedes acceder al sistema desde el navegador con:
echo http://vielma-presupuestos.com
echo.
pause
