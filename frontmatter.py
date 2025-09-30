import json
from typing import Tuple, Dict, Any


def _parse_kv_lines(lines: list[str]) -> dict:
    meta: dict[str, Any] = {}
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()

        # list inline: [a, b]
        if val.startswith("[") and val.endswith("]"):
            try:
                meta[key] = json.loads(val)
            except Exception:
                meta[key] = [v.strip() for v in val.strip("[]").split(",") if v.strip()]
            i += 1
            continue

        # block list:
        if val == "" and i + 1 < n and lines[i + 1].lstrip().startswith("- "):
            items = []
            i += 1
            while i < n and lines[i].lstrip().startswith("- "):
                items.append(lines[i].lstrip()[2:].strip())
                i += 1
            meta[key] = items
            continue

        # string or number/bool-like
        sval = val.strip().strip('"').strip("'")
        # attempt to coerce simple json literals
        if sval.lower() in {"true", "false"}:
            meta[key] = sval.lower() == "true"
        else:
            try:
                meta[key] = json.loads(sval)
            except Exception:
                meta[key] = sval
        i += 1
    return meta


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or not lines[0].strip().startswith("---"):
        return {}, text
    # find closing ---
    try:
        end = next(idx for idx in range(1, len(lines)) if lines[idx].strip().startswith("---"))
    except StopIteration:
        return {}, text
    meta_block = lines[1:end]
    body_lines = lines[end + 1 :]
    meta = _parse_kv_lines(meta_block)
    body = "\n".join(body_lines)
    return meta, body

