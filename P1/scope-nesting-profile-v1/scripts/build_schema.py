#!/usr/bin/env python3
"""Build context-v11.schema.json: the strict /10 schema plus scope_nesting (SN-1)."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
s = json.loads((HERE.parent / 'relation-origin-profile-v1/context-v10.schema.json').read_text('utf-8'))
s["$id"] = "urn:aiaeao:cube:p1:binding-context:11"
s["title"] = 'AIAEAO Cube binding context /11 (P1.15 scope nesting and admission outcomes)'
s['properties']['format'] = {'const': 'aiaeao.cube.binding-context/11'}
s['properties']['scope_nesting'] = {
    'type': 'array', 'maxItems': 512,
    'description': 'P1.15 SN-1: declared X scope chains (inner → outer), ending in the context scope_ref; structural only',
    'items': {'type': 'object', 'additionalProperties': False, 'required': ['inner', 'outer'],
              'properties': {'inner': {'type': 'string', 'minLength': 1, 'maxLength': 512},
                             'outer': {'type': 'string', 'minLength': 1, 'maxLength': 512}}}}
(HERE / 'context-v11.schema.json').write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n', 'utf-8')
print('ok')
