@echo off
echo ========================================
echo Tally Server Sync - Installation
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the application:
echo   python tally_sync_app.py
echo.
echo Or build executable:
echo   python build.py
echo.
pause
