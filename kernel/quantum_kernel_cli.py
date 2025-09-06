#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime

from . import registry as reg
from .signature_kernel import compute_signature, scroll_id_from_sig
from .ethics_kernel import validate_scroll
from .ontology_kernel import extract_title, annotate_terms
from .quantum_cascade import cascade_integrity
from .frontmatter import parse_frontmatter
from .legal_kernel import assign_license
from .config_loader import load_config
from .dashboard_builder import build_and_write
from .markdown_exporter import export_md

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = reg.VAULT_DIR
DOCS_DIR = reg.DOCS_DIR
BRAIDS_DIR = reg.BRAIDS_DIR
REGISTRY_DIR = reg.REGISTRY_DIR
LEDGER_PATH = reg.LEDGER_PATH
BRAIDMAP_PATH = os.path.join(ROOT, "stitchia-protocol-dev", "braidmap.json")


def ensure_dirs():
    reg.ensure_dirs()


def load_ledger():
    return reg.load_ledger()


def save_ledger(ledger):
    reg.save_ledger(ledger)


def process_scroll(path: str) -> int:
    ensure_dirs()
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f"[error] Scroll not found: {path}", file=sys.stderr)
        return 1
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode("utf-8", errors="replace")
    meta, body = parse_frontmatter(text)
    cfg = load_config()
    title = meta.get("title") or extract_title(body)
    digest = compute_signature(data)
    scroll_id = scroll_id_from_sig(digest)
    created_at = datetime.utcnow().isoformat() + "Z"
    ethics_status, ethics_reasons = validate_scroll(body, meta, cfg)
    ontology_terms = annotate_terms(body)
    cascade = cascade_integrity(data)
    license_info = assign_license(meta)
    classification = meta.get("classification") or "Governance+Ethics+StrategicDesign"
    validators = meta.get("validators") or []
    tags = meta.get("tags") or []
    links = meta.get("links") or []

    ledger = load_ledger()
    # avoid duplicate entries for same file hash
    if not any(s.get("id") == scroll_id for s in ledger["scrolls"]):
        entry = {
            "id": scroll_id,
            "filename": os.path.relpath(path, ROOT),
            "title": title,
            "signature": digest,
            "ethics_status": ethics_status,
            "ethics_reasons": ethics_reasons,
            "classification": classification,
            "created_at": created_at,
            "ontology": ontology_terms,
            "cascade": cascade,
            "license": license_info,
            "validators": validators,
            "tags": tags,
            "links": links,
        }
        ledger["scrolls"].append(entry)
        save_ledger(ledger)
        print(f"[ok] Processed scroll '{title}' -> id={scroll_id}")
    else:
        # Upgrade existing entry with latest annotations if missing
        for s in ledger["scrolls"]:
            if s.get("id") == scroll_id:
                # Update with latest annotations
                s["ethics_status"] = ethics_status
                s["ethics_reasons"] = ethics_reasons
                s["ontology"] = ontology_terms
                s["cascade"] = cascade
                s["classification"] = classification
                s["license"] = license_info
                s["validators"] = validators
                s["tags"] = tags
                s["links"] = links
        save_ledger(ledger)
        print(f"[ok] Scroll already in registry -> id={scroll_id}")
    # Generate braid for this scroll immediately for intuitive feedback
    try:
        generate_braid_by_id(scroll_id)
    except Exception:
        pass
    # Auto-regenerate dashboard JSON on every scroll process
    try:
        path = build_and_write()
        print(f"[ok] Dashboard data updated -> {os.path.relpath(path, ROOT)}")
    except Exception as e:
        print(f"[warn] Dashboard build failed: {e}")
    return 0


def cmd_process(args):
    return process_scroll(args.path)


def generate_braid_by_id(sid: str) -> int:
    ensure_dirs()
    ledger = load_ledger()
    entry = next((s for s in ledger.get("scrolls", []) if s.get("id") == sid), None)
    if not entry:
        print(f"[error] Scroll id not found in registry: {sid}", file=sys.stderr)
        return 1

    braid = {
        "id": sid,
        "title": entry.get("title"),
        "nodes": [
            {"id": sid, "label": entry.get("title"), "type": "scroll"}
        ],
        "edges": [],
        "context": {
            "source": entry.get("filename"),
        },
    }

    # Optionally enrich with braidmap clusters if available
    if os.path.exists(BRAIDMAP_PATH):
        try:
            with open(BRAIDMAP_PATH, "r", encoding="utf-8") as f:
                braidmap = json.load(f)
            clusters = braidmap.get("Clusters") or {}
            braid["context"]["clusters"] = clusters
        except Exception:
            pass

    # Enrich with cross-scroll links via tags or explicit links
    ledger = load_ledger()
    all_scrolls = {s["id"]: s for s in ledger.get("scrolls", [])}
    filename_to_id = {s.get("filename"): s.get("id") for s in ledger.get("scrolls", [])}

    target_tags = set(entry.get("tags") or [])
    cfg = load_config()
    tag_weight = (cfg.get("braid") or {}).get("tag_edge_weight", 1)

    # Tag edges
    for oid, other in all_scrolls.items():
        if oid == sid:
            continue
        otags = set(other.get("tags") or [])
        shared = target_tags & otags
        if shared:
            braid["edges"].append({
                "from": sid,
                "to": oid,
                "type": "tag",
                "weight": tag_weight * len(shared),
                "shared": sorted(shared),
            })
            braid["nodes"].append({"id": oid, "label": other.get("title"), "type": "scroll"})

    # Explicit links (id or filename)
    for ref in entry.get("links") or []:
        target_id = None
        if isinstance(ref, str):
            r = ref.strip()
            if len(r) == 12 and r in all_scrolls:
                target_id = r
            elif r in filename_to_id:
                target_id = filename_to_id[r]
        if target_id and target_id != sid:
            other = all_scrolls.get(target_id)
            braid["edges"].append({
                "from": sid,
                "to": target_id,
                "type": "link",
                "weight": 1,
            })
            braid["nodes"].append({"id": target_id, "label": other.get("title"), "type": "scroll"})

    # Deduplicate nodes
    seen = set()
    uniq_nodes = []
    for n in braid["nodes"]:
        if n["id"] in seen:
            continue
        seen.add(n["id"])
        uniq_nodes.append(n)
    braid["nodes"] = uniq_nodes

    out_path = os.path.join(BRAIDS_DIR, f"{sid}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(braid, f, indent=2, ensure_ascii=False)
    print(f"[ok] Braid generated -> {os.path.relpath(out_path, ROOT)}")
    return 0


def cmd_braid(args):
    return generate_braid_by_id(args.id)


def cmd_registry(_args):
    ensure_dirs()
    ledger = load_ledger()
    scrolls = ledger.get("scrolls", [])
    if not scrolls:
        print("[info] Registry is empty")
        return 0
    print("ID           | Title                       | File")
    print("-" * 80)
    for s in scrolls:
        sid = s.get("id", "").ljust(12)[:12]
        title = (s.get("title", "") or "").ljust(27)[:27]
        fname = s.get("filename", "")
        print(f"{sid} | {title} | {fname}")
    return 0


def cmd_export(args):
    ensure_dirs()
    ledger = load_ledger()
    out = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
    print(f"[ok] Exported registry -> {out}")
    return 0


def cmd_preview(args):
    ensure_dirs()
    import time
    last_ledger_mtime = None
    last_braid_mtime = None
    braid_dir = BRAIDS_DIR
    while True:
        try:
            # Detect changes
            mtime = os.path.getmtime(LEDGER_PATH) if os.path.exists(LEDGER_PATH) else 0
            if mtime != last_ledger_mtime:
                last_ledger_mtime = mtime
                ledger = load_ledger()
                scrolls = ledger.get("scrolls", [])
                print("==== Registry Preview ====")
                print(f"scroll_count: {len(scrolls)} | updated: {datetime.utcfromtimestamp(mtime).isoformat()+'Z' if mtime else 'never'}")
                for s in scrolls[-10:]:  # last 10
                    print(f"- {s.get('id')} | {s.get('title')} | ethics={s.get('ethics_status')} | tags={','.join(s.get('tags') or [])}")

            # Latest braid file
            latest_braid = None
            latest_braid_m = 0
            if os.path.isdir(braid_dir):
                for fn in os.listdir(braid_dir):
                    if not fn.endswith('.json'):
                        continue
                    p = os.path.join(braid_dir, fn)
                    m = os.path.getmtime(p)
                    if m > latest_braid_m:
                        latest_braid_m = m
                        latest_braid = p
            if latest_braid and latest_braid_m != last_braid_mtime:
                last_braid_mtime = latest_braid_m
                try:
                    with open(latest_braid, 'r', encoding='utf-8') as f:
                        b = json.load(f)
                    print("==== Braid Preview ====")
                    print(f"braid: {os.path.basename(latest_braid)} | nodes={len(b.get('nodes',[]))} | edges={len(b.get('edges',[]))}")
                except Exception:
                    pass

            time.sleep(max(0.1, float(getattr(args, 'interval', 1.0))))
        except KeyboardInterrupt:
            print("[preview] stopped")
            return 0


def _scan_md_files(dirs):
    files = {}
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for root, _dirs, fns in os.walk(d):
            for fn in fns:
                if not fn.lower().endswith((".md", ".markdown")):
                    continue
                p = os.path.join(root, fn)
                try:
                    files[p] = os.path.getmtime(p)
                except OSError:
                    pass
    return files


def cmd_watch(args):
    ensure_dirs()
    dirs = args.dirs
    last = _scan_md_files(dirs)
    last_ledger_mtime = os.path.getmtime(LEDGER_PATH) if os.path.exists(LEDGER_PATH) else 0
    print(f"[watch] watching: {', '.join([d for d in dirs if os.path.isdir(d)])}")
    try:
        # Debounce state
        import time as _t
        debounce = max(0.0, float(getattr(args, 'debounce', 0.0)))
        pending: set[str] = set()
        pending_since: float | None = None
        while True:
            now = _scan_md_files(dirs)
            # detect changes
            changed = [p for p, m in now.items() if p not in last or last[p] != m]
            if changed:
                for p in sorted(changed):
                    if os.path.exists(p):
                        rel = os.path.relpath(p, ROOT)
                        print(f"[watch] change detected -> {rel}")
                        pending.add(p)
                if pending_since is None:
                    pending_since = _t.time()

            # If debounce window elapsed, process batch
            if pending and (debounce == 0.0 or (_t.time() - (pending_since or 0)) >= debounce):
                batch = sorted(pending)
                print(f"[watch] processing {len(batch)} file(s) (debounce={debounce:.2f}s)")
                for p in batch:
                    process_scroll(p)
                try:
                    outp = build_and_write()
                    print(f"[watch] dashboard updated -> {os.path.relpath(outp, ROOT)}")
                except Exception as e:
                    print(f"[watch] dashboard build failed: {e}")
                pending.clear()
                pending_since = None

            # if registry changed, rebuild all braids
            reg_m = os.path.getmtime(LEDGER_PATH) if os.path.exists(LEDGER_PATH) else 0
            if reg_m != last_ledger_mtime:
                last_ledger_mtime = reg_m
                ledger = load_ledger()
                for s in ledger.get("scrolls", []):
                    generate_braid_by_id(s.get("id"))
                try:
                    outp = build_and_write()
                    print(f"[watch] dashboard updated -> {os.path.relpath(outp, ROOT)}")
                except Exception as e:
                    print(f"[watch] dashboard build failed: {e}")

            last = now
            import time
            time.sleep(max(0.1, float(getattr(args, 'interval', 1.0))))
    except KeyboardInterrupt:
        print("[watch] stopped")
        return 0


def cmd_init(args):
    ensure_dirs()
    print(f"[init] vault ready at {os.path.relpath(VAULT_DIR, ROOT)}")
    if getattr(args, "with_example", False):
        tpl_path = os.path.join(ROOT, "templates", "scroll_template.md")
        out = os.path.join(DOCS_DIR, "example_scroll.md")
        try:
            with open(tpl_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(out, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[init] example scroll -> {os.path.relpath(out, ROOT)}")
        except Exception as e:
            print(f"[init] could not create example scroll: {e}")
    return 0


def cmd_add(args):
    ensure_dirs()
    title = args.title.strip()
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    template = (
        "---\n"
        f"title: \"{title}\"\n"
        "classification: Governance+Ethics+StrategicDesign\n"
        "validators: []\n"
        "license: Public-Licensed / CodexLinked\n"
        "tags: []\n"
        "links: []\n"
        "---\n\n"
        f"# {title}\n\n"
        "## Intent\nDescribe intent here.\n\n"
        "## Design\nDescribe design here.\n\n"
        "## Ethics\nList ethics considerations here.\n\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"[add] created -> {os.path.relpath(out_path, ROOT)}")
    return 0


def cmd_status(_args):
    ensure_dirs()
    ledger = load_ledger()
    scrolls = ledger.get("scrolls", [])
    total = len(scrolls)
    flagged = sum(1 for s in scrolls if s.get("ethics_status") == "flagged")
    print(f"Scrolls: {total} | Flagged: {flagged}")
    if total:
        print("Recent:")
        for s in scrolls[-5:]:
            print(f"- {s.get('id')} | {s.get('title')} | ethics={s.get('ethics_status')}")
    return 0


def cmd_build(_args):
    ensure_dirs()
    ledger = load_ledger()
    for s in ledger.get("scrolls", []):
        generate_braid_by_id(s.get("id"))
    out = build_and_write()
    print(f"[build] dashboard updated -> {os.path.relpath(out, ROOT)}")
    return 0


def _resolve_path_by_id(sid: str) -> str:
    led = load_ledger()
    for s in led.get("scrolls", []):
        if s.get("id") == sid:
            return os.path.join(ROOT, s.get("filename"))
    raise FileNotFoundError(f"scroll id not found: {sid}")


def cmd_export_doc(args):
    ensure_dirs()
    if getattr(args, "id", None):
        path = _resolve_path_by_id(args.id)
    else:
        path = os.path.abspath(args.path)
    base = os.path.splitext(os.path.basename(path))[0]
    outdir = os.path.abspath(args.outdir)
    txt_path = os.path.join(outdir, f"{base}.txt")
    doc_path = os.path.join(outdir, f"{base}.doc")
    t, d = export_md(path, txt_path, doc_path)
    print(f"[export] TXT -> {os.path.relpath(t, ROOT)}")
    print(f"[export] DOC -> {os.path.relpath(d, ROOT)}")
    return 0


def cmd_export_docs_all(args):
    ensure_dirs()
    ledger = load_ledger()
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)
    count = 0
    for s in ledger.get("scrolls", []):
        src = os.path.join(ROOT, s.get("filename"))
        if not os.path.exists(src):
            continue
        base = os.path.splitext(os.path.basename(src))[0]
        txt_path = os.path.join(outdir, f"{base}.txt")
        doc_path = os.path.join(outdir, f"{base}.doc")
        try:
            export_md(src, txt_path, doc_path)
            count += 1
        except Exception as e:
            print(f"[export] failed for {src}: {e}")
    print(f"[export] batch complete -> {count} scroll(s) exported to {os.path.relpath(outdir, ROOT)}")
    return 0

def build_parser():
    p = argparse.ArgumentParser(description="GILC Quantum Kernel CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    # init: scaffold vault + optional template scroll
    p0 = sub.add_parser("init", help="Initialize vault and optional example scroll")
    p0.add_argument("--with-example", action="store_true", help="Create an example scroll from template")
    p0.set_defaults(func=cmd_init)

    p1 = sub.add_parser("process", help="Execute scroll through Ethics+Execution Kernel")
    p1.add_argument("path", help="Path to scroll markdown file")
    p1.set_defaults(func=cmd_process)

    p2 = sub.add_parser("braid", help="Visualize semantic topology for a scroll")
    p2.add_argument("--id", required=True, help="Scroll ID")
    p2.set_defaults(func=cmd_braid)

    p3 = sub.add_parser("registry", help="List validated scrolls in ledger")
    p3.set_defaults(func=cmd_registry)

    p4 = sub.add_parser("export", help="Export registry to JSON")
    p4.add_argument("--output", required=True, help="Output JSON path")
    p4.set_defaults(func=cmd_export)

    p5 = sub.add_parser("preview", help="Live preview of registry and braids")
    p5.add_argument("--interval", type=float, default=1.0, help="Refresh interval seconds")
    p5.set_defaults(func=cmd_preview)

    p6 = sub.add_parser("watch", help="Watch scrolls and auto-process + regenerate braids")
    p6.add_argument("--interval", type=float, default=1.0, help="Polling interval seconds")
    p6.add_argument("--debounce", type=float, default=0.5, help="Batch changes within N seconds before processing")
    p6.add_argument("--dirs", nargs="*", default=[
        os.path.join(ROOT, "vault", "documents"),
        os.path.join(ROOT, "stitchia-protocol-dev", "scrolls"),
    ], help="Directories to watch for .md changes")
    p6.set_defaults(func=cmd_watch)

    # add: create a new scroll from template
    p7 = sub.add_parser("add", help="Create a new scroll from template")
    p7.add_argument("--title", required=True, help="Title for the new scroll")
    p7.add_argument("--out", default=os.path.join(DOCS_DIR, "new_scroll.md"), help="Output path")
    p7.set_defaults(func=cmd_add)

    # status: quick registry summary
    p8 = sub.add_parser("status", help="Show registry summary and ethics flags")
    p8.set_defaults(func=cmd_status)

    # build: rebuild all braids and dashboard data
    p9 = sub.add_parser("build", help="Rebuild all braids and dashboard data")
    p9.set_defaults(func=cmd_build)

    # export-doc: export a scroll to TXT and DOC (RTF)
    p10 = sub.add_parser("export-doc", help="Export a scroll to TXT and DOC (RTF)")
    g = p10.add_mutually_exclusive_group(required=True)
    g.add_argument("--path", help="Path to a markdown scroll")
    g.add_argument("--id", help="Scroll ID from registry")
    p10.add_argument("--outdir", default=os.path.join(ROOT, "stitchia-protocol-dev", "docs", "exports"), help="Output directory")
    p10.set_defaults(func=cmd_export_doc)

    # export-docs-all: batch export all registry scrolls
    p11 = sub.add_parser("export-docs-all", help="Export all registry scrolls to TXT and DOC (RTF)")
    p11.add_argument("--outdir", default=os.path.join(ROOT, "stitchia-protocol-dev", "docs", "exports"), help="Output directory")
    p11.set_defaults(func=cmd_export_docs_all)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
