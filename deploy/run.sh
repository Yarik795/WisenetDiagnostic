#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACKAGES="$ROOT/python-packages"

if [[ ! -d "$PACKAGES" ]]; then
  echo "Нет каталога $PACKAGES" >&2
  echo "На Windows с интернетом сначала выполните:" >&2
  echo "  python deploy/download_linux_packages.py" >&2
  exit 1
fi

python3 --version

export PYTHONPATH="$PACKAGES${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT/backend"
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
