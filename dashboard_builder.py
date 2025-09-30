import json
import os
from typing import Dict, Any

from .frontmatter import parse_frontmatter
from . import registry as reg


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DATA = os.path.join(ROOT, "stitchia-protocol-dev", "frontend", "data.json")


DEFAULT_DASHBOARD: Dict[str, Any] = {
    "governance": {
        "roles": ["Anchor", "Architect", "Steward", "Initiator"],
        "counts": {},
        "members_total": 0,
    },
    "treasury": {
        "total_eth": 0,
        "staking_eth": 0,
        "protocol_eth": 0,
        "updated_at": None,
    },
    "proposals": {
        "items": []
    },
    "wallet": {
        "connected": False,
        "address": None
    }
}


def _merge_dashboard(base: Dict[str, Any], add: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(base))
    for key, val in (add or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _merge_dashboard(out[key], val)
        else:
            out[key] = val
    return out


def build_dashboard_from_ledger(ledger: Dict[str, Any]) -> Dict[str, Any]:
    dashboard = json.loads(json.dumps(DEFAULT_DASHBOARD))
    for s in ledger.get("scrolls", []):
        # Only consider scrolls tagged as dashboard providers
        tags = s.get("tags") or []
        if "dashboard" not in tags:
            continue
        path = os.path.join(ROOT, s.get("filename"))
        try:
            with open(path, "r", encoding="utf-8") as f:
                txt = f.read()
            meta, _ = parse_frontmatter(txt)
        except Exception:
            meta = {}
        dash = meta.get("dashboard") or {}

        # Normalize and compute members_total if counts present
        gov = dash.get("governance") or {}
        counts = gov.get("counts") or {}
        if counts and "members_total" not in gov:
            gov["members_total"] = int(sum(v for v in counts.values() if isinstance(v, (int, float))))
        if gov:
            dash["governance"] = gov

        dashboard = _merge_dashboard(dashboard, dash)

    # Derive total if not set
    gov = dashboard.get("governance", {})
    if not gov.get("members_total") and isinstance(gov.get("counts"), dict):
        gov["members_total"] = int(sum(v for v in gov["counts"].values() if isinstance(v, (int, float))))
        dashboard["governance"] = gov
    return dashboard


def write_dashboard_json(data: Dict[str, Any]) -> str:
    os.makedirs(os.path.dirname(FRONTEND_DATA), exist_ok=True)
    with open(FRONTEND_DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return FRONTEND_DATA


def build_and_write() -> str:
    reg.ensure_dirs()
    ledger = reg.load_ledger()
    data = build_dashboard_from_ledger(ledger)
    return write_dashboard_json(data)

