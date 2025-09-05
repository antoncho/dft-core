import json
import os
from typing import Any, Dict


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_PATH = os.path.join(ROOT, "kernel", "config.yml")


DEFAULTS: Dict[str, Any] = {
    "ethics": {
        "forbidden_tokens": ["malware_payload", "do_not_distribute"],
        "blocked_classifications": [],
        "require_validators": False,
    },
    "braid": {
        "tag_edge_weight": 1
    }
}


def load_config() -> Dict[str, Any]:
    # JSON-compatible YAML: we store as JSON text for simplicity
    if not os.path.exists(CONF_PATH):
        return json.loads(json.dumps(DEFAULTS))
    try:
        with open(CONF_PATH, "r", encoding="utf-8") as f:
            txt = f.read().strip()
        return json.loads(txt)
    except Exception:
        # If parsing fails, fall back to defaults
        return json.loads(json.dumps(DEFAULTS))

