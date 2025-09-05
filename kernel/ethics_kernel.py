from typing import Optional, Tuple, List, Dict


def validate_scroll(text: str, meta: Optional[dict], cfg: Optional[dict]) -> Tuple[str, List[str]]:
    meta = meta or {}
    cfg = (cfg or {}).get("ethics", {})
    reasons: list[str] = []
    lowered = text.lower()
    flagged = False

    forbidden = set(cfg.get("forbidden_tokens") or [])
    for tok in forbidden:
        if not tok:
            continue
        if tok.lower() in lowered:
            flagged = True
            reasons.append(f"contains forbidden token: {tok}")

    blocked_classes = set(cfg.get("blocked_classifications") or [])
    classification = (meta.get("classification") or "").strip()
    if classification in blocked_classes:
        flagged = True
        reasons.append(f"blocked classification: {classification}")

    require_validators = bool(cfg.get("require_validators"))
    validators = meta.get("validators") or []
    if require_validators and not validators:
        flagged = True
        reasons.append("validators required but missing")

    status = "flagged" if flagged else "validated"
    return status, reasons
