#!/usr/bin/env python3
"""G5 R5 offline parity (MILE-010 TASK-060): the assembled core equals the local tools for every R5 call.

1. Assembles the core (assemble_core.py) and copies `.g5-runtime` into an empty temporary directory.
2. In a fresh, isolated interpreter (-I) runs every chain of r5_calls.py through core `dispatch`, with an audit hook that
   records every file the core opens (Q-5: nothing outside the staged runtime and the Python standard library).
3. Compares every step with evidence/G5_R5_EXPECTATIONS.json (error flag, payload SHA-256, SVG digests, codes);
   `cube_validate` with `transport` set to the local value (the field is not compared, CL-2). Records CPU time per call (RM-1) and the runtime data files read.
Writes evidence/G5_R5_OFFLINE_PARITY.json. Run from anywhere: python3 P3/remote-mcp-g5/scripts/r5_parity.py
"""
import json, shutil, subprocess, sys, sysconfig, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]

CHILD = r'''
import hashlib, json, sys, time
rt, scripts = sys.argv[1], sys.argv[2]
sys.path.insert(0, scripts)
import r5_calls as RC
calls = RC.calls()                                   # fixtures are read from the repo before the hook is on
sys.path.insert(0, rt)
opened = set()
def hook(ev, args):
    if ev == 'open' and isinstance(args[0], str):
        opened.add(args[0])
sys.addaudithook(hook)
from core_runtime import dispatch
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
def invoke(op, args):
    r = dispatch(op, args)
    p = r['result'] if r['ok'] else r['diagnostic']
    if r['ok'] and op == 'cube_validate':
        p = dict(p); p['transport'] = 'local_mcp_stdio'  # CL-2: transport is not compared; set to the value of the local reference
    return (not r['ok']), p
out = []
for c in calls:
    t = time.process_time()
    steps = RC.run_chain(c, invoke)
    cpu = time.process_time() - t
    facts = []
    for st, (e, p) in zip(c['steps'], steps):
        f = {'op': st['op'], 'is_error': e, 'payload_sha256': hashlib.sha256(canon(p)).hexdigest()}
        if e: f['code'] = p.get('code')
        elif st['op'] == 'cube_plan_views': f['svg_sha256'] = [x['sha256'] for x in p['panels']]
        elif st['op'] == 'cube_discover_surface': f['surface'] = p
        facts.append(f)
    out.append({'id': c['id'], 'cpu_s': round(cpu, 3), 'steps': facts})
print(json.dumps({'calls': out, 'opened': sorted(opened)}))
'''


def get(d, dotted):
    for k in dotted.split('.'):
        d = d[k]
    return d


def main():
    subprocess.run([sys.executable, '-B', str(HERE/'scripts/assemble_core.py')], check=True, stdout=subprocess.DEVNULL)
    exp = json.loads((HERE/'evidence/G5_R5_EXPECTATIONS.json').read_text('utf-8'))
    want = {c['id']: c for c in exp['calls']}
    with tempfile.TemporaryDirectory() as tmp:
        rt = Path(tmp)/'rt'
        shutil.copytree(HERE/'.g5-runtime', rt)
        r = subprocess.run([sys.executable, '-I', '-B', '-c', CHILD, str(rt), str(HERE/'scripts')], capture_output=True, text=True)
        if r.returncode:
            sys.exit('FAIL: core run\n'+r.stderr[-2000:])
        got = json.loads(r.stdout)
        std = {Path(sysconfig.get_paths()[k]).resolve() for k in ('stdlib', 'platstdlib', 'purelib', 'platlib')}
        outside, data = [], []
        for f in got['opened']:
            p = Path(f).resolve()
            if str(p).startswith(str(rt.resolve())):
                if p.suffix not in ('.py', '.pyc') and not p.is_dir():
                    data.append(p.relative_to(rt.resolve()).as_posix())
            elif not any(str(p).startswith(str(s)) for s in std) and not str(p).startswith(str(Path(tmp).resolve())):
                outside.append(str(p))
    rows, bad = [], []
    for c in got['calls']:
        if c['id'] == 'D-01':
            s = c['steps'][0]['surface']
            d = exp['discovery']
            checks = {k: get(s, k) == v for k, v in d.items() if k not in ('unchanged', 'gateway_tools', 'gateway_version')
                      and not k.endswith('false_flags') and not k.endswith('printers')}
            checks['p113_control_flow.false_flags'] = all(s['p113_control_flow'][f] is False for f in d['p113_control_flow.false_flags'])
            checks['domains.P2.plan_views.printers'] = sorted(s['domains']['P2']['plan_views']['printers']) == sorted(d['domains.P2.plan_views.printers'])
            ok = all(checks.values())
            rows.append({'id': 'D-01', 'match': ok, 'checks': checks})
            bad += [] if ok else ['D-01']
            continue
        w = want[c['id']]
        same = [{k: v for k, v in g.items() if k in ('op', 'is_error', 'payload_sha256', 'code', 'svg_sha256')} ==
                {k: v for k, v in x.items() if k in ('op', 'is_error', 'payload_sha256', 'code', 'svg_sha256')}
                for g, x in zip(c['steps'], w['steps'])]
        ok = len(c['steps']) == len(w['steps']) and all(same)
        rows.append({'id': c['id'], 'match': ok, 'cpu_s_core': c['cpu_s'], 'cpu_s_local': w['cpu_s_local']})
        if not ok:
            bad.append(c['id'])
    cpu = sorted(((r['cpu_s_core'], r['id']) for r in rows if 'cpu_s_core' in r), reverse=True)
    rep = {'format': 'aiaeao.cube.g5-r5-offline-parity/1', 'release': 'P3-MCP-REMOTE/0.8.0-proof',
           'expectations': 'evidence/G5_R5_EXPECTATIONS.json', 'interpreter': f'CPython {sys.version.split()[0]} (not Pyodide)',
           'calls': len(rows), 'matched': sum(r['match'] for r in rows), 'mismatched': bad,
           'cpu_s_max': cpu[0][0] if cpu else None, 'cpu_top5': [{'id': i, 'cpu_s': s} for s, i in cpu[:5]],
           'cpu_rule_2s': all(s < 2 for s, _ in cpu), 'files_read_outside_runtime_and_stdlib': outside,
           'runtime_data_files_read': sorted(set(data)), 'rows': rows}
    (HERE/'evidence/G5_R5_OFFLINE_PARITY.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print(f"{rep['matched']}/{rep['calls']} as expected; cpu max {rep['cpu_s_max']} s; outside reads {len(outside)}; data files {len(rep['runtime_data_files_read'])}")
    print('mismatched:', bad)
    sys.exit(0 if not bad and not outside and rep['cpu_rule_2s'] else 1)


if __name__ == '__main__':
    main()
