#!/usr/bin/env python3
"""Build fixtures/golden_axes.json (VP09-07, D-11): synthetic, no client data.

Takes the P1.11 golden plan GM-pos (three workstreams mail/files/identity, 33 dependencies,
4 transitions, every transition and successor bound to a catalog method; binding-context/7)
and declares, by design, what the three priority views must show over panels at standard.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
GM = {c['id']: c for c in json.loads((REPO/'P1/migration-methods-v1/fixtures/golden_methods_synthetic.json').read_text('utf-8'))['cases']}
EXPECTED = {
    'views': [{'rows': 'Z:referent', 'cols': 'T', 'coverage': 'COMPLETE'},
              {'rows': 'Y:referent', 'cols': 'T', 'coverage': 'COMPLETE'},
              {'rows': 'F', 'cols': 'Z:referent', 'coverage': 'COMPLETE'}],
    'z_kind_order': ['Integration', 'Provider', 'ThirdPartyDependency'],
    'method_order': ['migrate.import/v1', 'migrate.rebuild/v1', 'migrate.retire/v1', 'migrate.rewrite/v1'],
    'method_bindings': 23,
    'f_cells': [{'row': 'migrate.retire/v1', 'col': 'acme:legacy-mail', 'entry': 't-mail-cut (retired)'},
                {'row': 'migrate.rewrite/v1', 'col': 'acme:new-directory', 'entry': 'a01a (new_object)'}],
    'y_cells': [{'row': 'acme:archive-store', 'col': 'p1', 'entry': 'g01'}],
}


def main():
    out = {'format': 'aiaeao.cube.vp09-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (P1.11 golden GM-pos); no client data',
           'context': GM['GM-pos']['context'], 'plan_id': 'mp-acme', 'expected': EXPECTED}
    (HERE/'fixtures/golden_axes.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden')


if __name__ == '__main__':
    main()
