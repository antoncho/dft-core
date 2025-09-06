---
title: "Tech Stack – GILC Fabrica"
classification: Governance+Ethics+StrategicDesign
validators:
  - role: "Architect"
license: Public-Licensed / CodexLinked
tags: [tech, blueprint]
---

# Tech Stack – GILC Fabrica

Core Components
---------------
- CLI: `quantum` entrypoint to kernels and workflows
- Ethics Kernel: config profiles (default/strict/permissive)
- Validator Workflow: seals (`approved`/`rejected`) with audit trail
- Dashboard Builder: merges `dashboard` data from scrolls
- Watcher: debounce batching, full braid rebuild on registry changes
- Exporters: TXT/DOC batch and archive zipper

Data Flow
---------
scroll.md -> process -> ledger.json -> braid.json -> dashboard data -> frontend UI

Profiles
--------
`kernel/config.yml` → `profiles` map with overrides applied at runtime via `--profile`.

CLI Additions
-------------
- `serve` to run a static server for the frontend
- `open` to print file paths for quick access
- `seal` to append validator decisions with timestamps

Extensibility
-------------
- Replace RTF exporter with Pandoc/Weasy if available
- Add JSON-LD/graph exports for braids
- Plug role-gated auth for seals and registry write protection

