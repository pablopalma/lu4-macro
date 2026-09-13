@echo off
cd /d "%~dp0"
title Compilando MacroFKeys.exe...
echo.
echo =====================================================
echo   Build - Macro Manager F1-F12
echo =====================================================
echo.

python --version >/dev/null 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instalalo desde https://python.org
    pause & exit /b 1
)

python -c "import PyInstaller" >/dev/null 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller --quiet
)

echo Compilando... (puede tardar 30-60 segundos)
echo.

pyinstaller --onefile --noconsole --name MacroFKeys MacroFKeys.py

if errorlevel 1 (
    echo.
    echo [ERROR] La compilacion fallo.
    pause & exit /b 1
)

echo.
echo =====================================================
echo   Listo!  El .exe esta en:  dist\MacroFKeys.exe
echo =====================================================
echo.
pause