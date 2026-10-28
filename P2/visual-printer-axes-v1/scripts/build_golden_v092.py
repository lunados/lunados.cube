#!/usr/bin/env python3
"""Build fixtures/golden_v092.json (VP092-08, D-9): synthetic, no client data.

GM-pos (P1.11 golden plan, as golden_axes.json) plus two synthetic Y referents and two Y → Y dependencies:
acme:ops-desk (actor) depends-on acme:archive-store, acme:archive-store recovers-via acme:backup-vault (both all steps).
Declared expectations: Y × Y directed (with hidden empty rows and columns), F × T with arguments, F × Z (every Z column
named by a binding, so nothing hidden), locale de.
"""
import copy, json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
G = json.loads((HERE/'fixtures/golden_axes.json').read_text('utf-8'))


def context():
    c = copy.deepcopy(G['context'])
    base = next(r for r in c['referents'] if r['ref'] == 'acme:archive-store')
    c['referents'] += [dict(copy.deepcopy(base), ref='acme:ops-desk', concept_id='Y:identity-anchor:actor'),
                       dict(copy.deepcopy(base), ref='acme:backup-vault')]
    mp = c['migration_plans'][0]
    allp = [p['phase_id'] for p in mp['phases']]
    mp['dependencies'] += [
        {'dependency_id': 'y01', 'subject': 'acme:ops-desk', 'predicate_id': 'depends-on', 'object': 'acme:archive-store', 'kind': 'job',
         'holds_in': allp, 'witness_ref': 'repo:example/y01'},
        {'dependency_id': 'y02', 'subject': 'acme:archive-store', 'predicate_id': 'recovers-via', 'object': 'acme:backup-vault', 'kind': 'job',
         'holds_in': allp, 'witness_ref': 'repo:example/y02'}]
    return c


EXPECTED = {
    'yy': {'rows': 'Y:referent', 'cols': 'Y:referent',
           'cells': {'acme:ops-desk|acme:archive-store': ['y01 · depends-on'], 'acme:archive-store|acme:backup-vault': ['y02 · recovers-via']}},
    'ft': {'rows': 'F', 'cols': 'T',
           'cell_contains': [{'row': 'migrate.import/v1', 'col': 'p2', 'entry': 't-mail-cut · import: acme:legacy-mail → acme:new-mail'},
                             {'row': 'migrate.rebuild/v1', 'col': 'p1', 'entry': 't-intro-mail · rebuild: acme:new-mail'},
                             {'row': 'migrate.rewrite/v1', 'col': 'p2', 'entry': 'a01a · rewrite: acme:account-01 → acme:new-directory'}]},
    'yy_hidden': {'rows': 'Y:referent', 'cols': 'Y:referent', 'hide_empty': 'both', 'row_values': ['acme:ops-desk', 'acme:archive-store'],
                  'col_values': ['acme:archive-store', 'acme:backup-vault'], 'hidden_rows': ['acme:backup-vault'], 'hidden_cols': ['acme:ops-desk']},
    'fz': {'rows': 'F', 'cols': 'Z:referent', 'hide_empty': 'cols', 'hidden_cols': [], 'coverage': 'COMPLETE'},
    'locale': {'code': 'de', 'texts_contain': ['CUBE.AXES · DEKLARIERTE AUSSAGEN JE ZELLE · kategoriale Matrix, keine Rangfolge, keine Distanz',
                                               'p3 · Ziel']},
}


def main():
    out = {'format': 'aiaeao.cube.vp09-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (P1.11 golden GM-pos + 2 Y → Y); no client data',
           'context': context(), 'plan_id': G['plan_id'], 'profile': 'P2-VP-AXES/0.9.2', 'expected': EXPECTED}
    (HERE/'fixtures/golden_v092.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden')


if __name__ == '__main__':
    main()
