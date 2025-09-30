def extract_title(markdown_text: str) -> str:
    for line in markdown_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
        if s.startswith("#"):
            return s.lstrip("#").strip()
    return "Untitled Scroll"


def annotate_terms(markdown_text: str) -> list[str]:
    terms: set[str] = set()
    for line in markdown_text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            terms.add(s.lstrip("#").strip())
    return sorted(terms)

