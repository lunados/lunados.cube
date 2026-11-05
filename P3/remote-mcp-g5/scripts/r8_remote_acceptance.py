#!/usr/bin/env python3
"""MILE-013 (R8) scripted G5 live check against the fixed local expectations (R6 calls, R5 heavy calls, VP-07.7).

Requires AIAEAO_G5_URL and AIAEAO_G5_TOKEN from a secure local source, plus the
G4 MCP SDK venv. Evidence contains digests and codes, never tokens or payloads.
"""
from __future__ import annotations
import argparse
import asyncio
import datetime
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE/'scripts'))
import r8_calls  # noqa: E402

canon = lambda obj: json.dumps(obj, sort_keys=True, ensure_ascii=False,
                               separators=(',', ':'), allow_nan=False).encode('utf-8')  # noqa: E731


def _get(obj, path):
    for key in path.split('.'):
        obj = obj[key]
    return obj


def _discovery(surface, expected):
    return {path: _get(surface, path) == value for path, value in expected.items()
            if path not in ('gateway_tools', 'gateway_version')}


def _step(op, error, payload):
    item = {'op': op, 'is_error': error,
            'payload_sha256': hashlib.sha256(canon(payload)).hexdigest() if payload is not None else None}
    if error and isinstance(payload, dict):
        item['code'] = payload.get('code')
    if not error and op == 'cube_plan_views':
        item['svg_sha256'] = [p['sha256'] for p in payload['panels']]
    return item


async def main(args):
    url, token = os.environ.get('AIAEAO_G5_URL', ''), os.environ.get('AIAEAO_G5_TOKEN', '')
    if not url.startswith('https://') and not url.startswith('http://127.0.0.1:'):
        raise SystemExit('Set AIAEAO_G5_URL to HTTPS /mcp (or local 127.0.0.1)')
    if len(token) < 32:
        raise SystemExit('Set AIAEAO_G5_TOKEN (32+ characters)')
    try:
        import httpx2
        from mcp import Client
        from mcp.client.streamable_http import streamable_http_client
    except ImportError:
        raise SystemExit('Install official MCP SDK v2 and httpx2 in the G4 venv')
    expected = json.loads((HERE/'evidence/G5_R8_EXPECTATIONS.json').read_text('utf-8'))
    want = {c['id']: c for c in expected['calls']}
    rows = []
    async with httpx2.AsyncClient(headers={'Authorization': f'Bearer {token}'},
                                  timeout=httpx2.Timeout(30.0, read=300.0)) as http:
        async with Client(streamable_http_client(url, http_client=http), mode='2026-07-28') as client:
            names = [tool.name for tool in (await client.list_tools()).tools]
            tools_ok = names == expected['discovery']['gateway_tools']
            health = (await http.get(url.rsplit('/mcp', 1)[0]+'/health')).json()
            health_ok = health.get('version') == expected['discovery']['gateway_version']
            for call in r8_calls.calls():
                previous, steps, walls = None, [], []
                for st in call['steps']:
                    wire = json.loads(json.dumps(st['args']))
                    if 'from' in st:
                        value = previous
                        for key in st['from']['path']:
                            value = value[key]
                        wire[st['from']['arg']] = value
                    start = time.perf_counter()
                    response = await client.call_tool(st['op'], wire)
                    walls.append(round(time.perf_counter()-start, 3))
                    payload = response.structured_content
                    error = bool(response.is_error)
                    if payload is not None and not error and st['op'] == 'cube_validate':
                        payload = dict(payload); payload['transport'] = 'local_mcp_stdio'
                    steps.append(_step(st['op'], error, payload))
                    if error:
                        break
                    previous = payload
                if call['id'] == 'D-01':
                    checks = _discovery(previous, expected['discovery']) if previous else {'response': False}
                    match = all(checks.values())
                    row = {'id': call['id'], 'match': match, 'checks': checks, 'wall_s': walls,
                           'host_subset': True}
                else:
                    ref = want[call['id']]['steps']
                    comparisons = [all(g.get(k) == x.get(k) for k in ('op', 'is_error', 'payload_sha256',
                                                                      'code', 'svg_sha256'))
                                   for g, x in zip(steps, ref)]
                    match = len(steps) == len(ref) and all(comparisons)
                    row = {'id': call['id'], 'match': match, 'wall_s': walls,
                           'host_subset': call['live'] == 'host'}
                    if not match:
                        row['steps'] = [{**g, 'match': comparisons[i]} for i, g in enumerate(steps)]
                rows.append(row)
                print('PASS' if match else 'FAIL', call['id'], walls, flush=True)
    mismatched = [r['id'] for r in rows if not r['match']]
    report = {'format': 'aiaeao.cube.g5-r8-live-script/1',
              'date': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'release': expected['release'], 'gateway_tools_as_expected': tools_ok,
              'gateway_health_version_as_expected': health_ok,
              'calls': len(rows), 'matched': sum(r['match'] for r in rows),
              'mismatched': mismatched,
              'wall_s_top5': sorted(({'id': r['id'], 'wall_s': max(r['wall_s'])} for r in rows),
                                    key=lambda r: r['wall_s'], reverse=True)[:5],
              'rows': rows, 'status': 'PASS' if not mismatched and tools_ok and health_ok else 'FAIL'}
    dest = Path(args.evidence)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=1)+'\n', 'utf-8')
    print(f"{report['status']} G5 R8 LIVE: {report['matched']}/{report['calls']}; "
          f"tools {tools_ok}; health {health_ok}; evidence {dest}")
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', default=str(HERE/'evidence/G5_R8_LIVE_SCRIPT.json'))
    raise SystemExit(asyncio.run(main(parser.parse_args())))
