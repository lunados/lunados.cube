#!/usr/bin/env python3
"""Diagnosis (MILE-010 TASK-061): run one R5 call against the deployed gateway and save every step's payload.
  python P3/remote-mcp-g5/scripts/r5_dump_call.py P-K07-flow .agent-env/r5_dump_P-K07-flow.json
Needs AIAEAO_G5_URL and AIAEAO_G5_TOKEN as for r5_remote_acceptance.py; the token is never written."""
import asyncio, json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE/'scripts'))
import r5_calls as RC


async def main(cid, out):
    import httpx2
    from mcp import Client
    from mcp.client.streamable_http import streamable_http_client
    url, token = os.environ['AIAEAO_G5_URL'], os.environ['AIAEAO_G5_TOKEN']
    call = next(c for c in RC.calls() if c['id'] == cid)
    async with httpx2.AsyncClient(headers={'Authorization': f'Bearer {token}'}, timeout=httpx2.Timeout(30.0, read=300.0)) as http:
        async with Client(streamable_http_client(url, http_client=http), mode='2026-07-28') as client:
            res, prev = [], None
            for st in call['steps']:
                a = json.loads(json.dumps(st['args']))
                if 'from' in st:
                    v = prev
                    for k in st['from']['path']:
                        v = v[k]
                    a[st['from']['arg']] = v
                r = await client.call_tool(st['op'], a)
                res.append({'op': st['op'], 'is_error': bool(r.is_error), 'payload': r.structured_content})
                if r.is_error:
                    break
                prev = r.structured_content
    Path(out).write_text(json.dumps({'id': cid, 'steps': res}, ensure_ascii=False)+'\n', 'utf-8')
    print('written', out)

asyncio.run(main(sys.argv[1], sys.argv[2]))
