"""MILE-012: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis (Python ≥ 3.11):
    python -I docs/10-Evidence/MILE-012/verify_mile012.py
Schreibt docs/10-Evidence/MILE-012/verification.json. Prüft: Plan vor den Dokumenten; seit MILE-011 (0d15c4b) keine
Änderung außerhalb der erlaubten Dokumente und Nachweise; jede Zahl in G5_ACCEPTANCE.md und KNOWN_LIMITS.md gegen die
Nachweisdateien; der Live-Ausgangswert nur mit den erwarteten Abweichungen; RELEASE_INDEX.md mit auflösbaren Links und
im Code vorhandenen Versionen; alle Prüfsummenlisten; Links. Kein Live-Aufruf, keine Codeprüfung (kein Code geändert).
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path.cwd(); EV = ROOT/'docs/10-Evidence/MILE-012'; G5 = ROOT/'P3/remote-mcp-g5'; E = G5/'evidence'
BASE = '0d15c4b'
UNAVAILABLE = '1a2e3cff30dd8b6081fbfe1dca30694ff82aad3b8bce1ff941138c82a8506ac8'   # payload digest of G5_CORE_UNAVAILABLE


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True)


def j(p):
    return json.loads(Path(p).read_text('utf-8'))


out = {'head': git('rev-parse', '--short', 'HEAD').stdout.strip(), 'base': BASE, 'python': sys.version.split()[0],
       'note': 'HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum.'}

# 1. Reihenfolge und erlaubte Änderungen
steps = [('f78497d', '0916995', 'Plan vor Ledger und Grenzen-Seite'), ('f78497d', '998943f', 'Plan vor RELEASE_INDEX'),
         ('0916995', '548bc41', 'Grenzen-Seite vor dem Ausgangswert')]
order = [{'what': w, 'ok': a != b and git('merge-base', '--is-ancestor', a, b).returncode == 0} for a, b, w in steps]
allowed_prefix = ('docs/', 'openspec/')
allowed_files = {'RELEASE_INDEX.md', 'P3/remote-mcp-g5/G5_ACCEPTANCE.md', 'P3/remote-mcp-g5/KNOWN_LIMITS.md', 'P3/remote-mcp-g5/SHA256SUMS.txt',
                 'P3/remote-mcp-g5/evidence/G5_M12_BASELINE_R5.json', 'P3/remote-mcp-g5/evidence/G5_M12_BASELINE_R6.json'}
changed = sorted(set(git('diff', '--name-only', BASE, 'HEAD').stdout.split()) | set(git('diff', '--name-only').stdout.split()))
outside = [p for p in changed if not p.startswith(allowed_prefix) and p not in allowed_files]
out['order'] = order; out['changed_outside_allowed'] = outside

# 2. Zahlen in Ledger und Grenzen-Seite gegen die Nachweise
ledger = (G5/'G5_ACCEPTANCE.md').read_text('utf-8'); limits = (G5/'KNOWN_LIMITS.md').read_text('utf-8')
r5o, r6o, r6l = j(E/'G5_R5_OFFLINE_PARITY.json'), j(E/'G5_R6_OFFLINE_PARITY.json'), j(E/'G5_R6_LEGACY_PARITY.json')
r5runs = [j(E/f'G5_R5_LIVE_SCRIPT_RUN{i}.json') for i in range(1, 5)]
r6runs = [j(E/f'G5_R6_LIVE_SCRIPT{s}.json') for s in ('', '_RUN2', '_RUN3')]
host6 = j(E/'G5_R6_HOST_RESULTS.json'); host5 = (E/'G5_R5_HOST_REPORT.md').read_text('utf-8')
cpu5, cpu6 = j(E/'G5_R5_CORE_CPU_EVENT.json'), j(E/'G5_R6_CORE_CPU_EVENT.json')
facts = {
    'R5 offline': f"{r5o['matched']}/{r5o['calls']}" in ledger,
    'R5 live runs': 'LIVE '+', '.join(f"{r['matched']}/{r['calls']}" for r in r5runs) in ledger,
    'R5 host 7/7': '7 of 7' in host5 and 'HOST PASS 7/7' in ledger,
    'R6 offline': f"OFFLINE PASS {r6o['matched']}/{r6o['calls']}" in ledger,
    'R6 legacy': f"R5 legacy {r6l['matched']}/{r6l['calls']}" in ledger,
    'R6 live runs': all(f"{r['matched']}/{r['calls']}" == '25/26' for r in r6runs) and 'LIVE 25/26 in three runs' in ledger,
    'R6 host': host6['host_calls'] == host6['matched'] == 9 and 'HOST PASS 9/9' in ledger,
    'CPU R5': f"{cpu5['cpuTime_ms']} ms" in limits and f"{cpu5['cpuTime_ms']} ms" in ledger,
    'CPU R6': f"{cpu6['cpuTime_ms']} ms" in limits and f"{cpu6['cpuTime_ms']} ms" in ledger,
}
# 3. Ausgangswert: nur erwartete Abweichungen
b5, b6 = j(E/'G5_M12_BASELINE_R5.json'), j(E/'G5_M12_BASELINE_R6.json')


def only_expected(run):
    ok = True
    for r in run['rows']:
        if r['match']:
            continue
        if r['id'] == 'D-01':
            ok &= {k for k, v in r['checks'].items() if not v} == {'release.version', 'remote_adapter.version'}
        else:
            ok &= all(s.get('payload_sha256') == UNAVAILABLE for s in r['steps'] if not s['match'])
    return bool(ok and run['gateway_tools_as_expected'] and run['gateway_health_version_as_expected'])


facts['baseline R5'] = f"{b5['matched']}/{b5['calls']}" == '86/88' and only_expected(b5) and '86/88' in limits
facts['baseline R6'] = f"{b6['matched']}/{b6['calls']}" == '25/26' and only_expected(b6) and '25/26' in limits
out['facts'] = facts

# 4. RELEASE_INDEX: Links und Versionen
idx = (ROOT/'RELEASE_INDEX.md').read_text('utf-8').split('## History')[0]
idx_links = [t for t in re.findall(r'\]\(([^)#\s]+)', idx) if not t.startswith('http')]
# Bereichsangaben („`0.7.0`…`0.7.6`“, „`0.10.1`, `0.11.0`“) tragen nur beim ersten Wert das Präfix; die übrigen Werte ausdrücklich
versions = sorted(set(re.findall(r'P[123]-[A-Z0-9-]+/[0-9][0-9.]*(?:-[a-z0-9]+)?', idx))
                  | {'0.2.0-proof', 'P2-VP-MIGRATION/0.7.6', 'P2-VP-AXES/0.9.2', 'P2-VP-CELLS/0.10.1', 'P2-VP-CELLS/0.11.0'})


def in_code(v):
    return git('grep', '-q', '-F', v, '--', '*.py', '*.mjs').returncode == 0


out['release_index'] = {'links_ok': all((ROOT/t).exists() for t in idx_links),
                        'versions_in_code': {v: in_code(v) for v in versions}}

# 5. Prüfsummen und Links
sums = {}
for f in sorted(ROOT.glob('**/*SHA256SUMS*.txt')):
    if any(x in f.parts for x in ('.git', '.g5-runtime', 'charge3-p16', '.agent-env', '.wheelhouse', 'node_modules')):
        continue
    sums[f.relative_to(ROOT).as_posix()] = subprocess.run(['sha256sum', '-c', '--quiet', f.name], cwd=f.parent,
                                                          capture_output=True).returncode == 0
out['sha256sums'] = sums
bad = []
for b in ('docs', 'openspec', 'P3/remote-mcp-g5', 'RELEASE_INDEX.md'):
    paths = [ROOT/b] if b.endswith('.md') else [Path(d)/f for d, _, fs in os.walk(ROOT/b) for f in fs if f.endswith('.md')]
    for p in paths:
        if any(x in p.parts for x in ('node_modules', '.g5-runtime', 'p0_snapshot')):
            continue
        for t in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', p.read_text(encoding='utf-8')):
            if t.startswith(('http', 'mailto', 'computer:')) or 'chatgpt' in t:
                continue
            tgt = (p.parent/t).resolve()
            if tgt.is_relative_to(ROOT.resolve()) and not tgt.exists():
                bad.append(f'{p.relative_to(ROOT)} -> {t}')
out['broken_links'] = sorted(set(bad))

ok = (all(o['ok'] for o in order) and not outside and all(facts.values()) and out['release_index']['links_ok']
      and all(out['release_index']['versions_in_code'].values()) and all(sums.values()) and not out['broken_links'])
out['all_ok'] = bool(ok)
EV.mkdir(parents=True, exist_ok=True)
(EV/'verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_ok', bool(ok))
