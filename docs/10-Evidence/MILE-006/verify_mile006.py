"""MILE-006: Abschlussprüfung. Aufruf aus dem Repo-Wurzelverzeichnis (Python mit jsonschema):
    python3 -I docs/10-Evidence/MILE-006/verify_mile006.py
Schreibt docs/10-Evidence/MILE-006/verification.json. Prüft die Reihenfolge Erwartung vor Code, führt die
Vektor- und Testläufe aus (P1.12, Parität G4/G5 offline, VP-10, VP-10.1, Adapter), prüft den Host-Bericht,
unveränderte Schichten, Prüfsummen und Links. Die lange G6-Parität (K-17) steht im TASK-040-Lauf.
"""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
EV = ROOT/'docs/10-Evidence/MILE-006'
PY = sys.executable


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

# 1. Erwartung vor Code
order = [
    ('P3/remote-mcp-g5/evidence/G5_R4_P112_EXPECTATIONS.json', '68ba97f', '49e3893', 'G5-Erwartungen vor Kern und Bereitstellung'),
    ('P2/visual-printer-cells-v1/oracles/independent_o01_o10.json', '507f8a6', 'b2f75f5', 'VP-10.1-Orakel vor dem Printercode'),
    ('P2/visual-printer-cells-v1/fixtures/regression_0100_digests.json', '507f8a6', 'b2f75f5', 'Pins der 0.10.0-Ausgaben vor dem Printercode'),
    ('P2/visual-printer-cells-v1/VP10_1_ACCEPTANCE_SPEC.md', 'ec147e5', 'b2f75f5', 'Entscheidungen Q-1–Q-6 vor dem Printercode'),
]
items = [{'file': f, 'what': w, 'expectation': s, 'code': c, 'before_code': before(s, c),
          'unchanged_since': unchanged_since(f, s) if not f.endswith('.md') else 'status line updated after implementation'} for f, s, c, w in order]
out['order'] = {'items': items, 'issues': sum(1 for i in items if not i['before_code'] or i['unchanged_since'] is False)}

# 2. Läufe
cells = ROOT/'P2/visual-printer-cells-v1'
out['runs'] = {
    'p112_vectors': run(['P1/coverage-instance-profile-v1/scripts/run_vectors.py']),
    'p112_tests': run(['P1/coverage-instance-profile-v1/tests/test_p112.py']),
    'g5_assemble': run(['P3/remote-mcp-g5/scripts/assemble_core.py']),
    'parity_g4_g5': run(['P1/coverage-instance-profile-v1/scripts/parity_g4_g5.py']),
    'vp10_vectors_j': run(['scripts/run_vectors.py'], cells),
    'vp10_tests': run(['tests/test_vp10.py'], cells),
    'vp101_vectors_o': run(['scripts/run_vectors_o.py'], cells),
    'vp100_pins': run(['scripts/pin_0100_digests.py'], cells),
    'vp101_tests': run(['tests/test_vp101.py'], cells),
    'adapter_tests': run(['-m', 'unittest', 'tests.test_mile006_order', 'tests.test_mile005_adapter', 'tests.test_validation_discovery'],
                         ROOT/'P3/adapters/mcp-local'),
}
t40 = json.loads((EV/'task040-run.json').read_text('utf-8'))
out['g6_parity_from_task040'] = t40['tests']['mcp-local/test_g6_plan_views']

# 3. Host-Abnahme und Sichtprüfung
host = (ROOT/'P3/remote-mcp-g5/evidence/G5_R4_P112_HOST_REPORT.md').read_text('utf-8')
rows = [l for l in host.splitlines() if l.startswith('| ') and l.rstrip().endswith('|') and not l.startswith('| ---')]
results = [l.rstrip(' |').rsplit('|', 1)[-1].strip() for l in rows]
out['host_acceptance'] = {'report': 'P3/remote-mcp-g5/evidence/G5_R4_P112_HOST_REPORT.md', 'overall_pass': '**PASS.**' in host,
                          'result_cells': {r: results.count(r) for r in sorted(set(results)) if r in ('PASS', 'FAIL')},
                          'deployed_version': '42e7b8a9-0086-43fd-bb33-1757fae1f32c' in host}
vis = (EV/'SICHTPRUEFUNG.md').read_text('utf-8')
out['visual_check'] = {'guide': 'docs/10-Evidence/MILE-006/SICHTPRUEFUNG.md', 'user_answer': '1–7 ja' if 'Nutzer: 1–7 ja' in vis else None}

# 4. Schichten und Prüfsummen
frozen = ['AIAEAO_Pure_Cube_P0_v9.4'] + [f'P1/{d}' for d in ('semantic-validator-v1', 'instantiation-profile-v1', 'simulation-profile-v1',
          'comparison-profile-v1', 'migration-profile-v1', 'migration-profile-v2', 'migration-methods-v1', 'contract-v1', 'release-v1',
          'visual-grammar-v1')] \
    + [f'P2/{d}' for d in ('visual-printer-2d-lab', 'visual-printer-axes-v1', 'visual-printer-conformance-v1', 'visual-printer-granularity-v1',
                          'visual-printer-migration-v1', 'visual-printer-release-v1', 'visual-printer-sequence-v1')]
p112_changed = sorted(git('diff', '--name-only', base, 'HEAD', '--', 'P1/coverage-instance-profile-v1').stdout.split())
sums = {}
for f in sorted(ROOT.glob('**/*SHA256SUMS*.txt')):
    if '.git' in f.parts or '.g5-runtime' in f.parts or 'charge3-p16' in f.parts:   # P3/charge3-p16: historical, stale before MILE-005
        continue
    r = subprocess.run(['shasum', '-a', '256', '-c', f.name], cwd=f.parent, capture_output=True, text=True)
    sums[f.relative_to(ROOT).as_posix()] = r.returncode == 0
out['layers'] = {'frozen_unchanged_since_main': git('diff', '--quiet', base, 'HEAD', '--', *frozen).returncode == 0,
                 'frozen_worktree_unchanged': git('diff', '--quiet', '--', *frozen).returncode == 0,
                 'p112_changed_files': p112_changed,
                 'p112_code_unchanged': set(p112_changed) <= {'P1/coverage-instance-profile-v1/README.md',
                                                             'P1/coverage-instance-profile-v1/scripts/parity_g4_g5.py'},
                 'vp100_byte_identity': 'via fixtures/regression_0100_digests.json (vp100_pins)',
                 'changed_outside_docs': sorted(git('diff', '--name-only', base, 'HEAD', '--', 'P0', 'P1', 'P2', 'P3').stdout.split()),
                 'sha256sums': sums}

# 5. Links
bad = []
for b in ('docs', 'openspec', 'P2/visual-printer-cells-v1', 'P3/remote-mcp-g5/evidence'):
    for d, _, fs in os.walk(ROOT/b):
        for f in fs:
            if f.endswith('.md'):
                p = Path(d)/f
                for t in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', p.read_text(encoding='utf-8')):
                    if t.startswith(('http', 'mailto')) or 'chatgpt' in t:
                        continue
                    if not (p.parent/t).resolve().exists():
                        bad.append(f'{p.relative_to(ROOT)} -> {t}')
out['broken_links'] = len(bad); out['broken_link_list'] = bad

ok = (out['order']['issues'] == 0 and all(v['exit'] == 0 for v in out['runs'].values())
      and out['host_acceptance']['overall_pass'] and out['host_acceptance']['deployed_version'] and out['visual_check']['user_answer']
      and out['layers']['frozen_unchanged_since_main'] and out['layers']['frozen_worktree_unchanged']
      and out['layers']['p112_code_unchanged'] and all(sums.values()) and out['broken_links'] == 0)
out['all_ok'] = bool(ok)
(EV/'verification.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n', 'utf-8')
print('all_ok', bool(ok))
