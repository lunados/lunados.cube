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

if [ ! -x "$ENV/python/bin/python3" ]; then
  ARCHIVE="$(python3 "$ROOT/scripts/dev/wheelhouse_lock.py" verify-archive --lock "$LOCK" --dir "$HOUSE/python")"
  mkdir -p "$ENV"
  tar -xzf "$ARCHIVE" -C "$ENV"   # install_only archives unpack to ./python
fi

if [ ! -x "$PY" ]; then
  "$ENV/python/bin/python3" -m venv "$ENV/venv"
fi

"$PY" -m pip install --disable-pip-version-check -q --no-index \
  --find-links "$HOUSE/wheels/$TARGET" --require-hashes -r "$LOCK"

"$PY" - <<'EOF'
import importlib.metadata as m, sys
print('agent env ready:', sys.version.split()[0], 'mcp', m.version('mcp'), 'jsonschema', m.version('jsonschema'))
EOF
echo "Use: $PY -B scripts/research/comparison_runner.py ..."
