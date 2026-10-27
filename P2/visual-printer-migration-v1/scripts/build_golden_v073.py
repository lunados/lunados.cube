#!/usr/bin/env python3
"""Build fixtures/golden_v073.json (VP073-06, D-8): synthetic, no client data.

Takes the P1.11 golden plan GM-pos (binding-context/7: three workstreams, 33 dependencies,
4 transitions with methods, 16 rewrite bindings on dependencies) and declares, by design, what
`cube.phases` panels must show under 0.7.3. The same plan backs VP-09.1 B-19/B-20.
"""
import hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
GM_FILE = REPO/'P1/migration-methods-v1/fixtures/golden_methods_synthetic.json'
EXPECTED = {
    'source_profile': 'P2-VP-MIGRATION/0.7.3',
    'view': {'view': 'cube.phases', 'partition': 'subject', 'granularity': 'standard'},
    'transition_methods': {'t-intro-mail': 'rebuild', 't-mail-cut': 'import, retire', 't-files-switch': 'import, retire',
                           't-directory-switch': 'rebuild, retire'},
    'rewrite_bars': 16,
    'coverage': 'COMPLETE',
}


def main():
    raw = GM_FILE.read_bytes()
    gm = next(c for c in json.loads(raw)['cases'] if c['id'] == 'GM-pos')
    out = {'format': 'aiaeao.cube.vp07-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (P1.11 golden GM-pos); no client data',
           'gm_pos_sha256': hashlib.sha256(raw).hexdigest(), 'context': gm['context'], 'plan_id': gm['context']['migration_plans'][0]['plan_id'],
           'expected': EXPECTED}
    (HERE/'fixtures/golden_v073.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden')


if __name__ == '__main__':
    main()
