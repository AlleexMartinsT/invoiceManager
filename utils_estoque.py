# utils_estoque.py
import os
import sys
import json
from datetime import datetime
from supabase import create_client
import uuid
import uuid

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2)).lower()

def get_or_create_user(supabase, mac_address):
    """
    Só verifica se já existe no Supabase.
    Se não existir, retorna None — a UI (tk_estoque) abre a janela para pedir o nome.
    """
    resp = supabase.table("users").select("*").eq("mac", mac_address).execute()
    if resp.data:
        return resp.data[0]
    return None

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

def poll_notifications(app, last_seen_ids=set(), first_run=[True]):
    """Verifica periodicamente se há notas novas ou conferidas e mostra Toast."""
    from system.ui_components import Toast

    def check():
        try:
            notes = load_notes()
            new_ids = {n["id"] for n in notes}

            if first_run[0]:
                # Primeira rodada → só registra IDs, não notifica
                last_seen_ids.clear()
                last_seen_ids.update(new_ids)
                first_run[0] = False
            else:
                # Notas novas
                added = new_ids - last_seen_ids.copy()
                for n in notes:
                    if n["id"] in added:
                        if n.get("conferido", False):
                            Toast(app.root, f"Nota {n['nf_number']} conferida!")
                        else:
                            Toast(app.root, f"Nota {n['nf_number']} adicionada!")

                # Atualiza conjunto de IDs vistos
                last_seen_ids.clear()
                last_seen_ids.update(new_ids)

        except Exception as e:
            print("Erro ao checar notificações:", e)

        # roda de novo em 5 segundos
        app.root.after(5000, check)

    check()

config_path = resource_path(os.path.join("data", "credentials.json"))

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
    
SUPABASE_URL = config.get("SUPABASE_URL")
SUPABASE_KEY = config.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- Settings ----------------

def settings_path():
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    cfg_dir = os.path.join(appdata, "RelatorioEstoque")
    os.makedirs(cfg_dir, exist_ok=True)
    return os.path.join(cfg_dir, "settings.json")

def load_settings():
    path = settings_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"visualizar_todos_meses": False}  # default

def save_settings(settings: dict):
    with open(settings_path(), "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

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
                                f"Nova versão baixada como '{new_file}'. ")
                            from system.autodelete import fechar_e_excluir
                            fechar_e_excluir()
                        except Exception as e:
                            messagebox.showerror("Erro no Download", f"Ocorreu um erro: {e}")
                root.after(0, ask_user)
            else:
                print("App atualizado.")

        except Exception as e:
            if root.winfo_exists():
                root.after(0, ask_user)

    threading.Thread(target=worker, daemon=True).start()