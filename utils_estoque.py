# utils_estoque.py
import os
import sys
import requests
from datetime import datetime
from supabase import create_client

# ---------------- Configuração do Supabase ----------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jouphkenfywomlryztle.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpvdXBoa2VuZnl3b21scnl6dGxlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2NDc1MzcsImV4cCI6MjA3NDIyMzUzN30.tRs9ycQPxAbxwXOQWaObM2gSFiBOnDA_nkJtJv85kzk")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- Fornecedores ----------------
def load_suppliers():
    resp = supabase.table("suppliers").select("*").order("name").execute() # Ordenando por nome
    return resp.data or []

def add_supplier(name):
    existing = supabase.table("suppliers").select("*").eq("name", name).execute()
    if existing.data:
        return load_suppliers()
    supabase.table("suppliers").insert({"name": name}).execute()
    return load_suppliers()

def remove_supplier(supplier_id):
    supabase.table("suppliers").delete().eq("id", supplier_id).execute()
    return load_suppliers()

# ---------------- Conferentes ----------------
def load_conferentes():
    resp = supabase.table("conferentes").select("*").order("name").execute() # Ordenando por nome
    return resp.data or []

def add_conferente(name):
    existing = supabase.table("conferentes").select("*").eq("name", name).execute()
    if existing.data:
        return load_conferentes()
    supabase.table("conferentes").insert({"name": name}).execute()
    return load_conferentes()

def remove_conferente(conferente_id):
    supabase.table("conferentes").delete().eq("id", conferente_id).execute()
    return load_conferentes()

# ---------------- Notas ----------------
def load_notes():
    resp = supabase.table("notes").select("*").order("id").execute()
    return resp.data or []

def save_note(note: dict):
    supabase.table("notes").insert(note).execute()
    return load_notes()

def update_note(note_id, fields: dict):
    supabase.table("notes").update(fields).eq("id", note_id).execute()
    return load_notes()

def remove_note(note_id):
    supabase.table("notes").delete().eq("id", note_id).execute()
    return load_notes()

def save_all_notes(notes: list[dict]):
    supabase.table("notes").delete().neq("id", 0).execute()
    if notes:
        supabase.table("notes").insert(notes).execute()
    return load_notes()

# ---------------- Helpers ----------------
def today_br():
    return datetime.now().strftime("%d-%m-%Y")

def resource_path(relative_path: str):
    """Garante que os assets funcionem no PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------- Update Checker ----------------
    
def check_for_updates(root):
    import requests
    from tkinter import messagebox
    import threading
    from versionfile_generator import APP_VERSION
    
    GITHUB_REPO = "AlleexMartinsT/invoiceManager"
    
    def worker():
        try:
            # Checa versão
            response = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=10)
            response.raise_for_status()
            data = response.json()
            latest_version = data["tag_name"].lstrip("v")

            if latest_version > APP_VERSION:
                # Mostra diálogo na thread principal usando after()
                def ask_user():
                    if messagebox.askyesno("Atualização Disponível",
                        f"Uma nova versão ({latest_version}) está disponível! Deseja baixar agora?"):
                        asset_url = data["assets"][0]["browser_download_url"]
                        new_file = f"Relatório de Clientes {latest_version}.exe"
                        try:
                            download = requests.get(asset_url, stream=True, timeout=30)
                            with open(new_file, "wb") as f:
                                for chunk in download.iter_content(8192):
                                    f.write(chunk)
                            messagebox.showinfo("Atualizado",
                                f"Nova versão baixada como '{new_file}'. "
                                "Feche o app, substitua o arquivo atual por esse novo e reinicie.")
                        except Exception as e:
                            messagebox.showerror("Erro no Download", f"Ocorreu um erro: {e}")
                root.after(0, ask_user)  # root é sua janela Tk principal
            else:
                print("App atualizado.")

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Erro na Atualização",
                                                       f"Ocorreu um erro ao checar atualizações: {e}"))

    threading.Thread(target=worker, daemon=True).start()