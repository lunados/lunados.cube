#!/usr/bin/env python3
"""Optional second oracle: validate P1.1 contexts against untouched Draft 2020-12 JSON Schema."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
try: import jsonschema
except ImportError:
    print('SKIP jsonschema unavailable (stdlib primary validators still run)');raise SystemExit(0)
schema=json.loads((P/'baseline/P1_1_Contract_Freeze/contract/context.schema.json').read_text())
for n in ('migration','metaphysics'):
    d=json.loads((P/'fixtures'/(n+'.binding-context.json')).read_text())
    jsonschema.Draft202012Validator(schema).validate(d)
    print('PASS context schema:',n)
