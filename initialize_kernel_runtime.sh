#!/usr/bin/env bash
set -euo pipefail

echo "[Init] Setting up GILC Vault + Kernel runtime..."
mkdir -p vault/documents vault/braids vault/registry kernel
touch vault/.gitkeep vault/documents/.gitkeep vault/braids/.gitkeep vault/registry/.gitkeep
echo "[Init] Done. Paths: vault/documents/, vault/braids/, vault/registry/, kernel/"

