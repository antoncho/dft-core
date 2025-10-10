GILC Fabrica – Quantum Kernel & Scroll Infrastructure
====================================================

Quick Start
-----------

1) Boot the shell

    chmod +x quantum_kernel_shell.sh
    ./quantum_kernel_shell.sh

2) Initialize and explore

    ./quantum init --with-example
    ./quantum status

3) Live workflows

    ./quantum watch            # watches scrolls (debounce 0.5s default)
    ./quantum preview          # live registry + braid summary

4) Core commands

    ./quantum process path/to/scroll.md
    ./quantum braid --id <scroll_id>
    ./quantum registry
    ./quantum export --output vault/registry/export.json
    ./quantum build            # rebuild braids + dashboard data
    ./quantum add --title "🧬 Scroll: My New Scroll" --out vault/documents/my_scroll.md

What happens under the hood
---------------------------
- Ethics, ontology, and signatures are computed on `process`.
- Braid files are generated per scroll in `vault/braids/<id>.json`.
- Registry is stored at `vault/registry/ledger.json`.
- Dashboard data is auto-built to `stitchia-protocol-dev/frontend/data.json` from dashboard-tagged scrolls.

Config
------
`kernel/config.yml` controls ethics filters and braid weighting.

Authoring scrolls
-----------------
- Use `templates/scroll_template.md` or `./quantum add --title ...`.
- Frontmatter fields honored: `title`, `classification`, `validators`, `license`, `tags`, `links`, and optional `dashboard` (inline JSON).

Frontend
--------
- Open `stitchia-protocol-dev/frontend/index.html` directly; it consumes `frontend/data.json`.

Community
---------
- Validator briefings, roadmap drops, and live demos: TikTok `@stitchiabites`
