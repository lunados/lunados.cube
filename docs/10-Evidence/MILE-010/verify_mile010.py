"""MILE-010: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis mit der Agent- oder Adapter-Umgebung (Python ≥ 3.11, mcp 2):
    python -I docs/10-Evidence/MILE-010/verify_mile010.py
Schreibt docs/10-Evidence/MILE-010/verification.json. Prüft die Reihenfolge Entscheidung → Spezifikation → Erwartungen →
Kern/Gateway → Live-Läufe → Host-Bericht, führt die G5-Gates in einer Kopie von HEAD aus (git archive; die committeten
Nachweise bleiben unberührt): verify_g5, Gateway-Tests, Offline-Parität R5 88/88, verify_release, Parität G4/G5 der
P1-Profile. Liest die vier Skript-Läufe live, das CPU-Ereignis und den Host-Bericht; prüft unveränderte Schichten,
Prüfsummen und Links. Auf langsamen Geräten zuerst --prepare und --gate NAME (siehe Abschnitt 2). Nicht wiederholt: Cloudflare-Bereitstellung und Live-Aufrufe (stehen in den Nachweisen).
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path.cwd(); EV = ROOT/'docs/10-Evidence/MILE-010'; G5 = 'P3/remote-mcp-g5'; PY = sys.executable


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True)


def run(args, cwd, py=True):
    r = subprocess.run(([PY, '-B'] if py else [])+args, cwd=cwd, capture_output=True, text=True)
    return {'exit': r.returncode, 'tail': (r.stdout+r.stderr).strip().splitlines()[-1:]}


def before(a, b):
    return a != b and git('merge-base', '--is-ancestor', a, b).returncode == 0


def unchanged_since(f, c):
    return git('diff', '--quiet', c, 'HEAD', '--', f).returncode == 0 and not git('status', '--porcelain', '--', f).stdout.strip()


base = git('merge-base', 'main', 'HEAD').stdout.strip()[:7]
out = {'head': git('rev-parse', '--short', 'HEAD').stdout.strip(), 'main_base': base, 'python': sys.version.split()[0],
       'note': 'HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum.'}

# 1. Reihenfolge
steps = [('c44a89d', '7cc8505', 'Entscheidungen D-1–D-8 vor dem Spezifikationsentwurf'),
         ('d7ed25a', 'a29450a', 'Detailfragen Q-1–Q-10 vor den Erwartungen'),
         ('a29450a', 'd5124d0', 'Erwartungen (87 Aufrufe) vor Kern- und Gateway-Code'),
         ('d5124d0', '75eb528', 'Kern und Gateway vor den Live-Läufen per Skript'),
         ('75eb528', '31d9686', 'Live-Läufe vor dem Host-Bericht')]
pins = [f'{G5}/evidence/G5_R5_EXPECTATIONS.json', f'{G5}/scripts/r5_calls.py', f'{G5}/scripts/r5_expectations.py']
order = {'steps': [{'what': w, 'first': a, 'then': b, 'ok': before(a, b)} for a, b, w in steps],
         'expectations_unchanged_since_a29450a': {f: unchanged_since(f, 'a29450a') for f in pins}}
order['issues'] = sum(not s['ok'] for s in order['steps']) + sum(not v for v in order['expectations_unchanged_since_a29450a'].values())
out['order'] = order

# 2. G5-Gates in einer Kopie von HEAD. Auf einem langsamen Gerät in Teilschritten (je ein Aufruf unter der Zeitgrenze):
#      --prepare     packt HEAD aus (git archive) nach $MILE010_CACHE/<HEAD>/tree
#      --gate NAME   führt ein Gate dort aus und legt das Ergebnis neben die Kopie
#    Der Hauptlauf übernimmt nur Ergebnisse zum aktuellen HEAD und führt fehlende selbst aus.
head_full = git('rev-parse', 'HEAD').stdout.strip()
cache = Path(os.environ.get('MILE010_CACHE', Path.home()/'.mile010'))/head_full
tree = cache/'tree'
JOBS = {'verify_g5': ([f'{G5}/scripts/verify_g5.py'], '.', True),
        'r5_offline_parity': ([f'{G5}/scripts/r5_parity.py'], '.', True),
        'gateway_tests': (['node', '--test', 'tests/freeze.test.mjs', 'tests/security.test.mjs'], f'{G5}/gateway', False),
        'verify_release': ([f'{G5}/scripts/verify_release.py'], '.', True)}
for prof in ('migration-profile-v1', 'migration-profile-v2', 'migration-methods-v1', 'coverage-instance-profile-v1'):
    JOBS[f'parity_g4_g5_{prof}'] = ([f'P1/{prof}/scripts/parity_g4_g5.py'], '.', True)


def prepare():
    if not (tree/'.complete').exists():
        shutil.rmtree(tree, ignore_errors=True); tree.mkdir(parents=True)
        subprocess.run(f'git archive HEAD | tar -x -C "{tree}"', shell=True, cwd=ROOT, check=True)
        (tree/'.complete').write_text(head_full)


def gate(name):
    prepare()
    args, cwd, py = JOBS[name]
    res = run(args, tree/cwd, py=py)
    if name == 'r5_offline_parity':
        par = json.loads((tree/G5/'evidence/G5_R5_OFFLINE_PARITY.json').read_text('utf-8'))
        res['summary'] = {k: par.get(k) for k in ('calls', 'matched', 'cpu_s_max', 'cpu_rule_2s', 'interpreter')}
    res['python'] = sys.version.split()[0]
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
par = runs['r5_offline_parity'].get('summary', {})
out['gates'] = {'head_copy': head_full[:7], 'how': 'git archive HEAD, gates einzeln ausgeführt (Ergebnisse je HEAD zwischengespeichert)'}
out['r5_offline_parity'] = dict(par, ok=par.get('calls') == 88 and par.get('matched') == 88 and par.get('cpu_rule_2s') is True)
out['runs'] = runs

# 3. Live: Skript-Läufe, CPU-Ereignis, Host-Bericht
ev = ROOT/G5/'evidence'
documented = {'P-K07-flow', 'P-K08-sequence'}   # Spezifikation §10: CPU-Grenze des Kerns und Neustart danach
live = []
for i in range(1, 5):
    d = json.loads((ev/f'G5_R5_LIVE_SCRIPT_RUN{i}.json').read_text('utf-8'))
    bad = [r for r in d['rows'] if not r['match']]
    steps_err = all(s['is_error'] for r in bad for s in r.get('steps', []) if not s['match'])
    live.append({'run': i, 'matched': d['matched'], 'calls': d['calls'], 'mismatched': d['mismatched'],
                 'gateway_tools': d['gateway_tools_as_expected'], 'gateway_version': d['gateway_health_version_as_expected'],
                 'only_documented_limit': set(d['mismatched']) <= documented and steps_err})
cpu = json.loads((ev/'G5_R5_CORE_CPU_EVENT.json').read_text('utf-8'))
host = (ev/'G5_R5_HOST_REPORT.md').read_text('utf-8')
cells = [l.rstrip(' |').rsplit('|', 1)[-1].strip() for l in host.splitlines()
         if l.startswith('| ') and l.rstrip().endswith('|') and not l.startswith('| ---')]
out['live'] = {'script_runs': live, 'cpu_event': {'outcome': cpu['outcome'], 'call': cpu['call'], 'core_version': cpu['scriptVersion']},
               'host_report': {'overall_pass': '**PASS.** 7 of 7' in host,
                               'result_cells': {r: cells.count(r) for r in ('PASS', 'FAIL')}}}
live_ok = (all(r['calls'] == 88 and r['gateway_tools'] and r['gateway_version'] and r['only_documented_limit'] for r in live)
           and cpu['outcome'] == 'exceededCpu' and out['live']['host_report']['overall_pass']
           and out['live']['host_report']['result_cells']['FAIL'] == 0)

# 4. Schichten und Prüfsummen
frozen = ['AIAEAO_Pure_Cube_P0_v9.4', 'P1', 'P2', 'P3', f':(exclude){G5}', 'scripts', 'RELEASE_INDEX.md']
sums = {}
for f in sorted(ROOT.glob('**/*SHA256SUMS*.txt')):
    if '.git' in f.parts or '.g5-runtime' in f.parts or 'charge3-p16' in f.parts or '.agent-env' in f.parts or '.wheelhouse' in f.parts:
        continue
    r = subprocess.run(['sha256sum', '-c', '--quiet', f.name], cwd=f.parent, capture_output=True, text=True)
    sums[f.relative_to(ROOT).as_posix()] = r.returncode == 0
out['layers'] = {'frozen_unchanged_since_main': git('diff', '--quiet', base, 'HEAD', '--', *frozen).returncode == 0,
                 'frozen_worktree_unchanged': git('diff', '--quiet', '--', *frozen).returncode == 0,
                 'changed_outside_docs': sorted(git('diff', '--name-only', base, 'HEAD', '--', 'AIAEAO_Pure_Cube_P0_v9.4', 'P1', 'P2', 'P3').stdout.split()),
                 'lunados_lib': 'nicht in diesem Repository; MILE-010 ändert keine Einträge (D-Rahmen)',
                 'sha256sums': sums}
out['layers']['only_g5_changed'] = all(p.startswith(G5+'/') for p in out['layers']['changed_outside_docs'])

# 5. Links
bad = []; outside = set()
for b in ('docs', 'openspec', f'{G5}'):
    for d, _, fs in os.walk(ROOT/b):
        if any(x in Path(d).parts for x in ('p0_snapshot', 'node_modules', '.g5-runtime')):
            continue
        for f in fs:
            if f.endswith('.md'):
                p = Path(d)/f
                for t in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', p.read_text(encoding='utf-8')):
                    if t.startswith(('http', 'mailto')) or 'chatgpt' in t:
                        continue
                    tgt = (p.parent/t).resolve()
                    if not tgt.is_relative_to(ROOT.resolve()):   # Nachbar-Repo (z. B. lunados.lib), hier nicht prüfbar
                        outside.add(f'{p.relative_to(ROOT)} -> {t}')
                    elif not tgt.exists():
                        bad.append(f'{p.relative_to(ROOT)} -> {t}')
out['broken_links'] = len(bad); out['broken_link_list'] = bad; out['links_outside_repo_not_checked'] = sorted(outside)

ok = (out['order']['issues'] == 0 and all(v['exit'] == 0 for v in runs.values()) and out['r5_offline_parity']['ok'] and live_ok
      and out['layers']['frozen_unchanged_since_main'] and out['layers']['frozen_worktree_unchanged'] and out['layers']['only_g5_changed']
      and all(sums.values()) and out['broken_links'] == 0)
out['all_ok'] = bool(ok)
(EV/'verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_ok', bool(ok))
