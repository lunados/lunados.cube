#!/usr/bin/env python3
"""P1 visual grammar conformance: static-only checks and negative controls.

No semantic inference, no deployment, no SVGs, no external dependencies.
"""
from pathlib import Path
import json,hashlib,re
REPO=Path(__file__).resolve().parents[3]
P0=REPO/'AIAEAO_Pure_Cube_P0_v9.4'
PUB=P0/'validation'/'v1'/'visual'

def load(name):return json.loads((PUB/name).read_text(encoding='utf8'))
def checksum(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def validate_plan(plan, registry, formset, colors):
    if not isinstance(plan,dict) or plan.get('profile')!='P1-VG-basic/1.0.0' or plan.get('reference_version')!='v9.4':
        return 'PROFILE_INVALID'
    if not isinstance(plan.get('items'),list):return 'ITEMS_INVALID'
    for item in plan['items']:
        if not isinstance(item,dict):return 'ITEM_INVALID'
        if not isinstance(item.get('label'),str) or not item['label'].strip():return 'LABEL_REQUIRED'
        rid=item.get('anchor_id')
        if rid not in registry:return 'UNKNOWN_ANCHOR'
        row=registry[rid]
        if item.get('form_id') not in formset:return 'FORM_UNKNOWN'
        tok=item.get('color_token')
        if tok is not None:
            if tok not in colors:return 'COLOR_UNKNOWN'
            if row['visual_role']=='relation_operator':return 'ARROW_FORCED_COLOR'
            if tok.startswith('domain.') and tok!=row['domain_accent_token']:return 'DOMAIN_MISMATCH'
            if tok.startswith('status.'):
                if row['visual_role']!='state_marker':return 'STATUS_NONSTATE'
                if not isinstance(item.get('qualified_state_witness_ref'),str) or not item['qualified_state_witness_ref'].strip():return 'STATE_WITNESS_MISSING'
            if tok not in ('relation.default','surface.muted') and not(tok.startswith('domain.') or tok.startswith('status.')):return 'COLOR_UNKNOWN'
        if item.get('qualified_state_witness_ref') is not None and not isinstance(item.get('qualified_state_witness_ref'),str):return 'WITNESS_INVALID'
    return 'PASS'

def main():
    source=json.loads((P0/'v9.4'/'visual'/'symbols.json').read_text(encoding='utf8'))
    reg=load('anchors.json');d=load('form-color.json');schema=load('render-plan.schema.json');ex=load('examples.json');pub=load('manifest.json')
    reference={a['id']:a for a in source['anchors']}
    rows=reg['entries'];idx={r['anchor_id']:r for r in rows}
    assert len(rows)==129==len(reference)==len(idx)
    assert len({r['unicode'] for r in rows})==129
    assert all(reference[k]['glyph']==r['unicode'] and reference[k]['codepoint']==r['codepoint'] and reference[k]['group']==r['home_or_ui'] for k,r in idx.items())
    assert len(source['historical_aliases'])==4
    assert all(r['form_default']=='form.glyph-only' for r in rows)
    assert len([x for x in rows if x['color_policy']=='none_for_operators'])==12
    assert len([x for x in rows if x['domain_accent_token']])==15
    assert len([x for x in rows if x['visual_role']=='dimension_letter'])==5
    assert len([x for x in rows if x['visual_role']=='paired_concept_marker'])==10
    forms={f['id'] for f in d['forms']};colors=d['colors']
    assert len(forms)==12 and len(colors)==17
    assert all(r['form_suggestion'] in forms for r in rows)
    assert d['colors']['domain.epistemology']['hex']=='#2F7D59'
    assert d['colors']['domain.provenance']['hex']=='#7C3AED'
    assert d['colors']['status.pending']['hex']=='#0891B2'
    assert all(re.fullmatch(r'#[A-F0-9]{6}',v['hex']) for v in colors.values())
    assert len(d['constraints'])==11 and len({x['id'] for x in d['constraints']})==11
    assert schema['properties']['profile']['const']==ex['profile']
    assert validate_plan(ex,idx,forms,colors)=='PASS'
    try:
        import jsonschema
    except ImportError:pass
    else:jsonschema.Draft202012Validator.check_schema(schema);jsonschema.validate(ex,schema)
    cases=json.loads((REPO/'P1'/'visual-grammar-v1'/'tests'/'negative_plans.json').read_text())
    for case in cases:
        assert validate_plan(case['plan'],idx,forms,colors)==case['expected'],case['id']
    for key,meta in pub['assets'].items():
        p=P0/meta['href'].replace('https://cube.lunados.net/','')
        assert p.exists() and checksum(p)==meta['sha256'] and p.stat().st_size==meta['bytes'],key
    rmanifest=json.loads((P0/'manifest.json').read_text())
    vmanifest=json.loads((P0/'validation'/'v1'/'manifest.json').read_text())
    assert rmanifest['visual_presentation_profiles']['P1-VG-basic/1.0.0']=='https://cube.lunados.net/validation/v1/visual/manifest.json'
    assert vmanifest['display_extensions']['P1-VG-basic/1.0.0']=='https://cube.lunados.net/validation/v1/visual/manifest.json'
    for k,v in rmanifest['assets'].items():
        p=P0/v['href'].replace('https://cube.lunados.net/','')
        assert p.exists() and checksum(p)==v['sha256'] and p.stat().st_size==v['bytes'],k
    assert not list(PUB.rglob('*.svg')) and not list((REPO/'P1/visual-grammar-v1').rglob('*.svg'))
    # Confirm the immutable v9.4 P0 symbol bytes against the adopted source lock.
    assert checksum(P0/'v9.4/visual/symbols.json')=='7d35d3e855e94f7b77c8c52fa6bddc6265cae57576b1beb5b8869a4170c54656'
    print(f'PASS P1-VG-basic: {len(rows)} v9.4 Unicode anchors; {len(forms)} form choices (11 historical + neutral fallback); {len(colors)} colors; {len(cases)} negative controls; immutable v9.4; public manifest integrity; zero SVG')
if __name__=='__main__':main()
