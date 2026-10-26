#!/usr/bin/env python3
"""Run S-01..S-20 (VP-08) against vpsequence through its Python API. Exit 0 only if every case matches the oracle."""
import json, sys, tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpsequence import VP08Error, render_sequence, print_panels, check_panels  # noqa: E402
from vpsequence.common import publish_dir, no_active_content, NS  # noqa: E402

VEC = json.loads((HERE/'fixtures/s01_s20_materialized.json').read_text('utf-8'))['cases']
ORACLE = {c['id']: c for c in json.loads((HERE/'oracles/independent_s01_s20.json').read_text('utf-8'))['cases']}
G = f'{{{NS}}}g'


def panels(inp, tmp):
    report, files = print_panels(inp['source'], inp['partition'], inp['granularity'], inp['overflow'])
    d = publish_dir(files, Path(tmp)/'panels')
    if inp.get('tamper') == 'drop_message':
        f = d/'panel-01.input.json'
        x = json.loads(f.read_text('utf-8'))
        seq = x['source']['triggers'][0]['sequence']
        seq.pop()
        f.write_text(json.dumps(x, sort_keys=True, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    check_panels(d)  # every export is re-verified; a tampered input must FAIL here
    return {'warnings': report['warnings'], 'report': report, 'files': files,
            'svgs': [b for n, b in sorted(files.items()) if n.startswith('panel-') and n.endswith('.svg')]}


def run(c, tmp):
    inp = c['input']
    if c['op'] == 'sequence':
        rep, svgs = render_sequence(inp['source'], inp['trigger'], inp['granularity'], inp['overflow'])
        return {'warnings': rep['warnings'], 'report': rep, 'svgs': svgs}
    return panels(inp, tmp)


def groups(svg, attr):
    return [g for g in ET.fromstring(svg).iter(G) if g.get(attr)]


def check(c, out):
    x, ok = c['expect'], True
    svg0 = out['svgs'][0]
    if 'messages_drawn' in x:
        ok = ok and len(groups(svg0, 'data-vp08-message')) == x['messages_drawn']
    if x.get('trigger_arrow'):
        ok = ok and len(groups(svg0, 'data-vp08-trigger')) == 1
    if 'distinct_kind_styles' in x:
        sig = {}
        for g in groups(svg0, 'data-vp08-message'):
            lines = [e for e in g if e.tag.endswith('line')]
            sig.setdefault(g.get('data-vp08-kind'), set()).add((len(lines), lines[0].get('stroke-dasharray'), g.get('data-vp08-head')))
        ok = ok and all(len(sig.get(k, ())) == 1 for k in x['distinct_kind_styles'])
        ok = ok and len({next(iter(sig[k])) for k in x['distinct_kind_styles']}) == len(x['distinct_kind_styles'])
    if 'legend_kinds_once' in x:
        kinds = [g.get('data-vp08-legend-kind') for g in groups(svg0, 'data-vp08-legend-kind')]
        ok = ok and all(kinds.count(k) == 1 for k in x['legend_kinds_once'])
    if 'numbering' in x:
        drawn = {g.get('data-vp08-message'): int(g.get('data-vp08-number')) for g in groups(svg0, 'data-vp08-message')}
        ok = ok and out['report']['numbering'] == x['numbering'] and drawn == x['numbering']
    if 'label_lines' in x:
        g = next(g for g in groups(svg0, 'data-vp08-message') if g.get('data-vp08-message') == x['label_lines']['message'])
        ok = ok and len([t for t in g.iter(f'{{{NS}}}text') if t.get('data-vp08-label-line')]) == x['label_lines']['lines']
    if 'full_label_in_title' in x:
        mid = x['full_label_in_title']
        m = next(m for m in c['input']['source']['triggers'][0]['sequence'] if m.get('id') == mid)
        g = next(g for g in groups(svg0, 'data-vp08-message') if g.get('data-vp08-message') == mid)
        ok = ok and m['label'] in g.find(f'{{{NS}}}title').text
        ok = ok and ' '.join(t.text for t in g.iter(f'{{{NS}}}text')).replace(' ', '') == ('1 · '+m['label']).replace(' ', '')
    if 'frame_spans' in x:
        g = next(g for g in groups(svg0, 'data-vp08-frame') if g.get('data-vp08-frame') == x['frame_spans']['frame'])
        ok = ok and g.get('data-vp08-participants').split() == x['frame_spans']['participants']
    if x.get('windows_cover_all'):
        wins = out['report']['windows']
        ids = [m for w in wins for m in w['message_ids']]
        ok = ok and sorted(ids) == sorted(out['report']['numbering']) and len(ids) == len(set(ids))
        ok = ok and len(wins) >= x.get('windows_min', 1) and len(out['svgs']) == len(wins)
    if 'panel_count_min' in x:
        ok = ok and out['report']['panel_count'] >= x['panel_count_min']
    if 'index_triggers' in x:
        ok = ok and len(groups(out['files']['index.svg'], 'data-vp08-index-trigger')) == x['index_triggers']
    if x.get('coverage_complete'):
        ok = ok and out['report']['coverage']['status'] == 'COMPLETE'
    if x.get('no_active_content'):
        ok = ok and all(no_active_content(ET.fromstring(s)) for s in out['svgs'])
    return ok


def main():
    assert {c['id'] for c in VEC} == set(ORACLE), 'vector/oracle id mismatch'
    bad = 0
    for c in VEC:
        o = ORACLE[c['id']]
        assert (c['expected_status'], c['required_codes'], c['forbidden_codes'], c['expect']) == \
            (o['expected_status'], o['required_codes'], o['forbidden_codes'], o['expect']), c['id']+': vector differs from oracle'
        with tempfile.TemporaryDirectory() as tmp:
            try:
                out = run(c, tmp)
                status, codes = 'PASS', [w['code'] for w in out['warnings']]
            except VP08Error as e:
                out, status, codes, msg = None, 'FAIL', [e.code], str(e)
        ok = status == c['expected_status'] and all(k in codes for k in c['required_codes']) and not any(k in codes for k in c['forbidden_codes'])
        if ok and status == 'PASS':
            ok = check(c, out)
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, sorted(set(codes)),
              msg if status == 'FAIL' else '')
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
