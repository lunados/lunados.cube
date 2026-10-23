#!/usr/bin/env python3
"""Static consistency check for P1.1 contract, NOT P1.2+ validation."""
from pathlib import Path
import json,re,hashlib,sys,collections
R=Path(__file__).resolve().parents[1]
def load(f):return json.loads((R/f).read_text(encoding='utf-8'))
profile=load('contract/validation_profile.json'); assert profile['id']=='P1-VC/1.0.0'
keys=load('contract/concept_keys.json')['entries']
assert len(keys)==85 and len({(e['home'],e['concept_key']) for e in keys})==85
assert len([e for e in keys if 'alias_kind' not in e])==80
assert len([e for e in keys if e.get('alias_kind')=='semantic_notation'])==5
assert all(k['instantiation']=='not_instantiable' for k in keys if k.get('alias_kind'))
assert {'X','Y','Z'}=={k['home'] for k in keys}
pr=load('contract/predicate_registry.json')
assert len(pr['reference_vocabulary'])==10 and not pr['built_in_signatures']
sc=load('contract/context.schema.json'); sr=load('contract/report.schema.json')
assert sc['$schema']==sr['$schema']=='https://json-schema.org/draft/2020-12/schema'
assert set(sr['properties']['checks']['required'])==set(profile['required_stage_order'])
assert sr['properties']['overall_status']['enum']==profile['overall_status_values']
diag=load('contract/diagnostics.json')['codes']; cs={c['code'] for c in diag}
assert len(cs)==len(diag)
fixtures=load('fixtures/conformance_cases.json')['cases']; assert len(fixtures)==25
assert len({c['id'] for c in fixtures})==len(fixtures)
assert all(c['expected_overall'] in profile['overall_status_values'] for c in fixtures)
assert all(c.get('expect_code') in cs for c in fixtures if c.get('expect_code'))
ctxs=[load('fixtures/'+x+'.binding-context.json') for x in ('migration','metaphysics')]
assert all(c['source_kind']=='illustrative_fixture' for c in ctxs)
assert all(len(c['predicate_contracts'])==1 and c['predicate_contracts'][0]['origin']=='illustrative_fixture' for c in ctxs)
assert all(r['provenance_status']=='declared_unverified' for c in ctxs for r in c['referents'])
for name,c in zip(('migration','metaphysics'),ctxs):
  assert c['context_id']=='p1-fixture:'+name
  assert c['referents'] and c['predicate_contracts']
  assert all(x['concept_id'] in {k['concept_id'] for k in keys} for x in c['referents'])
lock=load('contract/source_lock.json')
assert len(lock['sources'])==14
source_root=R.parent/'AIAEAO_Pure_Cube_P0_v9.4'
if source_root.is_dir():
 for source in lock['sources']:
  if source['name'].startswith('P0/'):
   p=source_root/source['name'][3:]
   assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256'],p
 source_status='P0 source hash parity confirmed'
else:
 source_status='P0 file parity not checked (source root not adjacent)' 
assert all(re.fullmatch('[0-9a-f]{64}',s['sha256']) for s in lock['sources'])
try:
 from jsonschema import Draft202012Validator
 Draft202012Validator.check_schema(sc)
 Draft202012Validator.check_schema(sr)
 for c in ctxs: Draft202012Validator(sc).validate(c)
 for r in load('fixtures/report_examples.json')['reports']: Draft202012Validator(sr).validate(r)
 schema_checked=True
except ImportError:
 schema_checked=False
print('PASS — P1.1 static consistency: 85 keys (80+5), 10 predicate names, '
      f'{len(diag)} diagnostics, 25 designed cases, 2 scoped contexts, source lock; '
      f'JSON Schemas '+('validated' if schema_checked else 'unchecked (jsonschema optional)')+'; '+source_status)
