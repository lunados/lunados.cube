#!/usr/bin/env python3
"""Build fixtures/golden_v075.json (VP075-07, D-9): synthetic, no client data.

Same P1.11 golden plan GM-pos as golden_v073/v074.json, declared expectations for VP-07.5 (from-plan with profile 0.7.5):
method sets of cube.phases with locale de and hidden ledger. Hand count on GM-pos: import names legacy-mail, new-mail,
legacy-files, new-files (9+9+4+4 bars); rebuild names new-mail, new-directory (9+3); retire names legacy-mail,
legacy-files, legacy-directory (9+4+3); rewrite is carried by the 16 `a` bars; g01 (archive-store) is named by none.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
G73 = json.loads((HERE/'fixtures/golden_v073.json').read_text('utf-8'))
EXPECTED = {
    'phases': {'view': 'cube.phases', 'partition': 'method-sets', 'granularity': 'standard', 'locale': 'de', 'hide_ledger': True},
    'set_order': ['migrate.import/v1', 'migrate.rebuild/v1', 'migrate.retire/v1', 'migrate.rewrite/v1', 'none'],
    'set_sizes': {'migrate.import/v1': 26, 'migrate.rebuild/v1': 12, 'migrate.retire/v1': 16, 'migrate.rewrite/v1': 16, 'none': 1},
    'none_cells': ['g01'],
    'texts_contain': ['CUBE.PHASES · DEKLARIERTE SCHRITTE UND ABHÄNGIGKEITEN · Reihenfolge deklariert, keine Zeitachse',
                      'NUR DARSTELLUNG · keine ACG-Validierung, keine Gewähr, keine Autoritätsentscheidung'],
    'texts_exclude': ['DECLARATION LEDGER · each bar is a declared, unverified assertion', 'DEKLARATIONSREGISTER · jeder Balken ist eine deklarierte, ungeprüfte Aussage'],
    'coverage': 'COMPLETE',
}


def main():
    out = {'format': 'aiaeao.cube.vp07-golden/1', 'reference_version': 'v9.4', 'source': 'synthetic (P1.11 golden GM-pos); no client data',
           'gm_pos_sha256': G73['gm_pos_sha256'], 'context': G73['context'], 'plan_id': G73['plan_id'], 'profile': 'P2-VP-MIGRATION/0.7.5',
           'expected': EXPECTED}
    (HERE/'fixtures/golden_v075.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1)+'\n', 'utf-8')
    print('wrote golden')


if __name__ == '__main__':
    main()
