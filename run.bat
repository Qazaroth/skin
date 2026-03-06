@echo off
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

if not exist ".deps_installed" (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    type nul > .deps_installed
)

python main.py