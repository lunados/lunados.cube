#!/usr/bin/env bash
# Run on the networked Mac. Fills .wheelhouse/ (gitignored) with a Linux CPython
# runtime and Linux wheels pinned to the versions of the adapter venv, then writes
# scripts/dev/requirements-agent.lock (committed). Nothing is installed here.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV_PY="$ROOT/P3/adapters/mcp-local/.venv/bin/python"
REQ="$ROOT/P3/adapters/mcp-local/requirements-mcp.txt"
TARGET="linux-x86_64-cp313"
PBS_TAG="${PBS_TAG:-20261013}"
PBS_PY="${PBS_PY:-3.13.16}"
ARCHIVE="cpython-${PBS_PY}+${PBS_TAG}-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz"
BASE="https://github.com/astral-sh/python-build-standalone/releases/download/${PBS_TAG}"
HOUSE="$ROOT/.wheelhouse"
WHEELS="$HOUSE/wheels/$TARGET"
LOCK="$ROOT/scripts/dev/requirements-agent.lock"

[ -x "$VENV_PY" ] || { echo "Adapter venv missing: $VENV_PY" >&2; exit 1; }
mkdir -p "$HOUSE/python" "$WHEELS"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# 1. Pin to exactly what the working Mac adapter venv uses.
"$VENV_PY" -m pip freeze --exclude pip > "$TMP/constraints.txt"

# 2. Linux wheels for CPython 3.13 (agent VM: x86_64, glibc 2.35).
if [ -n "$(ls -A "$WHEELS")" ]; then
  echo "Wheel folder not empty: $WHEELS — remove it to rebuild." >&2; exit 1
fi
"$VENV_PY" -m pip download --disable-pip-version-check -q \
  -r "$REQ" -c "$TMP/constraints.txt" \
  --only-binary=:all: --implementation cp --python-version 3.13 \
  --platform manylinux2014_x86_64 --platform manylinux_2_17_x86_64 \
  --platform manylinux_2_28_x86_64 --platform manylinux_2_31_x86_64 \
  --platform manylinux_2_34_x86_64 --platform manylinux_2_35_x86_64 \
  -d "$WHEELS"

# 3. Linux CPython runtime, checked against the release's published checksum.
if [ ! -f "$HOUSE/python/$ARCHIVE" ]; then
  curl -fsSL -o "$TMP/$ARCHIVE" "$BASE/$ARCHIVE"
  curl -fsSL -o "$TMP/SHA256SUMS" "$BASE/SHA256SUMS"
  EXPECTED="$(grep " $ARCHIVE\$" "$TMP/SHA256SUMS" | awk '{print $1}')"
  ACTUAL="$(shasum -a 256 "$TMP/$ARCHIVE" | awk '{print $1}')"
  [ -n "$EXPECTED" ] && [ "$EXPECTED" = "$ACTUAL" ] || { echo "Runtime checksum mismatch for $ARCHIVE" >&2; exit 1; }
  mv "$TMP/$ARCHIVE" "$HOUSE/python/$ARCHIVE"
fi

# 4. Lock: runtime archive + every wheel by SHA-256.
"$VENV_PY" "$ROOT/scripts/dev/wheelhouse_lock.py" write \
  --wheels "$WHEELS" --archive "$HOUSE/python/$ARCHIVE" --target "$TARGET" --lock "$LOCK"

echo "Done. Commit scripts/dev/requirements-agent.lock; .wheelhouse/ stays local."
