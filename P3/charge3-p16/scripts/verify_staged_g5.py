#!/usr/bin/env python3
"""Run in fresh Python process; confirms P1.6 is loaded from actual G5 staging."""
import json, sys, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
REPO=HERE.parents[1]
RT=REPO/'P3/remote-mcp-g5/.g5-runtime'
assert RT.is_dir(), 'First run G5 assemble_core.py'
sys.path.insert(0,str(RT))
from core_runtime import dispatch
from aiaeao_mcp_local import p1_adapter
assert Path(p1_adapter.__file__).resolve().is_relative_to(RT.resolve()), p1_adapter.__file__
# /2 is lazily imported by p1_adapter, so first exercise one /2 call below.
assets=json.loads((RT/'G5_SOURCE_MANIFEST.json').read_text())['files']
vocab='P1/instantiation-profile-v1/instantiation_reference_v1.json'
assert any(x['path']==vocab and x['sha256']==hashlib.sha256((RT/vocab).read_bytes()).hexdigest() for x in assets)
cases=json.loads((HERE/'fixtures/r01_r13_materialized.json').read_text('utf-8'))['cases']
assert len(cases)==13
warm=dispatch('cube_validate',{'input_text':cases[0]['input_text'],'context':cases[0]['context']})
assert warm['ok'],warm
import cube_p16.validator as p16
assert Path(p16.__file__).resolve().is_relative_to(RT.resolve()), p16.__file__
for v in cases:
    reply=dispatch('cube_validate',{'input_text':v['input_text'],'context':v['context']})
    assert reply['ok'],(v['id'],reply)
    content=reply['result']
    assert content['report']['overall_status']==v['expected_overall'],(v['id'],content['report'])
    assert content['transport']=='remote_mcp_streamable_http'
    assert set(v['required_codes']).issubset({d['code'] for d in content['report']['diagnostics']}),v['id']
    for key in ('epistemic_warrant','current_authority','canonical_admission'):
        assert content['report'][key]=='NOT_EVALUATED',v['id']
    if v['context']['format'].endswith('/1'):
        assert 'binding_context_profile' not in content,v['id']
    else:
        assert content['binding_context_profile']=='P1.6/instantiation-profile-v1',v['id']
invalid=cases[0]['context'].copy();invalid['format']='aiaeao.cube.binding-context/3'
reply=dispatch('cube_validate',{'input_text':cases[0]['input_text'],'context':invalid})
assert not reply['ok'] and reply['diagnostic']['code']=='P1_MCP_CONFIG_INVALID'
assert len(dispatch('cube_discover_surface')['result']['mcp']['tools'])==7
print('PASS CHARGE 3 staged G5: P1.6 module and vocabulary inside isolated assembly; R-01..R-13; 7 tools, v1 parity boundary')
