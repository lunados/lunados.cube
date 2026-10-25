#!/usr/bin/env python3
"""Minimal transparent stdio -> G5 remote Streamable HTTP bridge.

Credential: macOS Keychain only, never configuration or stdout.
Scope: G5's request-response MCP surface (tools, resources). No subscriptions.
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
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 90

class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('MCP_REDIRECT_REJECTED')

def keychain_token():
    username = pwd.getpwuid(os.getuid()).pw_name
    proc = subprocess.run(
        ['/usr/bin/security', 'find-generic-password', '-a', username,
         '-s', SERVICE, '-w'],
        capture_output=True, text=True, timeout=15,
        check=False)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError('KEYCHAIN_CREDENTIAL_UNAVAILABLE')
    token = proc.stdout.strip()
    if '\n' in token or '\r' in token:
        raise RuntimeError('INVALID_CREDENTIAL')
    return token

def responses(body, content_type):
    if content_type.split(';', 1)[0].strip().lower() == 'text/event-stream':
        # G5 stateless request/response: parse each complete SSE data event.
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
    else:
        if body:
            value = json.loads(body.decode('utf-8'))
            if isinstance(value, list):
                for item in value:
                    yield item
            else:
                yield value

class Bridge:
    def __init__(self, opener=None):
        self.opener = opener if opener is not None else urllib.request.build_opener(NoRedirects())
        self.session_id = None
        self.protocol_version = None

    def forward(self, message):
        if not isinstance(message, dict):
            raise ValueError('JSON_RPC_OBJECT_REQUIRED')
        if message.get('jsonrpc') != '2.0' or 'method' not in message:
            raise ValueError('MCP_MESSAGE_INVALID')
        method = message['method']
        payload = json.dumps(message, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        if len(payload) > MAX_INPUT_BYTES:
            raise ValueError('REQUEST_TOO_LARGE')
        headers = {
            'Authorization': 'Bearer ' + keychain_token(),
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
        }
        if self.session_id is not None:
            headers['Mcp-Session-Id'] = self.session_id
        if self.protocol_version is not None:
            headers['MCP-Protocol-Version'] = self.protocol_version
        req = urllib.request.Request(REMOTE, data=payload, headers=headers, method='POST')
        with self.opener.open(req, timeout=TIMEOUT_SECONDS) as response:
            if response.headers.get('Mcp-Session-Id'):
                self.session_id = response.headers['Mcp-Session-Id']
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError('RESPONSE_TOO_LARGE')
            content_type = response.headers.get('Content-Type', 'application/json')
        if method == 'initialize':
            self.protocol_version = message.get('params', {}).get('protocolVersion')
        return list(responses(raw, content_type))

def error_response(request_id, error_code, detail):
    # No Python exceptions/tracebacks or credentials returned to the MCP client.
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
        except Exception:
            if request_id is not None:
                stdout.write(json.dumps(error_response(request_id, -32000, 'G5_REMOTE_TRANSPORT_UNAVAILABLE')) + '\n')
                stdout.flush()
        # Notifications do not receive responses.

def main():
    if len(sys.argv) > 1:
        raise SystemExit('No arguments accepted; use as an MCP stdio host adapter')
    u = urlsplit(REMOTE)
    if u.scheme != 'https' or u.hostname != 'aiaeao-cube-g5-gateway.jo-885.workers.dev' or u.path != '/mcp':
        raise SystemExit('Remote URL identity invalid')
    process_stream(sys.stdin, sys.stdout, Bridge())

if __name__ == '__main__':
    main()
