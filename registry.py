import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.join(ROOT, "vault")
DOCS_DIR = os.path.join(VAULT_DIR, "documents")
BRAIDS_DIR = os.path.join(VAULT_DIR, "braids")
REGISTRY_DIR = os.path.join(VAULT_DIR, "registry")
LEDGER_PATH = os.path.join(REGISTRY_DIR, "ledger.json")


def ensure_dirs():
    for d in (VAULT_DIR, DOCS_DIR, BRAIDS_DIR, REGISTRY_DIR):
        os.makedirs(d, exist_ok=True)


def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return {"scrolls": []}
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"scrolls": []}


def save_ledger(ledger):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)

