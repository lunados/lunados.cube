#!/usr/bin/env python3
"""Codex stdio (legacy/modern MCP) -> modern G5 Streamable HTTP adapter.

No P0/P1/P2 logic here; all capabilities and data come from G5.
The upstream only speaks MCP 2026-07-28 (no 'initialize' on the wire).
The local Codex host may speak 2025-era MCP (initialize/initialized).
Credential is read from macOS Keychain and never logged or persisted.
"""
import json
import os
import pwd
import subprocess
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit

REMOTE = 'https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp'
SERVICE = 'aiaeao-g5-mcp-token'
UPSTREAM_VERSION = '2026-07-28'
LEGACY_VERSIONS = {'2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05'}
DEFAULT_LOCAL_VERSION = '2025-11-25'
BRIDGE_NAME = 'aiaeao-cube-codex-bridge'
BRIDGE_VERSION = '0.2.0'
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 90

class BridgeFailure(Exception):
    """Error code intentionally omits credentials, URLs, request bodies and responses."""

class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise BridgeFailure('MCP_REDIRECT_REJECTED')

def keychain_token():
    username = pwd.getpwuid(os.getuid()).pw_name
    proc = subprocess.run(
        ['/usr/bin/security', 'find-generic-password', '-a', username,
         '-s', SERVICE, '-w'],
        capture_output=True, text=True, timeout=15, check=False)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise BridgeFailure('KEYCHAIN_CREDENTIAL_UNAVAILABLE')
    token = proc.stdout.strip()
    if '\n' in token or '\r' in token:
        raise BridgeFailure('INVALID_CREDENTIAL')
    return token

def responses(body, content_type):
    if content_type.split(';', 1)[0].strip().lower() == 'text/event-stream':
        data_lines = []
        for line in body.decode('utf-8').splitlines():
            if line == '':
                if data_lines:
                    yield json.loads('\n'.join(data_lines))
                    data_lines = []
            elif line.startswith('data:'):
                data_lines.append(line[5:].lstrip(' '))
        if data_lines:
            yield json.loads('\n'.join(data_lines))
    elif body:
        value = json.loads(body.decode('utf-8'))
        if isinstance(value, list):
            yield from value
        else:
            yield value

def modernize(message):
    """Copy legacy/modern host request to fresh 2026-07-28 upstream envelope."""
    if not isinstance(message, dict) or message.get('jsonrpc') != '2.0':
        raise ValueError('MCP_MESSAGE_INVALID')
    method = message.get('method')
    if not isinstance(method, str):
        raise ValueError('MCP_METHOD_INVALID')
    request = dict(message)
    params = dict(request.get('params') or {})
    meta = dict(params.get('_meta') or {})
    # Preserve other host metadata while asserting the upstream wire version.
    meta['io.modelcontextprotocol/protocolVersion'] = UPSTREAM_VERSION
    meta.setdefault('io.modelcontextprotocol/clientInfo',
                    {'name': BRIDGE_NAME, 'version': BRIDGE_VERSION})
    meta.setdefault('io.modelcontextprotocol/clientCapabilities', {})
    params['_meta'] = meta
    request['params'] = params
    return request

def mirrored_name(message):
    method = message['method']
    params = message.get('params', {})
    if method in ('tools/call', 'prompts/get'):
        return params.get('name')
    if method == 'resources/read':
        return params.get('uri')
    return None

class Bridge:
    def __init__(self, opener=None):
        self.opener = opener if opener is not None else urllib.request.build_opener(NoRedirects())
        self.host_protocol_version = None

    def _upstream(self, message):
        modern = modernize(message)
        payload = json.dumps(modern, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        if len(payload) > MAX_INPUT_BYTES:
            raise ValueError('REQUEST_TOO_LARGE')
        headers = {
            'Authorization': 'Bearer ' + keychain_token(),
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'User-Agent': 'Lunados-Cube-Codex-Bridge/0.1',
            'MCP-Protocol-Version': UPSTREAM_VERSION,
            'Mcp-Method': modern['method'],
        }
        name = mirrored_name(modern)
        if name is not None:
            if not isinstance(name, str) or not name.isascii():
                raise ValueError('MCP_NAME_HEADER_UNSUPPORTED')
            headers['Mcp-Name'] = name
        req = urllib.request.Request(REMOTE, data=payload, headers=headers, method='POST')
        try:
            with self.opener.open(req, timeout=TIMEOUT_SECONDS) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise BridgeFailure('G5_RESPONSE_TOO_LARGE')
                content_type = response.headers.get('Content-Type', 'application/json')
        except urllib.error.HTTPError as e:
            # Preserve only structured MCP diagnostics; never leak arbitrary error pages.
            raw = e.read(MAX_RESPONSE_BYTES + 1)
            typ = e.headers.get('Content-Type', '') if e.headers else ''
            if len(raw) <= MAX_RESPONSE_BYTES and 'application/json' in typ:
                try:
                    parsed = list(responses(raw, typ))
                    if parsed and all(isinstance(item, dict) and
                                      isinstance(item.get('error'), dict) and
                                      isinstance(item['error'].get('code'), int)
                                      for item in parsed):
                        return parsed
                except (ValueError, UnicodeError):
                    pass
            raise BridgeFailure('G5_UPSTREAM_HTTP_' + str(e.code)) from None
        return list(responses(raw, content_type))

    def forward(self, message):
        if not isinstance(message, dict) or message.get('jsonrpc') != '2.0':
            raise ValueError('MCP_MESSAGE_INVALID')
        method = message.get('method')
        if not isinstance(method, str):
            raise ValueError('MCP_METHOD_INVALID')
        # Legacy handshake is local only: the G5 gateway is modern-only.
        if method == 'initialize':
            return [self._legacy_initialize(message)]
        if method == 'notifications/initialized':
            return []
        # Other operations (including modern server/discover) use actual G5 RPC.
        return self._upstream(message)

    def _legacy_initialize(self, message):
        if 'id' not in message:
            raise ValueError('INITIALIZE_ID_REQUIRED')
        requested = (message.get('params') or {}).get('protocolVersion')
        # The host expects an initialize-style 2025 session. Never advertise
        # modern 2026 semantics on a legacy initialize exchange.
        chosen = requested if requested in LEGACY_VERSIONS else DEFAULT_LOCAL_VERSION
        result = self._upstream({'jsonrpc': '2.0', 'id': message['id'],
                                 'method': 'server/discover', 'params': {}})
        if len(result) != 1 or not isinstance(result[0].get('result'), dict):
            if result and isinstance(result[0].get('error'), dict):
                return result[0]
            raise BridgeFailure('G5_DISCOVERY_UNAVAILABLE')
        data = result[0]['result']
        if UPSTREAM_VERSION not in data.get('supportedVersions', []):
            raise BridgeFailure('G5_PROTOCOL_INCOMPATIBLE')
        info = (data.get('_meta') or {}).get('io.modelcontextprotocol/serverInfo')
        if not isinstance(info, dict):
            info = {'name': 'aiaeao-cube-mcp-remote-g5', 'version': '0.1.0-proof'}
        capabilities = data.get('capabilities', {})
        if not isinstance(capabilities, dict):
            raise BridgeFailure('G5_CAPABILITIES_INVALID')
        local_result = {
            'protocolVersion': chosen,
            'capabilities': capabilities,
            'serverInfo': info,
        }
        if isinstance(data.get('instructions'), str):
            local_result['instructions'] = data['instructions']
        self.host_protocol_version = chosen
        return {'jsonrpc': '2.0', 'id': message['id'], 'result': local_result}

def error_response(request_id, error_code, detail):
    return {'jsonrpc': '2.0', 'id': request_id,
            'error': {'code': error_code, 'message': detail}}

def process_stream(stdin, stdout, bridge):
    while True:
        raw = stdin.buffer.readline(MAX_INPUT_BYTES + 2)
        if not raw:
            break
        request_id = None
        try:
            if len(raw) > MAX_INPUT_BYTES + 1:
                raise ValueError('REQUEST_TOO_LARGE')
            msg = json.loads(raw.decode('utf-8'))
            if isinstance(msg, dict):
                request_id = msg.get('id')
            items = bridge.forward(msg)
            for item in items:
                stdout.write(json.dumps(item, ensure_ascii=False, separators=(',', ':')) + '\n')
                stdout.flush()
        except (ValueError, json.JSONDecodeError):
            if request_id is not None:
                stdout.write(json.dumps(error_response(request_id, -32600, 'INVALID_MCP_REQUEST')) + '\n')
                stdout.flush()
        except BridgeFailure as e:
            if request_id is not None:
                stdout.write(json.dumps(error_response(request_id, -32000, str(e))) + '\n')
                stdout.flush()
        except Exception:
            if request_id is not None:
                stdout.write(json.dumps(error_response(request_id, -32000, 'G5_REMOTE_TRANSPORT_UNAVAILABLE')) + '\n')
                stdout.flush()
        # Notifications receive no response.

def main():
    if len(sys.argv) > 1:
        raise SystemExit('No arguments accepted; use as an MCP stdio host adapter')
    u = urlsplit(REMOTE)
    if u.scheme != 'https' or u.hostname != 'aiaeao-cube-g5-gateway.jo-885.workers.dev' or u.path != '/mcp':
        raise SystemExit('Remote URL identity invalid')
    process_stream(sys.stdin, sys.stdout, Bridge())

if __name__ == '__main__':
    main()
