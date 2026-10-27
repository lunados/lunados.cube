#!/usr/bin/env python3
"""VP-07.2 VP072-01: pin SHA-256 digests of every 0.7.1 output before any 0.7.2 code.

Run once on the unchanged 0.7.1 code (`--write`); afterwards `--check` recomputes the same
outputs (from-plan with profile 0.7.1) and compares byte digests. 0.7.0 stays covered by
pin_070_digests.py.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import render_plan, from_plan, print_panels  # noqa: E402
from vpmigration.common import encode  # noqa: E402

P071 = 'P2-VP-MIGRATION/0.7.1'
OUT = HERE/'fixtures/regression_071_digests.json'
VEC = json.loads((HERE/'fixtures/w01_w17_materialized.json').read_text('utf-8'))['cases']
GOLD = json.loads((HERE/'fixtures/golden_v071.json').read_text('utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def files_digest(files):
    return {n: sha(b) for n, b in sorted(files.items())}


def fp(*a, **k):
    return from_plan(*a, profile=P071, **k)


def collect():
    out = {}
    for c in VEC:
        if c['expected_status'] != 'PASS' or c['id'] == 'W-17':  # W-17 is a 0.7.0 source (pinned by pin_070)
            continue
        op, inp = c['op'], c['input']
        if op == 'phases':
            rep, svg = render_plan(inp['plan'], inp.get('overflow', 'summarize'))
            out[c['id']] = {'svg': sha(svg), 'report': sha(encode(rep))}
        elif op == 'panels':
            _, files = print_panels(inp['source'], inp['view'], inp['partition'], inp['granularity'], inp.get('lens'))
            out[c['id']] = files_digest(files)
        else:
            src, mapping = fp(inp['context'], inp['plan_id'], steps=inp.get('steps'))
            t = inp['then']
            out[c['id']] = {'source': sha(encode(src)), 'mapping': sha(encode(mapping)),
                            'panels': files_digest(print_panels(src, t['view'], t['partition'], t['granularity'], t.get('lens'))[1])}
    src, mapping = fp(GOLD['context'], 'mp-acme', tracks=GOLD['tracks'])
    out['golden071:source'] = {'source': sha(encode(src)), 'mapping': sha(encode(mapping))}
    out['golden071:phases-track-subject-standard'] = files_digest(print_panels(src, 'cube.phases', 'track,subject', 'standard')[1])
    out['golden071:flow-track-subject-standard'] = files_digest(
        print_panels(src, 'cube.flow', 'track,subject', 'standard', 'cube.lens.execution')[1])
    s3, _ = fp(GOLD['context'], 'mp-acme', tracks=GOLD['tracks'], subjects=['acme:mail-job-09', 'acme:file-job-01', 'acme:account-01'])
    out['golden071:stack-slice'] = files_digest(print_panels(s3, 'cube.phases', 'subject', 'standard')[1])
    sl, _ = fp(GOLD['context'], 'mp-acme', tracks=GOLD['tracks'], steps='p1:p2')
    out['golden071:slice-p1-p2'] = files_digest(print_panels(sl, 'cube.phases', 'track,subject', 'standard')[1])
    return out


def main():
    cur = collect()
    if '--write' in sys.argv:
        OUT.write_text(json.dumps({'format': 'aiaeao.cube.vp07-regression-digests/1', 'profile': P071,
                                   'pinned_before': 'any VP-07.2 runtime code (VP072-01)', 'digests': cur},
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
