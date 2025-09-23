# utils_estoque.py
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

SUPPLIERS_FILE = os.path.join(DATA_DIR, "suppliers.json")
CONFERENTES_FILE = os.path.join(DATA_DIR, "conferentes.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Defaults
_DEFAULT_SUPPLIERS = [
    {"id": 1, "name": "Fornecedor A"},
    {"id": 2, "name": "Fornecedor B"},
]
_DEFAULT_CONFERENTES = [
    {"id": 1, "name": "Cristiane Vieira"},
    {"id": 2, "name": "João Silva"},
]
_DEFAULT_SETTINGS = {"ask_on_close": True}

def _load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        return default.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # recreate
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        return default.copy()

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# suppliers
def load_suppliers():
    return _load_json(SUPPLIERS_FILE, _DEFAULT_SUPPLIERS)

def save_suppliers(suppliers):
    _save_json(SUPPLIERS_FILE, suppliers)

def add_supplier(name):
    suppliers = load_suppliers()
    # não permitir nomes repetidos
    if any(s["name"].lower() == name.lower() for s in suppliers):
        return suppliers
    next_id = max((s.get("id", 0) for s in suppliers), default=0) + 1
    suppliers.append({"id": next_id, "name": name})
    save_suppliers(suppliers)
    return suppliers

def remove_supplier(supplier_id):
    suppliers = load_suppliers()
    suppliers = [s for s in suppliers if s.get("id") != supplier_id]
    save_suppliers(suppliers)
    return suppliers

# conferentes
def load_conferentes():
    return _load_json(CONFERENTES_FILE, _DEFAULT_CONFERENTES)

def save_conferentes(conferentes):
    _save_json(CONFERENTES_FILE, conferentes)

def add_conferente(name):
    conferentes = load_conferentes()
    if any(c["name"].lower() == name.lower() for c in conferentes):
        return conferentes
    next_id = max((c.get("id", 0) for c in conferentes), default=0) + 1
    conferentes.append({"id": next_id, "name": name})
    save_conferentes(conferentes)
    return conferentes
def remove_conferente(conferente_id):
    conferentes = load_conferentes()
    conferentes = [c for c in conferentes if c.get("id") != conferente_id]
    save_conferentes(conferentes)
    return conferentes

# notes
def load_notes():
    return _load_json(NOTES_FILE, [])

def save_note(note):
    """
    note: dict with keys:
      - nf_number (str)
      - fornecedor_id (int)
      - fornecedor_name (str)
      - data_chegada (ISO date str)
      - cnpj (EH or MVA)
      - conferente_id
      - conferente_name
      - created_at (ISO)
    """
    notes = load_notes()
    notes.append(note)
    _save_json(NOTES_FILE, notes)
    return notes

def overwrite_notes(notes):
    _save_json(NOTES_FILE, notes)

# settings
def load_settings():
    return _load_json(SETTINGS_FILE, _DEFAULT_SETTINGS)

def save_settings(settings):
    _save_json(SETTINGS_FILE, settings)

# helper
def today_br():
    return datetime.now().strftime("%d-%m-%Y")

def save_all_notes(notes):
    """Sobrescreve todas as notas no arquivo."""
    overwrite_notes(notes)

def notes_path():
    """Retorna o caminho do arquivo notes.json."""
    return NOTES_FILE

