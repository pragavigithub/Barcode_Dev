@echo off
echo WMS Application - Windows Setup
echo ================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

python install_local_deps.py

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Set up MySQL database (see local_setup.md)
echo 2. Configure environment variables
echo 3. Run: python main.py
echo.
pause