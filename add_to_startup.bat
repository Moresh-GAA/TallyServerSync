@echo off
echo ========================================
echo Adding Tally Server Sync to Startup
echo ========================================
echo.

set "APP_PATH=%~dp0dist\TallyServerSync.exe"

if not exist "%APP_PATH%" (
    echo ERROR: TallyServerSync.exe not found!
    echo Please build the executable first using: python build.py
    pause
    exit /b 1
)

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP_FOLDER%\TallyServerSync.lnk"

echo Creating startup shortcut...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT%'); $SC.TargetPath = '%APP_PATH%'; $SC.Save()"

echo.
echo ========================================
echo Successfully Added to Startup!
echo ========================================
echo.
echo The application will start automatically when Windows starts.
echo.
pause
