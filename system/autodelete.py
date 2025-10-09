import os
import sys
import tempfile
import subprocess

def fechar_e_excluir():
    """Fecha o app e apaga o próprio arquivo após encerrar."""
    try:
        # Caminho do próprio arquivo (pode ser .py ou .exe)
        app_path = os.path.abspath(sys.argv[0])

        # Cria script temporário para exclusão
        temp_script = os.path.join(tempfile.gettempdir(), "delete_self.bat")

        with open(temp_script, "w") as f:
            f.write(f"""
@echo off
timeout /t 2 >nul
del "{app_path}" /f /q
del "%~f0" /f /q
""")

        # Executa o script num processo separado
        subprocess.Popen(["cmd", "/c", temp_script], creationflags=subprocess.CREATE_NO_WINDOW)

        # Fecha o app normalmente
        sys.exit(0)

    except Exception as e:
        print(f"Erro ao tentar excluir o aplicativo: {e}")
        sys.exit(1)
