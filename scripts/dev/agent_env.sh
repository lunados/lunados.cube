#!/usr/bin/env bash
# Run inside the offline agent Linux VM. Builds .agent-env/ (gitignored) from the
# local wheelhouse only: verified CPython runtime, then hash-checked wheels.
# Idempotent: an existing environment is checked, not rebuilt.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TARGET="linux-x86_64-cp313"
LOCK="$ROOT/scripts/dev/requirements-agent.lock"
HOUSE="$ROOT/.wheelhouse"
ENV="$ROOT/.agent-env"
PY="$ENV/venv/bin/python"

[ "$(uname -s)-$(uname -m)" = "Linux-x86_64" ] || { echo "Agent env targets Linux x86_64 only." >&2; exit 1; }
[ -f "$LOCK" ] || { echo "Missing $LOCK — run scripts/dev/build_wheelhouse.sh on the Mac first." >&2; exit 1; }
[ -d "$HOUSE/wheels/$TARGET" ] || { echo "Missing wheelhouse $HOUSE/wheels/$TARGET." >&2; exit 1; }

ARCHIVE="$(python3 "$ROOT/scripts/dev/wheelhouse_lock.py" verify-archive --lock "$LOCK" --dir "$HOUSE/python")"
SHA="$(sha256sum "$ARCHIVE" | cut -c1-12)"
RUNTIME="$ENV/runtime-$SHA"
# One directory per runtime hash; only a completed extraction is ever used.
if [ ! -f "$RUNTIME/.complete" ]; then
  [ ! -e "$RUNTIME" ] || { echo "Incomplete runtime at $RUNTIME — delete it (on the Mac) and rerun." >&2; exit 1; }
  mkdir -p "$RUNTIME"
  # share/terminfo holds names that differ only by case (N/ vs n/) and cannot be
  # unpacked onto a case-insensitive macOS volume; Python does not need it.
  tar -xzf "$ARCHIVE" -C "$RUNTIME" --exclude='python/share/terminfo'
  touch "$RUNTIME/.complete"
fi

if [ ! -x "$PY" ]; then
  "$RUNTIME/python/bin/python3" -m venv "$ENV/venv"
  echo "$SHA" > "$ENV/venv/.runtime"
fi
[ "$(cat "$ENV/venv/.runtime" 2>/dev/null)" = "$SHA" ] || { echo "Existing $ENV/venv was built from another runtime — delete it and rerun." >&2; exit 1; }

"$PY" -m pip install --disable-pip-version-check -q --no-index \
  --find-links "$HOUSE/wheels/$TARGET" --require-hashes -r "$LOCK"

"$PY" - <<'EOF'
import importlib.metadata as m, sys
print('agent env ready:', sys.version.split()[0], 'mcp', m.version('mcp'), 'jsonschema', m.version('jsonschema'))
EOF
echo "Use: $PY -B scripts/research/comparison_runner.py ..."
