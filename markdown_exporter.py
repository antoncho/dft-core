import os
import re
from typing import Tuple


HEADING_RE = re.compile(r"^\s{0,3}(#+)\s*")
LIST_RE = re.compile(r"^\s*[-*+]\s+")
CODE_FENCE_RE = re.compile(r"^\s*```")
INLINE_CODE_RE = re.compile(r"`([^`]*)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def md_to_text(md: str) -> str:
    lines = md.splitlines()
    out = []
    in_code = False
    for line in lines:
        if CODE_FENCE_RE.match(line):
            in_code = not in_code
            continue
        if in_code:
            out.append(line)
            continue
        # Headings -> plain text with underline for H1
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            content = HEADING_RE.sub("", line).strip()
            if level == 1 and content:
                out.append(content)
                out.append("=" * len(content))
            else:
                out.append(content)
            continue
        # Lists -> dash prefix
        if LIST_RE.match(line):
            out.append("- " + LIST_RE.sub("", line).strip())
            continue
        # Inline code
        line = INLINE_CODE_RE.sub(lambda m: m.group(1), line)
        # Links -> "text (url)"
        line = LINK_RE.sub(lambda m: f"{m.group(1)} ({m.group(2)})", line)
        out.append(line)
    text = "\n".join(out)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def _rtf_escape(s: str) -> str:
    return s.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def md_to_rtf(md: str) -> str:
    lines = md.splitlines()
    rtf_lines = [r"{\rtf1\ansi\deff0\fs22"]
    in_code = False
    for line in lines:
        if CODE_FENCE_RE.match(line):
            in_code = not in_code
            continue
        if in_code:
            rtf_lines.append(_rtf_escape(line) + r"\line")
            continue
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            content = _rtf_escape(HEADING_RE.sub("", line).strip())
            size = {1: 32, 2: 28, 3: 24}.get(level, 22)
            rtf_lines.append(f"\\b\\fs{size} {content}\\b0\\fs22\\line")
            continue
        if LIST_RE.match(line):
            content = _rtf_escape(LIST_RE.sub("", line).strip())
            rtf_lines.append(f"\\bullet\tab {content}\\line")
            continue
        # Inline code -> monospace-like via \f1 if present; fallback: quoted
        line = INLINE_CODE_RE.sub(lambda m: f"'{_rtf_escape(m.group(1))}'", line)
        line = LINK_RE.sub(lambda m: f"{_rtf_escape(m.group(1))} ({_rtf_escape(m.group(2))})", line)
        rtf_lines.append(_rtf_escape(line) + r"\line")
    rtf_lines.append("}")
    return "".join(rtf_lines)


def export_md(path: str, out_txt: str, out_doc: str) -> Tuple[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        md = f.read()
    txt = md_to_text(md)
    rtf = md_to_rtf(md)
    os.makedirs(os.path.dirname(out_txt), exist_ok=True)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(txt)
    os.makedirs(os.path.dirname(out_doc), exist_ok=True)
    with open(out_doc, "w", encoding="utf-8") as f:
        f.write(rtf)
    return out_txt, out_doc

