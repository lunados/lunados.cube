"""G6 offline gate: plan-view tools, vectors, CLI parity, pinned baseline, frozen G4/G3 regression.

SDK stdio smoke separately: python scripts/sdk_g6_stdio_smoke.py; host acceptance: G6_CLAUDE_ACCEPTANCE.md.
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def run(cmd, expect):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    p = subprocess.run([sys.executable, '-B', *cmd], cwd=BASE, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
    if p.returncode or expect not in p.stdout:
        print(p.stdout[-3000:], file=sys.stderr)
        raise SystemExit(p.returncode or 1)
    return p.stdout


def main():
    out = run(['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_g6_plan_views.py', '-v'], 'OK')
    print('PASS G6 unit tests:', out.split('Ran ')[-1].split(' tests')[0])
    print('PASS', run(['scripts/run_vectors_g6.py'], '18/18 match').strip().splitlines()[-1], '(K-01…K-18)')
    print('PASS', run(['scripts/parity_g6.py'], 'MCP == CLI').strip().splitlines()[-1])
    print('PASS', run(['scripts/pin_g6_baseline.py'], 'byte-identical').strip().splitlines()[-1])
    run(['scripts/verify_g4.py'], 'PASS G4 OFFLINE')
    print('PASS G4/G3 frozen regression (G4 card unchanged; it is also the base of the G5 surface)')
    print('PASS G6 OFFLINE: plan views in memory, CLI parity, limits; SDK smoke and Claude host proof separately')


if __name__ == '__main__':
    main()
