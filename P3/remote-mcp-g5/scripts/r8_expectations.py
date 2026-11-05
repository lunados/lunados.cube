#!/usr/bin/env python3
"""Fix MILE-013 (R8) G5 expectations from the local G4/G6 server before remote code."""
from __future__ import annotations
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE/'scripts'))
sys.path.insert(0, str(REPO/'P3/adapters/mcp-local'))
import r5_calls  # noqa: E402
import r8_calls  # noqa: E402
from aiaeao_mcp_local import server, plan_views  # noqa: E402

OUT = HERE/'evidence/G5_R8_EXPECTATIONS.json'
FN = {'cube_plan_source': server.cube_plan_source, 'cube_plan_views': server.cube_plan_views,
      'cube_plan_check': server.cube_plan_check, 'cube_validate': server.cube_validate}


def invoke(op, args):
    r = FN[op](**args)
    return bool(r.is_error), r.structured_content


def facts(op, error, payload):
    row = {'op': op, 'is_error': error,
           'payload_sha256': hashlib.sha256(plan_views.canonical(payload)).hexdigest()}
    if error:
        row['code'] = payload.get('code')
    elif op == 'cube_validate':
        row['overall_status'] = payload['report']['overall_status']
        row['codes'] = sorted({d['code'] for d in payload['report']['diagnostics']})
    elif op == 'cube_plan_views':
        row['svg_sha256'] = [p['sha256'] for p in payload['panels']]
        row['warnings'] = sorted({w['code'] for w in payload['report']['warnings']})
    elif op == 'cube_plan_check':
        row['status'] = payload['status']
    return row


def main():
    rows = []
    for call in r8_calls.calls():
        if call['group'] == 'D':
            continue
        start = time.process_time()
        steps = r5_calls.run_chain(call, invoke)
        rows.append({'id': call['id'], 'group': call['group'], 'live': call['live'],
                     'cpu_s_local': round(time.process_time()-start, 3),
                     'steps': [facts(st['op'], e, p) for st, (e, p) in zip(call['steps'], steps)]})
    doc = {'format': 'aiaeao.cube.g5-host-expectations/3',
           'release': 'P3-MCP-REMOTE/0.9.1-proof',
           'fixed_before': 'G5 R8 core 0.9.1-proof and its deployment (TASK-074, 2026-11-05)',
           'reference': 'local G4/G6 server functions; cube_validate compared with local transport',
           'calls_source': 'P3/remote-mcp-g5/scripts/r8_calls.py',
           'discovery': {'release.version': 'P3-MCP-REMOTE/0.9.1-proof',
                         'p114_relation_origin.profile': 'P1.14/relation-origin-profile-v1',
                         'p114_relation_origin.binding_context_formats': ['aiaeao.cube.binding-context/10'],
                         'domains.P2.plan_views.printers.vpmigration.profiles': list(plan_views.c07.PROFILES),
                         'domains.P2.plan_views.remote_available': True,
                         'gateway_tools': list(server.surface.TOOLS_G6),
                         'gateway_version': '0.2.0-proof'},
           'host_subset': [c['id'] for c in r8_calls.calls() if c['live'] == 'host'],
           'counts': {'V': sum(c['group'] == 'V' for c in rows), 'P': sum(c['group'] == 'P' for c in rows)},
           'max_cpu_s_local': max(c['cpu_s_local'] for c in rows), 'calls': rows}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print(len(rows), 'calls;', doc['counts'], 'host subset', len(doc['host_subset']),
          'max local CPU', doc['max_cpu_s_local'])


if __name__ == '__main__':
    main()
