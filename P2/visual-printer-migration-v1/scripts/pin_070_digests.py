#!/usr/bin/env python3
"""VP-07.1 PD-4 / VP071-01: pin SHA-256 digests of every 0.7.0 output before any 0.7.1 code.

Run once on the unchanged 0.7.0 code (`--write`); afterwards `--check` recomputes the same
outputs with 0.7.0 documents (from-plan with profile 0.7.0) and compares byte digests.
"""
import hashlib, inspect, json, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE/'scripts')); sys.dont_write_bytecode = True
from vpmigration import render_plan, render_styled, from_plan, print_panels  # noqa: E402
from vpmigration.common import encode  # noqa: E402

P070 = 'P2-VP-MIGRATION/0.7.0'
OUT = HERE/'fixtures/regression_070_digests.json'
VEC = json.loads((HERE/'fixtures/v01_v28_materialized.json').read_text('utf-8'))['cases']
GOLD = json.loads((HERE/'fixtures/golden_migration_views.json').read_text('utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fp(*a, **k):
    if 'profile' in inspect.signature(from_plan).parameters:
        k['profile'] = P070
    return from_plan(*a, **k)


def files_digest(files):
    return {n: sha(b) for n, b in sorted(files.items())}


def collect():
    out = {}
    for c in VEC:
        if c['expected_status'] != 'PASS':
            continue
        op, inp = c['op'], c['input']
        if op == 'phases':
            rep, svg = render_plan(inp['plan'], inp['overflow'])
            out[c['id']] = {'svg': sha(svg), 'report': sha(encode(rep))}
        elif op == 'styled':
            rep, svg = render_styled(inp['envelope'])
            out[c['id']] = {'svg': sha(svg), 'report': sha(encode(rep))}
        elif op == 'panels':
            _, files = print_panels(inp['source'], inp['view'], inp['partition'], inp['granularity'], inp.get('lens'))
            out[c['id']] = files_digest(files)
        else:
            src, mapping = fp(inp['context'], inp['plan_id'], inp.get('tracks'), inp.get('track'), inp.get('labels'))
            d = {'source': sha(encode(src)), 'mapping': sha(encode(mapping))}
            if 'then' in inp:
                t = inp['then']
                _, files = print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'))
                d['panels'] = files_digest(files)
            out[c['id']] = d
    g = GOLD
    src, mapping = fp(g['context'], 'mp-acme', tracks=g['tracks'], edge_styles=g['edge_styles'], witness_prefixes=g['witness_prefixes'])
    out['golden:source'] = {'source': sha(encode(src)), 'mapping': sha(encode(mapping))}
    out['golden:phases-subject-standard'] = files_digest(print_panels(src, 'cube.phases', 'subject', 'standard')[1])
    out['golden:flow-subject-standard-execution'] = files_digest(print_panels(src, 'cube.flow', 'subject', 'standard', 'cube.lens.execution')[1])
    s2, _ = fp(g['context'], 'mp-acme', tracks=g['tracks'], track='mail')
    out['golden:phases-track-mail'] = files_digest(print_panels(s2, 'cube.phases', 'subject', 'standard')[1])
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp07-regression-digests/1', 'profile': P070,
                                   'pinned_before': 'any VP-07.1 runtime code (PD-4)', 'digests': cur},
                                  sort_keys=True, indent=1)+'\n', 'utf-8')
        print('pinned', len(cur), 'scenarios'); return
    pinned = json.loads(OUT.read_text('utf-8'))['digests']
    bad = [k for k in pinned if pinned[k] != cur.get(k)]
    for k in bad:
        print('DIFF', k)
    print(f'{len(pinned)-len(bad)}/{len(pinned)} scenarios byte-identical')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
