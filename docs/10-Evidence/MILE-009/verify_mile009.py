"""MILE-009: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis (Python mit jsonschema):
    python3 -I docs/10-Evidence/MILE-009/verify_mile009.py
Schreibt docs/10-Evidence/MILE-009/verification.json. Prüft die Reihenfolge Erwartung vor Code, führt Vektoren, Pins und
Tests aus (VP-11, VP-10, Adapter), prüft die Sichtprüfung, unveränderte Schichten, Prüfsummen und Links.
Die vollständige G6-Suite (K-01…K-18) läuft wegen K-17 nicht in der Zeitgrenze des Geräts; hier laufen ihre übrigen Klassen,
die ganze Suite lief in TASK-056 (siehe TASK-056).
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path.cwd(); EV = ROOT/'docs/10-Evidence/MILE-009'; INST = ROOT/'P2/visual-printer-instances-v1'; PY = sys.executable
AD = ROOT/'P3/adapters/mcp-local'


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True)


def run(args, cwd=ROOT):
    r = subprocess.run([PY, '-B', *args], cwd=cwd, capture_output=True, text=True)
    return {'exit': r.returncode, 'tail': (r.stdout+r.stderr).strip().splitlines()[-1:]}


def before(a, b):
    return a != b and git('merge-base', '--is-ancestor', a, b).returncode == 0


def unchanged_since(f, c):
    return git('diff', '--quiet', c, 'HEAD', '--', f).returncode == 0 and not git('status', '--porcelain', '--', f).stdout.strip()


base = git('merge-base', 'main', 'HEAD').stdout.strip()[:7]
out = {'head': git('rev-parse', '--short', 'HEAD').stdout.strip(), 'main_base': base,
       'note': 'HEAD vor dem Abschluss-Commit; Statusänderungen dieses Commits liegen im Arbeitsbaum.'}
items = [{'file': f, 'what': w, 'expectation': s, 'code': c, 'before_code': before(s, c), 'unchanged_since': unchanged_since(f, s)}
         for f, s, c, w in (('docs/02-Milestones/MILE-009-instance-view.md', '25133a0', '0b5b114', 'Entscheidungen D-1–D-8 vor der Spezifikation'),
                            ('P2/visual-printer-instances-v1/oracles/independent_i01_i34.json', 'e842081', 'ba33c79', 'Orakel vor dem Printer-Code'),
                            ('P2/visual-printer-instances-v1/fixtures/i01_i34_materialized.json', 'e842081', 'ba33c79', 'Vektoren vor dem Printer-Code'),
                            ('P2/visual-printer-instances-v1/fixtures/regression_vp10_0110_digests.json', 'e842081', 'bf678a9', 'Pins VP-10 0.11.0 vor der G6-Änderung'))]
items[0]['unchanged_since'] = None  # der Milestone wird fortgeschrieben; geprüft wird nur die Reihenfolge
q_order = before('0b5b114', '5ab75cc') and before('5ab75cc', 'e842081')
out['order'] = {'items': items, 'spec_draft_before_decisions_before_vectors': q_order,
                'issues': sum(1 for i in items if not i['before_code'] or i['unchanged_since'] is False) + (0 if q_order else 1)}
jobs = {'vp11_vectors': (['scripts/run_vectors.py'], INST), 'vp11_tests': (['tests/test_vp11.py'], INST),
        'vp10_0110_pins': (['scripts/pin_vp10_0110_digests.py'], INST),
        'vp10_s_vectors': (['scripts/run_vectors_s.py'], ROOT/'P2/visual-printer-cells-v1'),
        'vp10_0101_pins': (['scripts/pin_0101_digests.py'], ROOT/'P2/visual-printer-cells-v1'),
        'vp10_0100_pins': (['scripts/pin_0100_digests.py'], ROOT/'P2/visual-printer-cells-v1'),
        'adapter_mile005_009': (['-m', 'unittest', 'tests.test_mile009_instances', 'tests.test_mile008_adapter', 'tests.test_mile007_statements',
                                 'tests.test_mile006_order', 'tests.test_mile005_adapter', 'tests.test_validation_discovery', 'tests.test_g4_surface'], AD),
        'adapter_p1_validation': (['-m', 'unittest', 'tests.test_p1_validation'], AD),
        'adapter_g6_without_vectors': (['-m', 'unittest', 'tests.test_g6_plan_views.Rows', 'tests.test_g6_plan_views.Surface',
                                        'tests.test_g6_plan_views.C12', 'tests.test_g6_plan_views.Server'], AD),
        'adapter_g6_contract': (['-m', 'unittest', 'tests.test_g6_plan_views.Contract'], AD)}
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = {k: ex.submit(run, *v) for k, v in jobs.items()}
out['runs'] = {k: futs[k].result() for k in jobs}
sp = (EV/'SICHTPRUEFUNG.md').read_text('utf-8')
out['visual_check'] = {'answers': '1–5 ja', 'recorded': '1–5 ja' in sp and '## Ergebnis' in sp}
frozen = ['AIAEAO_Pure_Cube_P0_v9.4', 'P1', 'P3/remote-mcp-g5'] + [str(p.relative_to(ROOT)) for p in sorted((ROOT/'P2').iterdir())
                                                                  if p.is_dir() and p.name != 'visual-printer-instances-v1']
sums = {}
for f in sorted(ROOT.glob('**/*SHA256SUMS*.txt')):
    if '.git' in f.parts or '.g5-runtime' in f.parts or 'charge3-p16' in f.parts:
        continue
    r = subprocess.run(['shasum', '-a', '256', '-c', f.name], cwd=f.parent, capture_output=True, text=True)
    sums[f.relative_to(ROOT).as_posix()] = r.returncode == 0
out['layers'] = {'frozen_unchanged_since_main': git('diff', '--quiet', base, 'HEAD', '--', *frozen).returncode == 0,
                 'frozen_worktree_unchanged': git('diff', '--quiet', '--', *frozen).returncode == 0,
                 'changed_outside_docs': sorted(git('diff', '--name-only', base, 'HEAD', '--', 'P0', 'P1', 'P2', 'P3').stdout.split()), 'sha256sums': sums}
bad = []
for b in ('docs', 'openspec', 'P2/visual-printer-instances-v1', 'P3/adapters/mcp-local'):
    for d, _, fs in os.walk(ROOT/b):
        if 'p0_snapshot' in Path(d).parts:  # eingefrorene P0-Kopie, Links zeigen auf nicht mitkopierte Dokumente
            continue
        for f in fs:
            if f.endswith('.md'):
                p = Path(d)/f
                for t in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', p.read_text(encoding='utf-8')):
                    if t.startswith(('http', 'mailto')) or 'chatgpt' in t:
                        continue
                    if not (p.parent/t).resolve().exists():
                        bad.append(f'{p.relative_to(ROOT)} -> {t}')
out['broken_links'] = len(bad); out['broken_link_list'] = bad
ok = (out['order']['issues'] == 0 and all(v['exit'] == 0 for v in out['runs'].values()) and out['visual_check']['recorded']
      and out['layers']['frozen_unchanged_since_main'] and out['layers']['frozen_worktree_unchanged'] and all(sums.values()) and out['broken_links'] == 0)
out['all_ok'] = bool(ok)
(EV/'verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_ok', bool(ok))
