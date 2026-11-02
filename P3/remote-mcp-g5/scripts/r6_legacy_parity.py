#!/usr/bin/env python3
"""Check all pre-MILE-011 R5 tool payloads without rewriting R5 evidence.

Discovery is compared by R6 because its release and capabilities intentionally
change. The 87 historical validation and plan chains remain byte-identical.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import r5_parity

HERE = Path(__file__).resolve().parents[1]
OUT = HERE/'evidence/G5_R6_LEGACY_PARITY.json'


def main():
    subprocess.run([sys.executable, '-B', str(HERE/'scripts/assemble_core.py')], check=True, stdout=subprocess.DEVNULL)
    expected = {c['id']: c for c in json.loads((HERE/'evidence/G5_R5_EXPECTATIONS.json').read_text('utf-8'))['calls']}
    with tempfile.TemporaryDirectory() as tmp:
        runtime = Path(tmp)/'rt'
        shutil.copytree(HERE/'.g5-runtime', runtime)
        run = subprocess.run([sys.executable, '-I', '-B', '-c', r5_parity.CHILD,
                              str(runtime), str(HERE/'scripts')], capture_output=True, text=True)
        if run.returncode:
            sys.exit('FAIL: isolated legacy run\n'+run.stderr[-2000:])
        actual = json.loads(run.stdout)['calls']
    rows = []
    for call in actual:
        if call['id'] == 'D-01':
            continue
        reference = expected[call['id']]['steps']
        got = call['steps']
        match = len(got) == len(reference) and all(
            {k: v for k, v in step.items() if k in ('op', 'is_error', 'payload_sha256', 'code', 'svg_sha256')} ==
            {k: v for k, v in exp.items() if k in ('op', 'is_error', 'payload_sha256', 'code', 'svg_sha256')}
            for step, exp in zip(got, reference))
        rows.append({'id': call['id'], 'match': match})
    bad = [r['id'] for r in rows if not r['match']]
    report = {'format': 'aiaeao.cube.g5-r6-legacy-parity/1',
              'release': 'P3-MCP-REMOTE/0.9.0-proof',
              'historical_expectations': 'evidence/G5_R5_EXPECTATIONS.json',
              'calls': len(rows), 'matched': len(rows)-len(bad), 'mismatched': bad, 'rows': rows}
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print(f"{report['matched']}/{report['calls']} historical R5 calls byte-identical; mismatched {bad}")
    return 0 if not bad and len(rows) == 87 else 1


if __name__ == '__main__':
    raise SystemExit(main())
