"""MILE-009 TASK-057: renderings for the short visual check (I-02 and I-34, German). Run from the lunados.cube root."""
import copy, hashlib, json, sys
from pathlib import Path
ROOT = Path.cwd(); INST = ROOT/'P2/visual-printer-instances-v1'
sys.path.insert(0, str(INST)); sys.dont_write_bytecode = True
from vpinstances.trace import from_trace  # noqa: E402
from vpinstances.view import render_instances  # noqa: E402
from vpinstances.common import encode  # noqa: E402

OUT = ROOT/'docs/10-Evidence/MILE-009/task057'
OUT.mkdir(parents=True, exist_ok=True)
VEC = {c['id']: c for c in json.loads((INST/'fixtures/i01_i34_materialized.json').read_text('utf-8'))['cases']}
rows = []
for cid, name, what in (('I-02', 'I-02-de', 'BPMN-01: zwei Pfade für eine Aktivierung (CF-12), mit LIB-Datensatz'),
                        ('I-34', 'I-34-de', 'BPMN-02-Modell: i1 vollständig, i2 wartet am Join; sechs LIB-Datensätze')):
    c = copy.deepcopy(VEC[cid])
    rep, svg = render_instances(from_trace(c['context'], c['trace'], c['records']), 'de')
    (OUT/f'{name}.svg').write_bytes(svg); (OUT/f'{name}.report.json').write_bytes(encode(rep))
    rows.append(f"| [{name}.svg]({name}.svg) | {what} | `{hashlib.sha256(svg).hexdigest()[:16]}` |")
(OUT/'README.md').write_text('# MILE-009 TASK-057 — Renderings für die Sichtprüfung\n\nErzeugt mit [`render_task057.py`](../render_task057.py) aus den Vektoren I-02 und I-34, Sprache Deutsch; synthetisch.\n\n'
                             '| Datei | Inhalt | SVG SHA-256 (16) |\n|---|---|---|\n'+'\n'.join(rows)+'\n', 'utf-8')
print('\n'.join(rows))
