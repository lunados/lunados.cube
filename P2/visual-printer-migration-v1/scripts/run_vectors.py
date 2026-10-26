#!/usr/bin/env python3
"""Run V-01..V-28 against vpmigration through its Python API. Exit 0 only if every case matches the oracle."""
import hashlib, json, shutil, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; P2 = HERE.parent
sys.path.insert(0, str(HERE)); sys.dont_write_bytecode = True
from vpmigration import VP07Error, render_plan, render_styled, from_plan, print_panels, check_panels  # noqa: E402
from vpmigration.common import publish_dir  # noqa: E402

VEC = json.loads((HERE/'fixtures/v01_v28_materialized.json').read_text('utf-8'))['cases']


def panels(inp, tmp):
    report, files = print_panels(inp['source'], inp['view'], inp['partition'], inp['granularity'], inp.get('lens'))
    d = publish_dir(files, Path(tmp)/'panels')
    if inp.get('tamper') == 'ledger':
        rep = json.loads((d/'report.json').read_text('utf-8'))
        e = next(x for x in rep['panel_ledger'] if len(x['shown_cell_ids']) > 1)
        e['shown_cell_ids'] = e['shown_cell_ids'][1:]
        (d/'report.json').write_text(json.dumps(rep, sort_keys=True, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    elif inp.get('tamper') == 'svg':
        f = d/'panel-01.svg'
        f.write_bytes(f.read_bytes().replace(b'CUBE.PHASES', b'CUBE.PHASEZ', 1))
    if inp.get('tamper'):
        check_panels(d)
    else:
        check_panels(d)  # every successful export is re-verified
    return {'warnings': report['warnings'], 'coverage': report['coverage']}, None


def run(c, tmp):
    op, inp = c['op'], c['input']
    if op == 'phases':
        rep, svg = render_plan(inp['plan'], inp['overflow'])
        return rep, svg
    if op == 'styled':
        return render_styled(inp['envelope'])
    if op == 'panels':
        return panels(inp, tmp)
    src, mapping = from_plan(inp['context'], inp['plan_id'], inp.get('tracks'), inp.get('track'), inp.get('labels'))
    if 'then' in inp:
        t = inp['then']
        return panels({'source': src, **t}, tmp)
    return {'warnings': [], 'mapping': mapping}, None


def check(c, out, svg):
    x = c['expect']
    codes = [w['code'] for w in out.get('warnings', [])]
    ok = all(code in codes for code in c['required_codes'])
    if x.get('omitted_cells_nonempty'):
        ok = ok and bool(out['omitted_cells'])
    if x.get('legend_rendered'):
        ok = ok and b'data-vp07-legend' in svg
    if x.get('svg_byte_identical_to_vp06'):
        ok = ok and svg == (P2/c['input']['vp06_svg']).read_bytes()
    if x.get('base_svg_equals_vp06'):
        ok = ok and out['base_svg_sha256'] == hashlib.sha256((P2/c['input']['vp06_svg']).read_bytes()).hexdigest() and svg != (P2/c['input']['vp06_svg']).read_bytes()
    if x.get('coverage_complete'):
        ok = ok and out['coverage']['status'] == 'COMPLETE'
    if 'epistemic_warrant' in out:
        ok = ok and all(out[k] == 'NOT_EVALUATED' for k in ('epistemic_warrant', 'current_authority', 'canonical_admission'))
    return ok


def main():
    bad = 0
    for c in VEC:
        tmp = tempfile.mkdtemp(prefix='vp07-vec-')
        try:
            try:
                out, svg = run(c, tmp)
                status, codes, ok = 'PASS', [w['code'] for w in out.get('warnings', [])], None
                ok = c['expected_status'] == 'PASS' and check(c, out, svg)
            except VP07Error as e:
                status, codes = 'FAIL', [e.code]
                ok = c['expected_status'] == 'FAIL' and all(code in codes for code in c['required_codes'])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        bad += not ok
        print('PASS' if ok else 'FAIL', c['id'], 'expected', c['expected_status'], c['required_codes'], '| got', status, codes)
    print(f'{len(VEC)-bad}/{len(VEC)} match')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
