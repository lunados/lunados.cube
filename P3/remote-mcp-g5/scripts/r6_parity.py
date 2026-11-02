#!/usr/bin/env python3
"""Compare all fixed MILE-011 calls with an isolated assembled G5 core.

The reused R5 child harness audits file reads and normalizes only the P1
transport field. Its call list is replaced by the committed R6 list.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path
import r5_parity

HERE = Path(__file__).resolve().parents[1]
OUT = HERE/'evidence/G5_R6_OFFLINE_PARITY.json'


def _get(obj, path):
    for key in path.split('.'):
        obj = obj[key]
    return obj


def main():
    subprocess.run([sys.executable, '-B', str(HERE/'scripts/assemble_core.py')], check=True, stdout=subprocess.DEVNULL)
    expected = json.loads((HERE/'evidence/G5_R6_EXPECTATIONS.json').read_text('utf-8'))
    want = {c['id']: c for c in expected['calls']}
    child = r5_parity.CHILD.replace('import r5_calls as RC', 'import r6_calls as RC')
    with tempfile.TemporaryDirectory() as tmp:
        runtime = Path(tmp)/'rt'
        shutil.copytree(HERE/'.g5-runtime', runtime)
        run = subprocess.run([sys.executable, '-I', '-B', '-c', child, str(runtime), str(HERE/'scripts')],
                             capture_output=True, text=True)
        if run.returncode:
            sys.exit('FAIL: isolated R6 core run\n'+run.stderr[-2000:])
        actual = json.loads(run.stdout)
        std = {Path(sysconfig.get_paths()[k]).resolve() for k in ('stdlib', 'platstdlib', 'purelib', 'platlib')}
        outside, data = [], []
        for name in actual['opened']:
            path = Path(name).resolve()
            if str(path).startswith(str(runtime.resolve())):
                if path.suffix not in ('.py', '.pyc') and not path.is_dir():
                    data.append(path.relative_to(runtime.resolve()).as_posix())
            elif not any(str(path).startswith(str(s)) for s in std) and not str(path).startswith(str(Path(tmp).resolve())):
                outside.append(str(path))
    rows, mismatched = [], []
    for call in actual['calls']:
        if call['id'] == 'D-01':
            surface = call['steps'][0]['surface']
            checks = {k: _get(surface, k) == v for k, v in expected['discovery'].items()
                      if k not in ('gateway_tools', 'gateway_version')}
            match = all(checks.values())
            rows.append({'id': 'D-01', 'match': match, 'checks': checks})
        else:
            reference = want[call['id']]['steps']
            got = call['steps']
            match = len(got) == len(reference) and all(
                {k: v for k, v in step.items() if k in ('op', 'is_error', 'payload_sha256', 'code', 'svg_sha256')} ==
                {k: v for k, v in exp.items() if k in ('op', 'is_error', 'payload_sha256', 'code', 'svg_sha256')}
                for step, exp in zip(got, reference))
            rows.append({'id': call['id'], 'match': match, 'cpu_s_core': call['cpu_s'],
                         'cpu_s_local': want[call['id']]['cpu_s_local']})
        if not match:
            mismatched.append(call['id'])
    cpu = sorted(((r['cpu_s_core'], r['id']) for r in rows if 'cpu_s_core' in r), reverse=True)
    report = {'format': 'aiaeao.cube.g5-r6-offline-parity/1', 'release': expected['release'],
              'expectations': 'evidence/G5_R6_EXPECTATIONS.json',
              'interpreter': f'CPython {sys.version.split()[0]} (not Pyodide)',
              'calls': len(rows), 'matched': sum(r['match'] for r in rows), 'mismatched': mismatched,
              'cpu_s_max': cpu[0][0] if cpu else None,
              'cpu_top5': [{'id': ident, 'cpu_s': sec} for sec, ident in cpu[:5]],
              'cpu_rule_2s': all(sec < 2 for sec, _ in cpu),
              'files_read_outside_runtime_and_stdlib': outside,
              'runtime_data_files_read': sorted(set(data)), 'rows': rows}
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print(f"{report['matched']}/{report['calls']} as expected; CPU max {report['cpu_s_max']} s; "
          f"outside reads {len(outside)}; data files {len(report['runtime_data_files_read'])}")
    print('mismatched:', mismatched)
    return 0 if not mismatched and not outside and report['cpu_rule_2s'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
