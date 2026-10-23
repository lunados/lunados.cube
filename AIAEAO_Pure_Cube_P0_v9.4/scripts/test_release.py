#!/usr/bin/env python3
"""Pure Cube P0 packaging / consistency tests (no external dependencies)."""
from pathlib import Path
import json, hashlib, re
R=Path(__file__).resolve().parent.parent
M=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
V='v9.4'
assert M['reference_version']==V
assert M['api']['function_invocation_available'] is False
assert not M['api']['writes_available']
for key,entry in M['assets'].items():
    rel=entry['href'].removeprefix(M['canonical_origin']+'/')
    assert not rel.startswith('http'),key
    b=(R/rel).read_bytes()
    assert entry['sha256']==hashlib.sha256(b).hexdigest(),(key,'sha256')
    assert entry['bytes']==len(b),(key,'bytes')
for name in ['core','time','observer']:
    assert M['entrypoints'][name]==M['assets'][name]['href']
def read(p):return json.loads((R/'v9.4'/p).read_text(encoding='utf-8'))
core,time,obs=[read(n+'.json') for n in ['core','time','observer']]
assert core['ontology_definition_homes']==['X','Y','Z']
assert core['coordinates']==['X','Y','Z','F','M']
assert time['coordinate']=='T' and len(time['facets'])==8
assert obs['coordinate']=='O'
assert len(core['ontology']['X']['pairs'])==5
catalog=read('grammar/concepts.json')['concepts']
ids=[c['id'] for c in catalog]; assert len(ids)==len(set(ids))
concepts={c['id']:c for c in catalog}
assert {c['home'] for c in catalog}=={'X','Y','Z'}
for p in core['ontology']['X']['pairs']:
    assert concepts[p['dimension']]['kind']=='dimension'
    assert concepts[p['scope']]['kind']=='scope'
    assert concepts[p['opening']]['kind']=='endpoint'
    assert concepts[p['complement']]['kind']=='endpoint'
assert len([c for c in catalog if c['home']=='X' and c['kind']=='dimension'])==5
assert len([c for c in catalog if c['home']=='X' and c['kind']=='scope'])==5
assert len([c for c in catalog if c['home']=='X' and c['kind']=='endpoint'])==10
arrows=read('grammar/relations.json')
for row in arrows['conceptual_x_logic']+arrows['conceptual_y_arrows']:
    assert row['concept_ref'] in concepts,row['concept_ref']
assert len(arrows['technical_reference_kinds'])==10
constraints=read('grammar/constraints.json')['rules']
assert len(constraints)==32
cids={c['id'] for c in constraints}
assert len(cids)==32
vg=read('visual/symbols.json')
glyphs=vg['anchors']
assert len(glyphs)==129
assert len({r['glyph'] for r in glyphs})==129
assert len({r['id'] for r in glyphs})==129
assert all(len(r['glyph'])==1 for r in glyphs)
assert len(vg['historical_aliases'])==4
sids={r['id'] for r in glyphs}
assert all(a['target_id'] in sids for a in vg['historical_aliases'])
assert all(c.get('visual_semantic_id') in sids for c in catalog if 'visual_semantic_id' in c)
for n in ['migration','metaphysics']:
    e=read('examples/'+n+'.json')
    assert e['reference_version']==V and e['evidence_level']=='scenario_only'
    for ref in e['mapped_referents']:
        assert ref['concept_ref'] in concepts,(n,ref['concept_ref'])
    assert set(e['constraints_observed'])<=cids
for n in ['migration','metaphysics']:
    ast=read('examples/'+n+'.ast.json')
    assert ast['kind']=='relation' and ast['parameters']=={}
    assert ast['predicate_id'] in [r['name'] for r in arrows['technical_reference_kinds']]
    assert ast['subject']['kind']=='reference'
    assert ast['object']['kind']=='reference'
    assert ast['subject']['address']['home']=='Y'
    assert ast['object']['address']['home']=='Y'
    assert (R/'v9.4'/'examples'/(n+'.acg')).read_text().startswith('rel(')
assert (R/'_headers').read_text().find('X-Robots-Tag: noindex')>=0
assert 'Disallow: /' not in (R/'robots.txt').read_text()
assert 'X:α:Event' in (R/'v9.4'/'morphology.md').read_text(encoding='utf-8')
print(f'PASS — {len(M["assets"])} resources; {len(catalog)} concepts; '
      f'{len(glyphs)} glyphs; 4 aliases; 5 X pairs; 8 T facets; '
      '32 constraints; two scenarios; all hashes linked.')
