@echo off
:: Auto-elevar a admin si es necesario
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"
python MacroFKeys.py
