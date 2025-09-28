#!/usr/bin/env python3
import argparse
import hashlib
import json
import os


def extract_title(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("#"):
                    return line.strip().lstrip("#").strip()
    except Exception:
        pass
    return os.path.basename(path)


def scan_documents(root: str):
    nodes = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.lower().endswith((".md", ".markdown")):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, "rb") as f:
                    data = f.read()
            except Exception:
                continue
            hid = hashlib.sha256(data).hexdigest()[:12]
            nodes.append({
                "id": hid,
                "label": extract_title(p),
                "path": os.path.relpath(p),
                "type": "scroll"
            })
    # naive: no edges yet
    return {"nodes": nodes, "edges": []}


def main():
    ap = argparse.ArgumentParser(description="Braid connector: build semantic links snapshot")
    ap.add_argument("--scan", required=True, help="Directory containing scroll documents")
    ap.add_argument("--output", required=True, help="Output JSON path")
    args = ap.parse_args()

    graph = scan_documents(args.scan)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
    print(f"[ok] Semantic links snapshot -> {args.output}")


if __name__ == "__main__":
    main()

