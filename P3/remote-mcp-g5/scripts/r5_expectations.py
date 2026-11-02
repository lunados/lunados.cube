#!/usr/bin/env python3
"""G5 R5 expectations (MILE-010 TASK-059), fixed before any core or gateway code.

Runs every call of r5_calls.py through the LOCAL stdio server functions (G4/G6, P3/adapters/mcp-local) and records per
step: error flag, SHA-256 of the canonical payload, SVG digests and the code. The remote core and the live gateway must
reproduce exactly this (D-4); `cube_validate` results are compared without the remote `transport` field.
Writes P3/remote-mcp-g5/evidence/G5_R5_EXPECTATIONS.json. Run from the lunados.cube root with the adapter venv.
"""
import hashlib, json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE/'scripts')); sys.path.insert(0, str(REPO/'P3/adapters/mcp-local'))
import r5_calls as RC  # noqa: E402
from aiaeao_mcp_local import server, plan_views  # noqa: E402

OUT = HERE/'evidence/G5_R5_EXPECTATIONS.json'
FN = {'cube_plan_source': server.cube_plan_source, 'cube_plan_views': server.cube_plan_views, 'cube_plan_check': server.cube_plan_check,
      'cube_validate': server.cube_validate, 'cube_discover_surface': server.cube_discover_surface}


def invoke(op, args):
    r = FN[op](**args)
    return bool(r.is_error), r.structured_content


def sha(payload):
    return hashlib.sha256(plan_views.canonical(payload)).hexdigest()


def step_facts(op, err, payload):
    f = {'op': op, 'is_error': err, 'payload_sha256': sha(payload)}
    if err:
        f['code'] = payload.get('code')
    elif op == 'cube_plan_views':
        f['svg_sha256'] = [p['sha256'] for p in payload['panels']]
        f['profile'] = payload['profile']
    elif op == 'cube_plan_check':
        f['status'] = payload['status']
    elif op == 'cube_validate':
        f['overall_status'] = payload['report']['overall_status']
        f['codes'] = sorted({d['code'] for d in payload['report']['diagnostics']})
    return f


def main():
    out, slow = [], {}
    for call in RC.calls():
        if call['group'] == 'D':
            continue
        t = time.process_time()
        steps = RC.run_chain(call, invoke)
        cpu = time.process_time()-t
        out.append({'id': call['id'], 'group': call['group'], 'live': call['live'], 'cpu_s_local': round(cpu, 3),
                    'steps': [step_facts(st['op'], e, p) for st, (e, p) in zip(call['steps'], steps)]})
        slow[call['id']] = cpu
    discovery = {  # remote discovery after R5 (Q-6, Q-8); checked by key, the rest of the surface as in 0.7.0-proof
        'release.version': 'P3-MCP-REMOTE/0.8.0-proof', 'remote_adapter.version': 'P3-MCP-REMOTE/0.8.0-proof',
        'p113_control_flow.profile': 'P1.13/control-flow-profile-v1',
        'p113_control_flow.binding_context_formats': ['aiaeao.cube.binding-context/9'],
        'p113_control_flow.false_flags': ['trace_evaluation_by_cube', 'condition_evaluation_by_cube', 'evaluation_performed_by_cube'],
        'domains.P2.plan_views.tools': ['cube_plan_source', 'cube_plan_views', 'cube_plan_check'],
        'domains.P2.plan_views.remote_available': True,
        'domains.P2.plan_views.printers': ['vpmigration', 'vpsequence', 'vpaxes', 'vpcells', 'vpinstances'],
        'unchanged': ['p16_instantiation', 'p18_simulation', 'p19_comparison', 'p110_migration', 'p1101_migration', 'p111_migration_methods',
                      'p112_coverage_instance', 'deployment.remote_status'],
        'gateway_tools': ['cube_get_capabilities', 'cube_prepare_print', 'cube_check_print', 'cube_render_svg', 'cube_read_reference',
                          'cube_validate', 'cube_discover_surface', 'cube_plan_source', 'cube_plan_views', 'cube_plan_check'],
        'gateway_version': '0.2.0-proof'}
    doc = {'format': 'aiaeao.cube.g5-host-expectations/2', 'release': 'P3-MCP-REMOTE/0.8.0-proof',
           'fixed_before': 'core and gateway changes and deployment (TASK-060, TASK-061), 2026-11-02',
           'reference': 'local stdio server functions of P3/adapters/mcp-local (G4/G6); cube_validate compared without transport',
           'calls_source': 'P3/remote-mcp-g5/scripts/r5_calls.py', 'discovery': discovery,
           'counts': {g: sum(1 for c in out if c['group'] == g) for g in ('V', 'P')},
           'host_subset': [c['id'] for c in RC.calls() if c['live'] == 'host'],
           'max_cpu_s_local': round(max(slow.values()), 3), 'calls': out,
           'not_in_scope': ['production approval', 'visual check (outputs byte-identical to the checked local ones, D-8)']}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    errs = [c['id'] for c in out if c['steps'][-1]['is_error']]
    print(len(out), 'calls;', doc['counts'], 'errors expected:', errs, 'max cpu', doc['max_cpu_s_local'])


if __name__ == '__main__':
    main()
