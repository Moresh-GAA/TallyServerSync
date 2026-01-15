"""
Build script to create Windows executable
"""
import PyInstaller.__main__
import os
import sys

def build_exe():
    """Build Windows executable"""
    
    print("=" * 50)
    print("Building Tally Server Sync Executable")
    print("=" * 50)
    
    # PyInstaller arguments
    args = [
        'tally_sync_app.py',
        '--name=TallyServerSync',
        '--onefile',
        '--windowed',
        '--hidden-import=PyQt6',
        '--hidden-import=requests',
        '--hidden-import=xml.etree.ElementTree',
        '--clean',
        '--noconfirm',
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n" + "=" * 50)
    print("Build Complete!")
    print("=" * 50)
    print("\nExecutable location: dist\\TallyServerSync.exe")
    print("\nYou can now:")
    print("1. Run dist\\TallyServerSync.exe")
    print("2. Copy it to any Windows machine")
    print("3. Add to startup using add_to_startup.bat")
    print()

if __name__ == "__main__":
    try:
        import PyInstaller
        build_exe()
    except ImportError:
        print("ERROR: PyInstaller not found!")
        print("Installing PyInstaller...")
        os.system("pip install pyinstaller")
        print("\nPlease run this script again.")
        sys.exit(1)
