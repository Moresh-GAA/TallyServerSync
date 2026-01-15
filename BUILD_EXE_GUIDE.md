# Building Windows Executable Guide

Complete guide to create a professional Windows executable (.exe) for distribution to clients.

## 🎯 Overview

We'll use **PyInstaller** to convert the Python application into a standalone Windows executable that includes:
- ✅ All Python dependencies
- ✅ Application icon
- ✅ No Python installation required
- ✅ Single file or folder distribution
- ✅ Professional installer (optional)

## 📋 Prerequisites

1. **Windows PC** (for building Windows exe)
2. **Python 3.8+** installed
3. **All dependencies** installed (`pip install -r requirements.txt`)

## 🚀 Quick Build

### Option 1: Using Build Script (Recommended)

```batch
build_exe.bat
```

This creates:
- `dist/TallyServerSync.exe` - Single executable file
- `dist/TallyServerSync/` - Folder with all files

### Option 2: Manual Build

```batch
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name=TallyServerSync tally_sync_app.py
```

## 📦 Build Methods

### Method 1: Single File Executable (Easiest Distribution)

**Pros:**
- ✅ Single .exe file
- ✅ Easy to share
- ✅ No installation needed

**Cons:**
- ❌ Slower startup (extracts to temp)
- ❌ Larger file size

**Build Command:**
```batch
pyinstaller --onefile --windowed --icon=icon.ico --name=TallyServerSync tally_sync_app.py
```

**Output:** `dist/TallyServerSync.exe` (~50-80 MB)

### Method 2: Folder Distribution (Faster Startup)

**Pros:**
- ✅ Faster startup
- ✅ Smaller individual files

**Cons:**
- ❌ Multiple files to distribute
- ❌ Need to zip for sharing

**Build Command:**
```batch
pyinstaller --windowed --icon=icon.ico --name=TallyServerSync tally_sync_app.py
```

**Output:** `dist/TallyServerSync/` folder with exe and dependencies

### Method 3: With Installer (Most Professional)

**Pros:**
- ✅ Professional installation experience
- ✅ Start menu shortcuts
- ✅ Uninstaller included
- ✅ Desktop icon

**Cons:**
- ❌ Requires Inno Setup
- ❌ More complex setup

See "Creating Installer" section below.

## 🔧 Detailed Build Process

### Step 1: Install PyInstaller

```batch
pip install pyinstaller
```

### Step 2: Create Application Icon (Optional)

1. **Get/Create Icon:**
   - Use online converter: https://convertio.co/png-ico/
   - Or use existing `icon.ico`

2. **Place in project root:**
   ```
   TallyServerSync/
   ├── icon.ico
   ├── tally_sync_app.py
   └── ...
   ```

### Step 3: Build Executable

**Single File:**
```batch
pyinstaller ^
  --onefile ^
  --windowed ^
  --icon=icon.ico ^
  --name=TallyServerSync ^
  --add-data "icon.ico;." ^
  tally_sync_app.py
```

**Folder:**
```batch
pyinstaller ^
  --windowed ^
  --icon=icon.ico ^
  --name=TallyServerSync ^
  --add-data "icon.ico;." ^
  tally_sync_app.py
```

### Step 4: Test Executable

```batch
cd dist
TallyServerSync.exe
```

## 📝 Build Configuration File

Create `TallyServerSync.spec` for advanced configuration:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tally_sync_app.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.')],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'requests',
        'xml.etree.ElementTree',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TallyServerSync',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
```

Build with spec file:
```batch
pyinstaller TallyServerSync.spec
```

## 🎨 Creating Professional Installer

### Using Inno Setup (Free & Professional)

#### Step 1: Install Inno Setup

Download from: https://jrsoftware.org/isdl.php

#### Step 2: Create Installer Script

Create `installer.iss`:

```iss
[Setup]
AppName=Tally Server Sync
AppVersion=1.0.0
AppPublisher=Your Company Name
AppPublisherURL=https://yourwebsite.com
DefaultDirName={autopf}\TallyServerSync
DefaultGroupName=Tally Server Sync
OutputDir=installer_output
OutputBaseFilename=TallyServerSync_Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\TallyServerSync.exe
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
Name: "startupicon"; Description: "Run at Windows &startup"; GroupDescription: "Additional options:"

[Files]
Source: "dist\TallyServerSync.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; If using folder distribution, include all files:
; Source: "dist\TallyServerSync\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Tally Server Sync"; Filename: "{app}\TallyServerSync.exe"
Name: "{group}\Uninstall Tally Server Sync"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Tally Server Sync"; Filename: "{app}\TallyServerSync.exe"; Tasks: desktopicon
Name: "{userstartup}\Tally Server Sync"; Filename: "{app}\TallyServerSync.exe"; Tasks: startupicon

[Run]
Filename: "{app}\TallyServerSync.exe"; Description: "Launch Tally Server Sync"; Flags: nowait postinstall skipifsilent
```

#### Step 3: Compile Installer

1. Open Inno Setup
2. File → Open → Select `installer.iss`
3. Build → Compile
4. Output: `installer_output/TallyServerSync_Setup.exe`

## 📤 Distribution Options

### Option 1: Direct EXE Distribution

**For Single File:**
```
1. Build: build_exe.bat
2. Share: dist/TallyServerSync.exe
3. Client: Double-click to run
```

**File Size:** ~50-80 MB

### Option 2: ZIP Distribution

**For Folder:**
```
1. Build: pyinstaller --windowed ...
2. Zip: dist/TallyServerSync/ → TallyServerSync.zip
3. Share: TallyServerSync.zip
4. Client: Extract and run TallyServerSync.exe
```

### Option 3: Installer Distribution (Recommended)

**Most Professional:**
```
1. Build exe: build_exe.bat
2. Create installer: Compile installer.iss
3. Share: TallyServerSync_Setup.exe
4. Client: Run installer, follow wizard
```

**Benefits:**
- ✅ Professional installation
- ✅ Start menu shortcuts
- ✅ Desktop icon
- ✅ Uninstaller
- ✅ Auto-startup option

## 🔒 Code Signing (Optional but Recommended)

### Why Sign?

- ✅ Removes "Unknown Publisher" warning
- ✅ Builds trust with clients
- ✅ Prevents tampering alerts

### How to Sign:

1. **Get Code Signing Certificate:**
   - DigiCert, Sectigo, GlobalSign
   - Cost: ~$100-300/year

2. **Sign Executable:**
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/TallyServerSync.exe
   ```

3. **Sign Installer:**
   ```batch
   signtool sign /f certificate.pfx /p password installer_output/TallyServerSync_Setup.exe
   ```

## 📋 Pre-Distribution Checklist

Before sharing with clients:

- [ ] Test on clean Windows machine (no Python installed)
- [ ] Test all features (Tally connection, server sync, etc.)
- [ ] Verify icon displays correctly
- [ ] Check file size is reasonable
- [ ] Test installation/uninstallation (if using installer)
- [ ] Scan with antivirus (some may flag PyInstaller exes)
- [ ] Create user documentation
- [ ] Prepare support contact info

## 🐛 Troubleshooting

### Issue: "Failed to execute script"

**Solution:**
```batch
# Build with console to see errors
pyinstaller --onefile --console --icon=icon.ico --name=TallyServerSync tally_sync_app.py
```

### Issue: Missing DLL errors

**Solution:**
```batch
# Include all dependencies
pyinstaller --onefile --windowed --hidden-import=PyQt6 --collect-all PyQt6 tally_sync_app.py
```

### Issue: Antivirus flags executable

**Solutions:**
1. Code sign the executable
2. Submit to antivirus vendors as false positive
3. Use folder distribution instead of --onefile
4. Add exclusion in antivirus

### Issue: Large file size

**Solutions:**
1. Use UPX compression:
   ```batch
   pyinstaller --onefile --upx-dir=C:\upx tally_sync_app.py
   ```
2. Exclude unnecessary packages in .spec file
3. Use folder distribution

## 📊 File Size Comparison

| Method | Size | Startup | Distribution |
|--------|------|---------|--------------|
| Single File | 50-80 MB | Slower | Easiest |
| Folder | 40-70 MB | Faster | Medium |
| Installer | 50-80 MB | Faster | Professional |

## 🎯 Recommended Workflow

### For Development:
```batch
python tally_sync_app.py
```

### For Testing:
```batch
build_exe.bat
dist\TallyServerSync.exe
```

### For Distribution:
```batch
1. build_exe.bat
2. Compile installer.iss in Inno Setup
3. Share: TallyServerSync_Setup.exe
```

## 📝 Client Instructions

Create `README_FOR_CLIENTS.txt`:

```
Tally Server Sync - Installation Guide
======================================

OPTION 1: Using Installer (Recommended)
----------------------------------------
1. Double-click TallyServerSync_Setup.exe
2. Follow installation wizard
3. Launch from Start Menu or Desktop icon

OPTION 2: Standalone Executable
--------------------------------
1. Double-click TallyServerSync.exe
2. Application will start

FIRST TIME SETUP:
-----------------
1. Click "Settings" tab
2. Enter your server credentials:
   - Server URL: https://yourserver.com/api/tally
   - Email: your@email.com
   - Password: your_password
3. Click "Login"
4. Configure Tally settings:
   - Host: localhost
   - Port: 9000
5. Click "Test Tally Connection"
6. Click "Save Configuration"
7. Go to "Sync" tab
8. Click "Start Auto Sync"

SUPPORT:
--------
Email: support@yourcompany.com
Website: https://yourwebsite.com
```

## 🚀 Automation Script

Create `build_and_package.bat`:

```batch
@echo off
echo ========================================
echo Tally Server Sync - Build and Package
echo ========================================
echo.

echo Step 1: Cleaning old builds...
rmdir /s /q build dist 2>nul
del /q *.spec 2>nul

echo Step 2: Building executable...
pyinstaller --onefile --windowed --icon=icon.ico --name=TallyServerSync tally_sync_app.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo Step 3: Testing executable...
start /wait dist\TallyServerSync.exe

echo Step 4: Creating distribution package...
mkdir distribution 2>nul
copy dist\TallyServerSync.exe distribution\
copy README_FOR_CLIENTS.txt distribution\
copy icon.ico distribution\

echo Step 5: Creating ZIP...
powershell Compress-Archive -Path distribution\* -DestinationPath TallyServerSync_v1.0.zip -Force

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Files created:
echo - dist\TallyServerSync.exe
echo - TallyServerSync_v1.0.zip
echo.
echo Next steps:
echo 1. Test the executable
echo 2. Create installer with Inno Setup (optional)
echo 3. Share with clients
echo.
pause
```

## ✅ Summary

**Easiest:** Single file exe
```batch
build_exe.bat
Share: dist/TallyServerSync.exe
```

**Most Professional:** Installer
```batch
build_exe.bat
Compile installer.iss
Share: TallyServerSync_Setup.exe
```

**Best Practice:** Code-signed installer with documentation

---

**Ready to distribute!** 🎉
