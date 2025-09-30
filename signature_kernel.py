import hashlib


def compute_signature(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scroll_id_from_sig(signature_hex: str) -> str:
    return signature_hex[:12]

