@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo              TALLY SERVER SYNC - BUILD AND PACKAGE AUTOMATION
echo ================================================================================
echo.

REM Configuration
set APP_NAME=TallyServerSync
set APP_VERSION=1.0.0
set DIST_FOLDER=distribution

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/7] Checking dependencies...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller --quiet
)

echo [2/7] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %DIST_FOLDER% rmdir /s /q %DIST_FOLDER%
if exist *.spec del /q *.spec
if exist installer_output rmdir /s /q installer_output

echo [3/7] Building executable...
echo This may take 2-5 minutes, please wait...
echo.

pyinstaller ^
  --onefile ^
  --windowed ^
  --name=%APP_NAME% ^
  --icon=icon.ico ^
  --add-data "icon.ico;." ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=requests ^
  tally_sync_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo Troubleshooting:
    echo 1. Run: pip install -r requirements.txt
    echo 2. Check if icon.ico exists
    echo 3. Test: python tally_sync_app.py
    echo.
    pause
    exit /b 1
)

echo.
echo [4/7] Verifying build...
if not exist "dist\%APP_NAME%.exe" (
    echo [ERROR] Executable not found!
    pause
    exit /b 1
)

REM Get file size
for %%A in ("dist\%APP_NAME%.exe") do set FILE_SIZE=%%~zA
set /a FILE_SIZE_MB=!FILE_SIZE! / 1048576
echo Executable size: !FILE_SIZE_MB! MB

echo.
echo [5/7] Creating distribution package...
mkdir %DIST_FOLDER% 2>nul

REM Copy files
copy "dist\%APP_NAME%.exe" "%DIST_FOLDER%\" >nul
copy "README_FOR_CLIENTS.txt" "%DIST_FOLDER%\README.txt" >nul
copy "LICENSE" "%DIST_FOLDER%\" >nul 2>nul
copy "icon.ico" "%DIST_FOLDER%\" >nul 2>nul

echo.
echo [6/7] Creating ZIP archive...
powershell -Command "Compress-Archive -Path '%DIST_FOLDER%\*' -DestinationPath '%APP_NAME%_v%APP_VERSION%.zip' -Force"

if errorlevel 1 (
    echo [WARNING] Failed to create ZIP. You can manually zip the %DIST_FOLDER% folder.
) else (
    echo ZIP created: %APP_NAME%_v%APP_VERSION%.zip
)

echo.
echo [7/7] Testing executable...
echo.
echo Press any key to launch the application for testing...
pause >nul

start "" "dist\%APP_NAME%.exe"

timeout /t 3 >nul

echo.
echo ================================================================================
echo                              BUILD COMPLETE!
echo ================================================================================
echo.
echo Files created:
echo   1. dist\%APP_NAME%.exe                    [Standalone executable]
echo   2. %DIST_FOLDER%\                         [Distribution folder]
echo   3. %APP_NAME%_v%APP_VERSION%.zip          [ZIP package]
echo.
echo File sizes:
dir "dist\%APP_NAME%.exe" | find "%APP_NAME%.exe"
dir "%APP_NAME%_v%APP_VERSION%.zip" | find ".zip"
echo.
echo ================================================================================
echo                           DISTRIBUTION OPTIONS
echo ================================================================================
echo.
echo OPTION 1: Share Standalone EXE
echo   - Send: dist\%APP_NAME%.exe
echo   - Size: ~!FILE_SIZE_MB! MB
echo   - Client: Double-click to run
echo.
echo OPTION 2: Share ZIP Package
echo   - Send: %APP_NAME%_v%APP_VERSION%.zip
echo   - Client: Extract and run %APP_NAME%.exe
echo   - Includes: README and documentation
echo.
echo OPTION 3: Create Professional Installer (Recommended)
echo   - Install Inno Setup: https://jrsoftware.org/isdl.php
echo   - Open installer.iss in Inno Setup
echo   - Click Build ^> Compile
echo   - Share: installer_output\%APP_NAME%_Setup_v%APP_VERSION%.exe
echo.
echo ================================================================================
echo                              NEXT STEPS
echo ================================================================================
echo.
echo 1. Test the application thoroughly
echo 2. Check all features work correctly
echo 3. Scan with antivirus (optional)
echo 4. Create installer with Inno Setup (optional)
echo 5. Distribute to clients
echo.
echo ================================================================================
echo.

REM Ask if user wants to create installer
echo Do you want to create a professional installer now?
echo (Requires Inno Setup to be installed)
echo.
choice /C YN /M "Create installer"

if errorlevel 2 goto :skip_installer
if errorlevel 1 goto :create_installer

:create_installer
echo.
echo Checking for Inno Setup...

REM Check common Inno Setup installation paths
set INNO_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe

if "%INNO_PATH%"=="" (
    echo [WARNING] Inno Setup not found!
    echo.
    echo Please install Inno Setup from: https://jrsoftware.org/isdl.php
    echo Then manually compile installer.iss
    echo.
    goto :skip_installer
)

echo Found Inno Setup: %INNO_PATH%
echo Compiling installer...
echo.

"%INNO_PATH%" installer.iss

if errorlevel 1 (
    echo [ERROR] Installer compilation failed!
    echo Please check installer.iss for errors
) else (
    echo.
    echo ================================================================================
    echo                        INSTALLER CREATED SUCCESSFULLY!
    echo ================================================================================
    echo.
    echo Installer location: installer_output\%APP_NAME%_Setup_v%APP_VERSION%.exe
    echo.
    dir "installer_output\%APP_NAME%_Setup_v%APP_VERSION%.exe" | find "Setup"
    echo.
    echo You can now distribute this installer to your clients!
    echo.
)

:skip_installer

echo ================================================================================
echo.
echo Build process complete!
echo.
echo For support: support@yourcompany.com
echo.
pause
