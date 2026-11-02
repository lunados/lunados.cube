"""MILE-011: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis mit der Agent- oder Adapter-Umgebung (Python ≥ 3.11, mcp 2):
    python -I docs/10-Evidence/MILE-011/verify_mile011.py
Schreibt docs/10-Evidence/MILE-011/verification.json. Prüft die Reihenfolge Entscheidung → Spezifikation → Orakel und Pins →
Code → G5-Erwartungen → G5-Code → Live → Sichtprüfung, führt die Gates in einer Kopie von HEAD aus (git archive; committete
Nachweise bleiben unberührt): P1.14 mit Orakel, P1.13 und P1.12, Adapter-Tests, VP-07-Pins 0.7.0–0.7.5, VP-07.6 mit
Kantenprüfung gegen das Orakel, G5 (verify_g5, Gateway-Tests, verify_release, R6-Parität, R5-Altbestand). Liest die
R6-Live-Läufe, das CPU-Ereignis, den Host-Bericht und die Sichtprüfung; prüft Schichten, Prüfsummen und Links.
Auf langsamen Geräten zuerst --prepare und --gate NAME (Abschnitt 2). Nicht wiederholt: Bereitstellung und Live-Aufrufe.
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path.cwd(); EV = ROOT/'docs/10-Evidence/MILE-011'; G5 = 'P3/remote-mcp-g5'; PY = sys.executable
P114 = 'P1/relation-origin-profile-v1'; VP07 = 'P2/visual-printer-migration-v1'


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True)


def run(args, cwd, py=True):
    r = subprocess.run(([PY, '-B'] if py else [])+args, cwd=cwd, capture_output=True, text=True)
    return {'exit': r.returncode, 'tail': (r.stdout+r.stderr).strip().splitlines()[-1:]}


def before(a, b):
    return a != b and git('merge-base', '--is-ancestor', a, b).returncode == 0


def unchanged_since(f, c):
    return git('diff', '--quiet', c, 'HEAD', '--', f).returncode == 0 and not git('status', '--porcelain', '--', f).stdout.strip()


BASE = 'ec18401'   # MILE-010 abgeschlossen; Ausgangspunkt von MILE-011
out = {'head': git('rev-parse', '--short', 'HEAD').stdout.strip(), 'base': BASE, 'python': sys.version.split()[0],
       'note': 'HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum.'}

# 1. Reihenfolge
steps = [('79da657', '64cf9c0', 'Entscheidungen D-1–D-8 vor den Spezifikationsentwürfen'),
         ('e2cf8e3', 'bfe5308', 'Detailfragen Q vor Orakeln, Vektoren und Pins'),
         ('bfe5308', '8dd8b94', 'Orakel, Vektoren und Pins vor dem P1.14-Code'),
         ('bfe5308', '177e24d', 'Orakel, Vektoren und Pins vor dem VP-07.6-Code'),
         ('177e24d', '58ae4a8', 'lokale Umsetzung vor den G5-Erwartungen'),
         ('58ae4a8', 'c120c3c', 'G5-Erwartungen (R6) vor dem G5-Code'),
         ('c120c3c', '4d18689', 'G5-Code vor Live-Läufen und Host-Bericht'),
         ('4d18689', 'e860778', 'Host-Abnahme vor der Sichtprüfung')]
pins = {f'{P114}/oracles/independent_ho01_ho12.json': 'bfe5308', f'{VP07}/oracles/independent_ol01_ol12.json': 'bfe5308',
        f'{VP07}/fixtures/regression_075_digests.json': 'bfe5308', f'{G5}/evidence/G5_R6_EXPECTATIONS.json': '58ae4a8',
        f'{G5}/scripts/r6_expectations.py': '58ae4a8'}
for v in ('070', '071', '072', '073', '074'):
    pins[f'{VP07}/fixtures/regression_{v}_digests.json'] = BASE
order = {'steps': [{'what': w, 'first': a, 'then': b, 'ok': before(a, b)} for a, b, w in steps],
         'pinned_unchanged': {f: unchanged_since(f, c) for f, c in pins.items()}}
order['issues'] = sum(not s['ok'] for s in order['steps']) + sum(not v for v in order['pinned_unchanged'].values())
out['order'] = order

# 2. Gates in einer Kopie von HEAD:  --prepare packt HEAD aus;  --gate NAME führt ein Gate aus und speichert das Ergebnis.
head_full = git('rev-parse', 'HEAD').stdout.strip()
cache = Path(os.environ.get('MILE011_CACHE', Path.home()/'.mile011'))/head_full
tree = cache/'tree'
JOBS = {'p114_tests': (['-m', 'unittest', '-q', 'tests.test_p114'], P114, True),
        'p113_vectors': (['scripts/run_vectors.py'], 'P1/control-flow-profile-v1', True),
        'p112_vectors': (['scripts/run_vectors.py'], 'P1/coverage-instance-profile-v1', True),
        'adapter_tests': (['-m', 'unittest', 'discover', '-s', 'tests', '-q'], 'P3/adapters/mcp-local', True),
        'vp076_vectors': (['scripts/run_vectors_ol.py'], VP07, True),
        'vp076_tests': (['-m', 'unittest', '-q', 'tests.test_vp076'], VP07, True),
        'g5_verify': ([f'{G5}/scripts/verify_g5.py'], '.', True),
        'g5_gateway_tests': (['node', '--test', 'tests/freeze.test.mjs', 'tests/security.test.mjs'], f'{G5}/gateway', False),
        'g5_verify_release': ([f'{G5}/scripts/verify_release.py'], '.', True),
        'g5_r6_parity': ([f'{G5}/scripts/r6_parity.py'], '.', True),
        'g5_r5_legacy_parity': ([f'{G5}/scripts/r6_legacy_parity.py'], '.', True)}
for v in ('070', '071', '072', '073', '074', '075'):
    JOBS[f'vp07_pin_{v}'] = ([f'scripts/pin_{v}_digests.py'], VP07, True)


def prepare():
    if not (tree/'.complete').exists():
        shutil.rmtree(tree, ignore_errors=True); tree.mkdir(parents=True)
        subprocess.run(f'git archive HEAD | tar -x -C "{tree}"', shell=True, cwd=ROOT, check=True)
        (tree/'.complete').write_text(head_full)


def gate(name):
    prepare()
    args, cwd, py = JOBS[name]
    res = run(args, tree/cwd, py=py); res['python'] = sys.version.split()[0]
    (cache/f'{name}.json').write_text(json.dumps(res, ensure_ascii=False)+'\n', 'utf-8')
    return res


if len(sys.argv) > 1:
    if sys.argv[1] == '--prepare':
        prepare(); print('prepared', head_full[:7]); raise SystemExit(0)
    if sys.argv[1] == '--gate':
        r = gate(sys.argv[2]); print(sys.argv[2], 'exit', r['exit'], r['tail']); raise SystemExit(0)
runs = {}
for name in JOBS:
    f = cache/f'{name}.json'
    runs[name] = json.loads(f.read_text('utf-8')) if f.exists() else gate(name)
out['gates'] = {'head_copy': head_full[:7], 'how': 'git archive HEAD, Gates einzeln ausgeführt (Ergebnisse je HEAD zwischengespeichert)'}
out['runs'] = runs

# 3. Live (R6), Host-Bericht, Sichtprüfung
ev = ROOT/G5/'evidence'
live = []
for f in ('G5_R6_LIVE_SCRIPT', 'G5_R6_LIVE_SCRIPT_RUN2', 'G5_R6_LIVE_SCRIPT_RUN3'):
    d = json.loads((ev/f'{f}.json').read_text('utf-8'))
    bad = [r for r in d['rows'] if not r['match']]
    only_unavailable = all(s.get('is_error') and s.get('code') == 'G5_CORE_UNAVAILABLE'
                           for r in bad for s in r.get('steps', []) if not s.get('match'))
    live.append({'run': f, 'matched': d['matched'], 'calls': d['calls'], 'mismatched': d['mismatched'],
                 'gateway_tools': d['gateway_tools_as_expected'], 'gateway_version': d['gateway_health_version_as_expected'],
                 'only_core_unavailable': only_unavailable})
cpu = json.loads((ev/'G5_R6_CORE_CPU_EVENT.json').read_text('utf-8'))
host = json.loads((ev/'G5_R6_HOST_RESULTS.json').read_text('utf-8'))
vis = (EV/'visual-check/SICHTPRUEFUNG.md').read_text('utf-8')
answers = re.findall(r'^\| (S-\d) \|.*\| \*\*(ja|nein)\*\* \|$', vis, flags=re.M)
out['live'] = {'r6_script_runs': live,
               'cpu_event': {'exception': cpu['exception'], 'cpu_ms': cpu['cpuTime_ms'], 'call': cpu['call'], 'core_version': cpu['scriptVersion']},
               'host_results': {k: host[k] for k in ('host_calls', 'matched', 'digests_matched', 'view_steps_with_svg_digests_matched')}}
out['visual_check'] = {'answers': dict(answers), 'all_yes': len(answers) == 6 and all(a == 'ja' for _, a in answers)}
live_ok = (all(r['calls'] == 26 and r['matched'] >= 25 and r['gateway_tools'] and r['gateway_version'] and r['only_core_unavailable']
               for r in live) and 'CpuLimitExceeded' in cpu['exception'] and host['host_calls'] == host['matched'] == 9)

# 4. Schichten und Prüfsummen
frozen = ['AIAEAO_Pure_Cube_P0_v9.4', 'P1', f':(exclude){P114}', 'P2', f':(exclude){VP07}', 'scripts', 'RELEASE_INDEX.md']
sums = {}
for f in sorted(ROOT.glob('**/*SHA256SUMS*.txt')):
    if any(x in f.parts for x in ('.git', '.g5-runtime', 'charge3-p16', '.agent-env', '.wheelhouse', 'node_modules')):
        continue
    r = subprocess.run(['sha256sum', '-c', '--quiet', f.name], cwd=f.parent, capture_output=True, text=True)
    sums[f.relative_to(ROOT).as_posix()] = r.returncode == 0
changed = sorted(git('diff', '--name-only', BASE, 'HEAD', '--', 'AIAEAO_Pure_Cube_P0_v9.4', 'P1', 'P2', 'P3').stdout.split())
allowed = (P114+'/', VP07+'/', G5+'/', 'P3/adapters/mcp-local/')
out['layers'] = {'frozen_unchanged_since_base': git('diff', '--quiet', BASE, 'HEAD', '--', *frozen).returncode == 0,
                 'frozen_worktree_unchanged': git('diff', '--quiet', '--', *frozen).returncode == 0,
                 'changed_outside_allowed': [p for p in changed if not p.startswith(allowed)],
                 'vp07_older_profiles': 'byte-identisch über die Pins 0.7.0–0.7.5 (Abschnitt 2)',
                 'charge3_p16_sums': 'nicht geprüft: Pfade relativ zur Repo-Wurzel, schon vor MILE-011 so',
                 'sha256sums': sums}

# 5. Links
bad, outside = [], set()
for b in ('docs', 'openspec', P114, VP07, G5):
    for d, _, fs in os.walk(ROOT/b):
        if any(x in Path(d).parts for x in ('p0_snapshot', 'node_modules', '.g5-runtime')):
            continue
        for f in fs:
            if f.endswith('.md'):
                p = Path(d)/f
                for t in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', p.read_text(encoding='utf-8')):
                    if t.startswith(('http', 'mailto', 'computer:')) or 'chatgpt' in t:
                        continue
                    tgt = (p.parent/t).resolve()
                    if not tgt.is_relative_to(ROOT.resolve()):
                        outside.add(f'{p.relative_to(ROOT)} -> {t}')
                    elif not tgt.exists():
                        bad.append(f'{p.relative_to(ROOT)} -> {t}')
out['broken_links'] = len(bad); out['broken_link_list'] = sorted(set(bad)); out['links_outside_repo_not_checked'] = sorted(outside)

ok = (out['order']['issues'] == 0 and all(v['exit'] == 0 for v in runs.values()) and live_ok and out['visual_check']['all_yes']
      and out['layers']['frozen_unchanged_since_base'] and out['layers']['frozen_worktree_unchanged']
      and not out['layers']['changed_outside_allowed'] and all(sums.values()) and out['broken_links'] == 0)
out['all_ok'] = bool(ok)
(EV/'verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_ok', bool(ok))
