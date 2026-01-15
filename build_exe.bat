@echo off
echo ========================================
echo Tally Server Sync - Build Executable
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Step 1: Installing PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo Step 2: Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo Step 3: Building executable (this may take a few minutes)...
echo.

REM Build single file executable
pyinstaller ^
  --onefile ^
  --windowed ^
  --name=TallyServerSync ^
  --icon=icon.ico ^
  --add-data "icon.ico;." ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=requests ^
  tally_sync_app.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    echo Troubleshooting:
    echo 1. Make sure all dependencies are installed: pip install -r requirements.txt
    echo 2. Check if icon.ico exists in the current directory
    echo 3. Try running: python tally_sync_app.py to check for errors
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Successful!
echo ========================================
echo.
echo Executable created at: dist\TallyServerSync.exe
echo File size: 
dir dist\TallyServerSync.exe | find "TallyServerSync.exe"
echo.
echo Next steps:
echo 1. Test the executable: dist\TallyServerSync.exe
echo 2. Share with clients: dist\TallyServerSync.exe
echo 3. (Optional) Create installer using Inno Setup
echo.
echo Press any key to test the executable...
pause >nul

echo.
echo Launching executable for testing...
start "" "dist\TallyServerSync.exe"

echo.
echo If the application works correctly, you can distribute:
echo   dist\TallyServerSync.exe
echo.
pause
