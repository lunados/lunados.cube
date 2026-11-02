#!/usr/bin/env python3
"""G5 R5 scripted live acceptance (MILE-010 TASK-061, CL-3): run ALL R5 calls against the deployed gateway.

Run after deploying core and gateway, from the lunados.cube root, in the G4 MCP SDK venv:
  export AIAEAO_G5_URL='https://<deployed-gateway>.workers.dev/mcp'
  export AIAEAO_G5_TOKEN='<local secret, do not commit or share>'
  python P3/remote-mcp-g5/scripts/r5_remote_acceptance.py --evidence P3/remote-mcp-g5/evidence/G5_R5_LIVE_SCRIPT.json

Every step is compared with evidence/G5_R5_EXPECTATIONS.json (error flag, payload SHA-256, SVG digests, codes;
cube_validate with transport set to the local value, CL-2). P-K12 asks for an unknown view: the gateway schema rejects it
before the core (the local stdio SDK does the same with its Literal type), so that step expects a schema rejection.
Wall time per call is recorded (RM-2). No token is printed or written; no files except the optional evidence JSON.
"""
import argparse, asyncio, datetime, hashlib, json, os, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REPO = HERE.parents[1]
sys.path.insert(0, str(HERE/'scripts'))
import r5_calls as RC  # noqa: E402

SCHEMA_REJECTED = {('P-K12-view-unknown', 1)}
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')  # noqa: E731


def get(d, dotted):
    for k in dotted.split('.'):
        d = d[k]
    return d


def discovery_ok(surface, d):
    checks = {k: get(surface, k) == v for k, v in d.items() if k not in ('unchanged', 'gateway_tools', 'gateway_version')
              and not k.endswith('false_flags') and not k.endswith('printers')}
    checks['p113_control_flow.false_flags'] = all(surface['p113_control_flow'][f] is False for f in d['p113_control_flow.false_flags'])
    checks['domains.P2.plan_views.printers'] = sorted(surface['domains']['P2']['plan_views']['printers']) == sorted(d['domains.P2.plan_views.printers'])
    return checks


async def main(args):
    url, token = os.environ.get('AIAEAO_G5_URL', ''), os.environ.get('AIAEAO_G5_TOKEN', '')
    if not url.startswith('https://') and not url.startswith('http://127.0.0.1:'):
        raise SystemExit('Set AIAEAO_G5_URL to an HTTPS endpoint (or local 127.0.0.1)')
    if len(token) < 32:
        raise SystemExit('Set AIAEAO_G5_TOKEN (32+ characters)')
    try:
        import httpx2
        from mcp import Client
        from mcp.client.streamable_http import streamable_http_client
    except ImportError:
        raise SystemExit('Install official mcp SDK v2 and httpx2 in isolated venv')
    exp = json.loads((HERE/'evidence/G5_R5_EXPECTATIONS.json').read_text('utf-8'))
    want = {c['id']: c for c in exp['calls']}
    rows, bad = [], []
    async with httpx2.AsyncClient(headers={'Authorization': f'Bearer {token}'}, timeout=httpx2.Timeout(30.0, read=300.0)) as http:
        async with Client(streamable_http_client(url, http_client=http), mode='2026-07-28') as client:
            names = [t.name for t in (await client.list_tools()).tools]
            tools_ok = names == exp['discovery']['gateway_tools']
            health = (await http.get(url.rsplit('/mcp', 1)[0]+'/health')).json()
            health_ok = health.get('version') == exp['discovery']['gateway_version']
            for call in RC.calls():
                cache = {}

                async def invoke(op, a, _cid=call['id']):
                    t = time.perf_counter()
                    r = await client.call_tool(op, a)
                    cache.setdefault('wall', []).append(round(time.perf_counter()-t, 3))
                    p = r.structured_content
                    if p is not None and not r.is_error and op == 'cube_validate':
                        p = dict(p); p['transport'] = 'local_mcp_stdio'
                    return bool(r.is_error), p
                steps, prev = [], None
                for i, st in enumerate(call['steps']):
                    a = json.loads(json.dumps(st['args']))
                    if 'from' in st:
                        v = prev
                        for k in st['from']['path']:
                            v = v[k]
                        a[st['from']['arg']] = v
                    e, p = await invoke(st['op'], a)
                    steps.append((e, p))
                    if e:
                        break
                    prev = p
                if call['id'] == 'D-01':
                    checks = discovery_ok(steps[0][1], exp['discovery'])
                    ok = all(checks.values())
                    rows.append({'id': 'D-01', 'match': ok, 'checks': checks, 'wall_s': cache['wall']})
                else:
                    w, ok, got = want[call['id']], True, []
                    if len(steps) != len(w['steps']):
                        ok = False
                    for i, ((e, p), x) in enumerate(zip(steps, w['steps'])):
                        if (call['id'], i) in SCHEMA_REJECTED:
                            ok = ok and e and (p is None or p.get('code') in (None, x.get('code')))
                            continue
                        f = {'is_error': e, 'payload_sha256': hashlib.sha256(canon(p)).hexdigest() if p is not None else None}
                        if not e and call['steps'][i]['op'] == 'cube_plan_views':
                            f['svg_sha256'] = [q['sha256'] for q in p['panels']]
                        same = f['is_error'] == x['is_error'] and f['payload_sha256'] == x['payload_sha256'] and f.get('svg_sha256') == x.get('svg_sha256')
                        got.append({'op': call['steps'][i]['op'], 'match': same, **({} if same else f)})
                        ok = ok and same
                    rows.append({'id': call['id'], 'match': ok, 'wall_s': cache['wall'], 'host_subset': call['live'] == 'host',
                                 **({} if ok else {'steps': got})})
                    if not ok and args.dump_dir:            # diagnosis: the remote payloads of a mismatching chain (no token)
                        Path(args.dump_dir).mkdir(parents=True, exist_ok=True)
                        (Path(args.dump_dir)/f"r5_mismatch_{call['id']}.json").write_text(
                            json.dumps([{'is_error': e, 'payload': p} for e, p in steps], ensure_ascii=False)+'\n', 'utf-8')
                if not rows[-1]['match']:
                    bad.append(call['id'])
                print('PASS' if rows[-1]['match'] else 'FAIL', call['id'], rows[-1]['wall_s'], flush=True)
    walls = sorted(((max(r['wall_s']), r['id']) for r in rows), reverse=True)
    ev = {'format': 'aiaeao.cube.g5-r5-live-script/1', 'date': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'release': exp['release'], 'gateway_tools_as_expected': tools_ok, 'gateway_health_version_as_expected': health_ok,
          'calls': len(rows), 'matched': sum(r['match'] for r in rows), 'mismatched': bad,
          'wall_s_top5': [{'id': i, 'wall_s': s} for s, i in walls[:5]], 'rows': rows,
          'status': 'PASS' if not bad and tools_ok and health_ok else 'FAIL'}
    print(f"{ev['status']} G5 R5 LIVE: {ev['matched']}/{ev['calls']} as expected; tools {tools_ok}; health {health_ok}; slowest {walls[0] if walls else None}")
    if args.evidence:
        dest = Path(args.evidence); dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=1)+'\n', 'utf-8')
        print('evidence written to:', dest)
    sys.exit(0 if ev['status'] == 'PASS' else 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--evidence', help='write the sanitized JSON report (no token)')
    p.add_argument('--dump-dir', help='on a mismatch, save the remote payloads of that chain here (diagnosis)')
    asyncio.run(main(p.parse_args()))
