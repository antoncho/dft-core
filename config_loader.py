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
  },
  "profiles": {
    "default": {
      "ethics": {"require_validators": True}
    },
    "permissive": {
      "ethics": {"require_validators": False}
    },
    "strict": {
      "ethics": {
        "require_validators": True,
        "blocked_classifications": ["Financial-Product"]
      }
    }
  }
}


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = json.loads(json.dumps(a))
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


from typing import Optional


def load_config(profile: Optional[str] = None) -> Dict[str, Any]:
    # JSON-compatible YAML: we store as JSON text for simplicity
    base = json.loads(json.dumps(DEFAULTS))
    if not os.path.exists(CONF_PATH):
        cfg = base
    else:
        try:
            with open(CONF_PATH, "r", encoding="utf-8") as f:
                txt = f.read().strip()
            cfg = _deep_merge(base, json.loads(txt))
        except Exception:
            cfg = base
    if profile:
        prof = (cfg.get("profiles") or {}).get(profile)
        if prof:
            cfg = _deep_merge(cfg, prof)
    return cfg
