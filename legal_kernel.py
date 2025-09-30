DEFAULT_LICENSE = {
    "name": "Public-Licensed / CodexLinked",
    "permissions": ["EXECUTE", "SEAL", "LINK", "EXPORT"],
}

from typing import Optional


def assign_license(meta: Optional[dict]) -> dict:
    meta = meta or {}
    lic = meta.get("license")
    if isinstance(lic, dict):
        # Ensure required fields exist
        name = lic.get("name") or "Custom"
        perms = lic.get("permissions") or DEFAULT_LICENSE["permissions"]
        return {"name": name, "permissions": perms}
    if isinstance(lic, str) and lic:
        out = DEFAULT_LICENSE.copy()
        out["name"] = lic
        return out
    return DEFAULT_LICENSE.copy()
