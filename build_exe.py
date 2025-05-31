#!/usr/bin/env python3
"""
Script pour compiler install.py en exécutable .exe pour Windows
Utilise PyInstaller pour créer un standalone executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_spec_file():
    """Créer le fichier .spec pour PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['install.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'requests',
        'packaging',
        'json',
        'subprocess',
        'datetime',
        'argparse',
        'urllib3',
        'charset_normalizer',
        'idna',
        'certifi'
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
    name='equicord_updater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version='version_info.txt'
)
'''
    
    with open('equicord_updater.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Fichier .spec créé")

def create_version_info():
    """Créer le fichier d'informations de version"""
    version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 12, 2, 0),
    prodvers=(1, 12, 2, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Equicord Community'),
        StringStruct(u'FileDescription', u'Equicord Updater - Vérifie les mises à jour sans affecter les plugins'),
        StringStruct(u'FileVersion', u'1.12.2.0'),
        StringStruct(u'InternalName', u'equicord_updater'),
        StringStruct(u'LegalCopyright', u'GPL-3.0-or-later'),
        StringStruct(u'OriginalFilename', u'equicord_updater.exe'),
        StringStruct(u'ProductName', u'Equicord Updater'),
        StringStruct(u'ProductVersion', u'1.12.2.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print("✅ Fichier version_info.txt créé")

def build_exe():
    """Compiler en .exe"""
    print("🔧 Compilation en cours...")
    print("=" * 50)
    
    try:
        # Utiliser le fichier .spec
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'equicord_updater.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Compilation réussie!")
        print(f"📁 Exécutable créé dans: dist/equicord_updater.exe")
        
        # Vérifier si le fichier existe
        exe_path = Path('dist/equicord_updater.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📏 Taille: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Fichier .exe non trouvé après compilation")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur de compilation: {e}")
        print("Sortie d'erreur:", e.stderr)
        return False

def create_bat_file():
    """Créer un fichier .bat pour Windows"""
    bat_content = '''@echo off
chcp 65001 > nul
title Equicord Updater

echo.
echo 🔧 Equicord Updater pour Windows
echo ================================
echo.

:: Vérifier si l'exécutable existe
if not exist "equicord_updater.exe" (
    echo ❌ equicord_updater.exe non trouvé!
    echo 💡 Assurez-vous que ce fichier est dans le même dossier.
    pause
    exit /b 1
)

:: Afficher le menu
:menu
echo.
echo Options disponibles:
echo   1. Vérifier les mises à jour
echo   2. Simulation de mise à jour
echo   3. Mise à jour interactive
echo   4. Aide
echo   5. Quitter
echo.
set /p choice="Votre choix (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🔍 Vérification des mises à jour...
    equicord_updater.exe
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🧪 Simulation de mise à jour...
    equicord_updater.exe --dry-run
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 🚀 Mise à jour interactive...
    equicord_updater.exe --update
    goto end
)

if "%choice%"=="4" (
    echo.
    equicord_updater.exe --help
    goto end
)

if "%choice%"=="5" (
    echo.
    echo 👋 Au revoir!
    exit /b 0
)

echo.
echo ❌ Choix invalide. Veuillez entrer un nombre entre 1 et 5.
goto menu

:end
echo.
echo 📝 Terminé. Appuyez sur une touche pour continuer...
pause > nul
goto menu
'''
    
    with open('equicord_updater.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("✅ Fichier .bat créé pour Windows")

def clean_build_files():
    """Nettoyer les fichiers temporaires de build"""
    files_to_remove = [
        'equicord_updater.spec',
        'version_info.txt'
    ]
    
    dirs_to_remove = [
        'build',
        '__pycache__'
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Supprimé: {file_path}")
    
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"🗑️  Dossier supprimé: {dir_path}")

def main():
    print("🏗️  Build Equicord Updater .exe")
    print("=" * 40)
    
    # Vérifier si install.py existe
    if not os.path.exists('install.py'):
        print("❌ install.py non trouvé!")
        sys.exit(1)
    
    try:
        # Étapes de build
        create_version_info()
        create_spec_file()
        
        success = build_exe()
        
        if success:
            create_bat_file()
            print("\n" + "=" * 50)
            print("🎉 Build terminé avec succès!")
            print("\nFichiers créés:")
            print("📁 dist/equicord_updater.exe")
            print("📁 equicord_updater.bat")
            print("\n💡 Pour Windows:")
            print("   - Copiez equicord_updater.exe vers votre dossier Equicord")
            print("   - Ou utilisez equicord_updater.bat pour un menu interactif")
        else:
            print("❌ Build échoué!")
            
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
    
    finally:
        # Nettoyage optionnel
        choice = input("\n🗑️  Nettoyer les fichiers temporaires? (y/N): ")
        if choice.lower() in ['y', 'yes', 'oui']:
            clean_build_files()

if __name__ == "__main__":
    main() 