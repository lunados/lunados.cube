#!/usr/bin/env python3
"""Small research runner. Real local MCP stdio; no replacement validator."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

CASE_FORMAT = 'aiaeao.cube.research-case/1'
REPORT_FORMAT = 'aiaeao.cube.research-run/1'
DIMENSIONS = ('expression', 'contract_binding', 'implemented_validation', 'visualization', 'utility')
STATUSES = {'PASS', 'FAIL', 'UNRESOLVED'}

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_json(path):
    def invalid_constant(value):
        raise ValueError('Non-finite JSON: ' + value)
    return json.loads(path.read_text(), parse_constant=invalid_constant)

def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

def load_case(path, root):
    case = read_json(path)
    if case.get('format') != CASE_FORMAT or not isinstance(case.get('case_id'), str):
        raise ValueError('Invalid case identity: ' + str(path))
    if case.get('operation') != 'cube_validate' or case.get('invocation_kind') != 'local_mcp_stdio':
        raise ValueError('Only explicit local cube_validate cases are supported')
    args = case.get('arguments')
    if not isinstance(args, dict) or not isinstance(args.get('input_text'), str):
        raise ValueError('Missing input_text')
    if case.get('arguments_sha256') != digest(args):
        raise ValueError('Case arguments digest mismatch')
    bindings = case.get('bindings', {})
    for key in ('context', 'qualification_profiles'):
        if key + '_sha256' not in bindings or bindings[key + '_sha256'] != digest(args.get(key)):
            raise ValueError('Missing or mismatched binding: ' + key)
    if bindings.get('context_format') != (args.get('context') or {}).get('format'):
        raise ValueError('Context format mismatch')
    origin = case.get('origin', {})
    source = (root / origin.get('path', '')).resolve()
    if not source.is_relative_to(root.resolve()) or not source.is_file():
        raise ValueError('Origin must be an existing repository file')
    if not origin.get('reference_version') or file_hash(source) != origin.get('sha256'):
        raise ValueError('Origin version/hash mismatch')
    # v1 fixtures are exact extractions, not transformations of historical input.
    archived = read_json(source)
    matches = [p for p in archived.get('probes', []) if p.get('id') == origin.get('probe_id')]
    if len(matches) != 1 or matches[0]['args'] != args:
        raise ValueError('Fixture is not the declared exact origin extraction')
    expected = case.get('expected', {})
    if expected.get('domain_status') not in STATUSES or not isinstance(expected.get('diagnostic_codes'), list):
        raise ValueError('Expected domain status and diagnostics required before execution')
    if any(not isinstance(c, str) for c in expected['diagnostic_codes']):
        raise ValueError('Invalid expected diagnostic code')
    return case

def interpret(raw):
    """Keep transport/protocol errors separate from a returned domain judgement."""
    if not isinstance(raw, dict) or not isinstance(raw.get('isError'), bool):
        return {'invocation_status': 'MALFORMED_RESPONSE', 'domain_status': None, 'diagnostic_codes': []}
    payload = raw.get('structuredContent')
    if raw['isError']:
        code = payload.get('code') if isinstance(payload, dict) else None
        return {'invocation_status': 'TOOL_ERROR', 'domain_status': None,
                'diagnostic_codes': [code] if isinstance(code, str) else []}
    report = payload.get('report') if isinstance(payload, dict) else None
    if not isinstance(report, dict) or report.get('overall_status') not in STATUSES:
        return {'invocation_status': 'MALFORMED_RESPONSE', 'domain_status': None, 'diagnostic_codes': []}
    diagnostics = report.get('diagnostics')
    if not isinstance(diagnostics, list) or any(not isinstance(d, dict) or not isinstance(d.get('code'), str) for d in diagnostics):
        return {'invocation_status': 'MALFORMED_RESPONSE', 'domain_status': None, 'diagnostic_codes': []}
    return {'invocation_status': 'RETURNED', 'domain_status': report['overall_status'],
            'diagnostic_codes': sorted(d['code'] for d in diagnostics)}

def assess(case, raw):
    result = interpret(raw)
    result['expectation_match'] = (result['invocation_status'] == 'RETURNED'
        and result['domain_status'] == case['expected']['domain_status']
        and result['diagnostic_codes'] == sorted(case['expected']['diagnostic_codes']))
    result['dimensions'] = {d: {'assessment': 'NOT_ASSESSED'} for d in DIMENSIONS}
    if result['invocation_status'] == 'RETURNED':
        result['dimensions']['implemented_validation'] = {
            'assessment': 'OBSERVED', 'domain_status': result['domain_status'],
            'scope': 'Only this declared input and its bound context/profiles; no completeness claim.'}
    return result

def semantic_signature(result):
    return {k: result[k] for k in ('invocation_status', 'domain_status', 'diagnostic_codes', 'expectation_match')}

def source_snapshot(root):
    hashes = {}
    # Include current source/contract bytes, not merely HEAD of an uncommitted worktree.
    for folder in ('AIAEAO_Pure_Cube_P0_v9.4', 'P1', 'P2', 'P3', 'scripts/research'):
        for current, dirs, files in os.walk(root / folder):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules'))
            for name in sorted(files):
                p = Path(current) / name
                if p.suffix in ('.py', '.json', '.lark', '.ebnf', '.yaml', '.toml', '.txt') and not p.is_symlink():
                    hashes[p.relative_to(root).as_posix()] = file_hash(p)
    head = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    return {'git_head': head, 'files': hashes, 'files_sha256': digest(hashes),
            'python': sys.version, 'python_executable': sys.executable,
            'mcp_sdk': importlib.metadata.version('mcp')}

async def execute(root, cases, repeats, timeout, runs):
    from mcp import Client, StdioServerParameters
    from mcp.client.stdio import stdio_client
    server = root / 'P3/adapters/mcp-local/run_server.py'
    params = StdioServerParameters(command=sys.executable, args=['-B', '-u', str(server)])
    # Each repetition deliberately opens a fresh local process/connection.
    for repetition in range(repeats):
        async with asyncio.timeout(timeout):
            async with Client(stdio_client(params), mode='2026-07-28') as client:
                tools = await client.list_tools()
                discovery = await client.call_tool('cube_discover_surface', {})
                legacy = await client.call_tool('cube_get_capabilities', {})
                run = {'run_id': str(uuid.uuid4()), 'at': datetime.now(timezone.utc).isoformat(),
                       'repetition': repetition + 1, 'connection': 'fresh_local_mcp_stdio',
                       'tools': tools.model_dump(mode='json', by_alias=True),
                       'discovery': discovery.model_dump(mode='json', by_alias=True),
                       'legacy': legacy.model_dump(mode='json', by_alias=True), 'cases': []}
                if discovery.is_error or legacy.is_error:
                    raise RuntimeError('Discovery failed; no readiness claim')
                runs.append(run)  # Keep completed responses even if a later invocation fails.
                for case in cases:
                    response = await client.call_tool(case['operation'], case['arguments'])
                    raw = response.model_dump(mode='json', by_alias=True)
                    run['cases'].append({'case_id': case['case_id'], 'arguments_sha256': case['arguments_sha256'],
                                         'raw_response': raw, **assess(case, raw)})
                # Actual malformed configuration, not a simulated domain failure.
                invalid = await client.call_tool('cube_validate', {'input_text': 'Y:α:Artifact', 'context': {}})
                raw = invalid.model_dump(mode='json', by_alias=True)
                run['invalid_configuration_control'] = {'arguments': {'input_text': 'Y:α:Artifact', 'context': {}},
                                                        'raw_response': raw, **interpret(raw)}
    return runs

async def unavailable_control(timeout):
    """Real, controlled attempt to start a nonexistent executable; no service mutation."""
    from mcp import Client, StdioServerParameters
    from mcp.client.stdio import stdio_client
    missing = str(Path('/private/tmp') / ('cube-unavailable-' + uuid.uuid4().hex))
    try:
        async with asyncio.timeout(timeout):
            async with Client(stdio_client(StdioServerParameters(command=missing, args=[])), mode='2026-07-28'):
                pass
    except Exception as exc:
        return {'control': 'deliberately_nonexistent_executable', 'simulated_domain_response': False,
                'invocation_status': 'UNAVAILABLE', 'domain_status': None,
                'exception_type': type(exc).__name__, 'exception_message': str(exc), 'command': missing}
    raise RuntimeError('Unavailability control unexpectedly connected')

def argument_differences(before, after, pointer=''):
    """JSON Pointer differences, preserving absence versus explicit null."""
    if isinstance(before, dict) and isinstance(after, dict):
        changes = []
        for key in sorted(before.keys() | after.keys()):
            path = pointer + '/' + key.replace('~', '~0').replace('/', '~1')
            if key in before and key in after:
                changes.extend(argument_differences(before[key], after[key], path))
            else:
                change = {'pointer': path, 'before_present': key in before, 'after_present': key in after}
                if key in before:
                    change['before'] = before[key]
                if key in after:
                    change['after'] = after[key]
                changes.append(change)
        return changes
    if canonical(before) == canonical(after):
        return []
    return [{'pointer': pointer, 'before_present': True, 'after_present': True,
             'before': before, 'after': after}]

def compare_cases(report, baseline_id, variant_id):
    if baseline_id == variant_id:
        raise ValueError('Comparison needs two distinct case identities')
    cases = {case['case_id']: case for case in report['cases']}
    if baseline_id not in cases or variant_id not in cases:
        raise ValueError('Unknown comparison case')
    baseline, variant = cases[baseline_id], cases[variant_id]
    observations = []
    for run in report['runs']:
        results = {result['case_id']: result for result in run['cases']}
        observations.append({'run_id': run['run_id'],
                             'baseline': semantic_signature(results[baseline_id]),
                             'variant': semantic_signature(results[variant_id])})
    return {'baseline_case_id': baseline_id, 'variant_case_id': variant_id,
            'baseline_arguments_sha256': baseline['arguments_sha256'],
            'variant_arguments_sha256': variant['arguments_sha256'],
            'argument_changes': argument_differences(baseline['arguments'], variant['arguments']),
            'observations': observations,
            'scope': 'Declared inputs and observed validation only; no new semantic, visual or utility proof.'}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--cases', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing results are never overwritten')
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--compare', nargs=2, metavar=('BASELINE_ID', 'VARIANT_ID'))
    opts = parser.parse_args(argv)
    root = opts.repo.resolve()
    cases_dir = opts.cases or root / 'docs/09-Research/analysis-readiness/cases'
    if opts.repeats < 2 or opts.timeout <= 0:
        parser.error('At least two repeats and a positive timeout required')
    paths = sorted(cases_dir.glob('*.json'))
    if not paths:
        parser.error('No case fixtures found')
    cases = [load_case(p, root) for p in paths]
    if len({c['case_id'] for c in cases}) != len(cases):
        parser.error('Duplicate case IDs')
    if opts.compare and (opts.compare[0] == opts.compare[1] or any(i not in {c['case_id'] for c in cases} for i in opts.compare)):
        parser.error('Comparison requires two distinct known case IDs')
    opts.output.mkdir(parents=True, exist_ok=False)
    snapshot = source_snapshot(root)
    report = {'format': REPORT_FORMAT, 'invocation_kind': 'local_mcp_stdio', 'snapshot': snapshot,
              'cases': cases, 'case_file_hashes': {p.name: file_hash(p) for p in paths}, 'runs': []}
    try:
        asyncio.run(execute(root, cases, opts.repeats, opts.timeout, report['runs']))
        report['unavailable_control'] = asyncio.run(unavailable_control(opts.timeout))
    except Exception as exc:
        report['invocation_failure'] = {'type': type(exc).__name__, 'message': str(exc), 'domain_status': None}
        report['readiness_checks_passed'] = False
        write_json(opts.output / 'report.json', report)
        print('Invocation failed; no domain judgement inferred. See', opts.output / 'report.json')
        return 2
    first = [semantic_signature(c) for c in report['runs'][0]['cases']]
    report['repeats_semantically_equal'] = all([semantic_signature(c) for c in run['cases']] == first for run in report['runs'])
    report['source_unchanged_during_run'] = source_snapshot(root)['files_sha256'] == snapshot['files_sha256']
    report['readiness_checks_passed'] = (report['repeats_semantically_equal'] and report['source_unchanged_during_run']
        and all(c['expectation_match'] for run in report['runs'] for c in run['cases'])
        and all(run['invalid_configuration_control']['invocation_status'] == 'TOOL_ERROR'
                and run['invalid_configuration_control']['diagnostic_codes'] == ['P1_MCP_CONFIG_INVALID'] for run in report['runs']))
    if opts.compare:
        report['comparison'] = compare_cases(report, *opts.compare)
    write_json(opts.output / 'report.json', report)
    print(('PASS' if report['readiness_checks_passed'] else 'FAIL'), len(cases), 'cases x', opts.repeats,
          'fresh local connections; result:', opts.output / 'report.json')
    return 0 if report['readiness_checks_passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
