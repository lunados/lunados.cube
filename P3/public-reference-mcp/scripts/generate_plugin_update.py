#!/usr/bin/env python3
"""Produce a partial update for the EXISTING lunados-cube plugin after Worker deployment.
No network or account changes; actual plugin update is a separate explicit step.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'plugin-source'

def validate_url(value: str) -> str:
    parsed = urlparse(value)
    if (parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password or
            parsed.query or parsed.fragment or parsed.path != '/mcp' or parsed.port not in (None, 443)):
        raise ValueError('Expected exact https://<public-reference-worker-host>/mcp URL')
    if (parsed.hostname in ('cube.lunados.net', 'aiaeao-cube-g5-gateway.jo-885.workers.dev')):
        raise ValueError('Do not bind to P0 static pages or the protected G5 gateway')
    return value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='Actual URL returned by Wrangler, ending /mcp')
    parser.add_argument('--out', default='lunados-cube-0.2.0-update.zip')
    args = parser.parse_args()
    url = validate_url(args.url)
    out = Path(args.out).resolve()
    paths = ['plugin.json','.codex-plugin/plugin.json','skills/read-cube/SKILL.md']
    mcp = {'$schema':'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
           'mcpServers':{'cube-public-reference':{'type':'streamable-http','url':url}}}
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in paths:
            z.write(SOURCE/path,arcname=path)
        z.writestr('mcp.json', json.dumps(mcp,indent=2,ensure_ascii=False)+'\n')
    print('Created plugin update:',out)
    print('MCP URL:',url)
    print('Plugin identity: lunados-cube; same private plugin, update rather than create')

if __name__=='__main__':main()
