import PyInstaller.__main__
import os
from versionfile_generator import versionfile_generator

# Nome do executável final
APP_NAME = "Relatorio de Estoque"

# Arquivo principal (menu inicial)
ENTRY_POINT = "tk_estoque.py" 

# Ícone
ICON = "icone.ico"

# Pastas de dados (serão copiadas para dentro do .exe)
DATA_FOLDERS = [
    "data",       # pasta com imagens e outros assets
]

# Arquivos individuais que precisam estar junto
DATA_FILES = [
    "utils_estoque.py",
]

# Constrói argumentos para --add-data
datas = []
for folder in DATA_FOLDERS:
    if os.path.exists(folder):
        datas.append(f"{folder}{os.pathsep}{folder}")
for file in DATA_FILES:
    if os.path.exists(file):
        datas.append(f"{file}{os.pathsep}.")

versionfile_generator()

# Executa o PyInstaller
PyInstaller.__main__.run([
    ENTRY_POINT,
    "--name", APP_NAME,
    "--icon", ICON,
    "--version-file", "version.txt",
    "--noconsole",        # não abre terminal junto
    "--onefile",            # único executável
    "--clean",              # limpa build anterior
    "--hidden-import", "tkinter",
    "--hidden-import", "customtkinter",
    "--hidden-import", "PIL",
    "--hidden-import", "pytesseract",
    
    *[f"--add-data={d}" for d in datas]
])
