from __future__ import annotations
from datetime import datetime
from typing import Dict, Any

from . import registry as reg


def add_seal(scroll_id: str, by: str, role: str, status: str, note: str | None = None) -> Dict[str, Any]:
    reg.ensure_dirs()
    ledger = reg.load_ledger()
    entry = next((s for s in ledger.get("scrolls", []) if s.get("id") == scroll_id), None)
    if not entry:
        raise KeyError(f"scroll not found: {scroll_id}")
    seal = {
        "by": by,
        "role": role,
        "status": status.lower(),  # 'approved' | 'rejected'
        "note": note or "",
        "time": datetime.utcnow().isoformat() + "Z",
    }
    seals = entry.setdefault("seals", [])
    seals.append(seal)
    # derive overall seal_status
    statuses = {s.get("status") for s in seals}
    if "rejected" in statuses:
        entry["seal_status"] = "rejected"
    elif "approved" in statuses:
        entry["seal_status"] = "approved"
    else:
        entry["seal_status"] = "none"
    reg.save_ledger(ledger)
    return entry

