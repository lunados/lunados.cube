#!/usr/bin/env python3
"""Independent JSON Schema oracle for emitted P1.4 reports (optional dependency)."""
import copy
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
try:
    from jsonschema import Draft202012Validator
except ImportError:
    print('SKIP — install jsonschema to run independent report-schema validation')
    raise SystemExit(0)
from cube_semantic.validator import SemanticValidator
p=Path(__file__).resolve().parents[1]
schema=json.loads((p/'baseline/P1_1_Contract_Freeze/contract/report.schema.json').read_text())
validator=Draft202012Validator(schema)
instance=SemanticValidator()
cases=json.loads((p/'baseline/P1_1_Contract_Freeze/fixtures/conformance_cases.json').read_text())['cases']
count=0
for c in cases:
    if 'input_text' in c: raw=c['input_text'].encode()
    elif c['id']=='F01':raw=(p/'fixtures/migration.acg').read_bytes()
    elif c['id']=='F02':raw=(p/'fixtures/metaphysics.acg').read_bytes()
    ctx=None
    if c.get('context'):
        ctx=json.loads((p/'fixtures'/('migration.binding-context.json' if 'migration.' in c['context'] else 'metaphysics.binding-context.json')).read_text())
    result=instance.validate_bytes(raw,context=ctx)
    validator.validate(result);count+=1
qp=json.loads((p/'fixtures/semantic/migration.qualifier-profiles.json').read_text())
qpschema=json.loads((p/'QUALIFIER_PROFILES.schema.json').read_text())
Draft202012Validator(qpschema).validate(qp)
context=json.loads((p/'fixtures/semantic/migration-with-method.binding-context.json').read_text())
for n in ('example-qualified.acg','example-method.acg','example-f.acg','example-m.acg'):
    result=instance.validate_bytes((p/'fixtures/semantic'/n).read_bytes(),context=context,qualification_profiles=qp)
    validator.validate(result);count+=1
print('PASS — P1.1 report schema for',count,'end-to-end cases; optional qualifier schema PASS')
