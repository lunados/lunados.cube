#!/usr/bin/env python3
"""Real G5 remote probe through installed Codex Keychain bridge; no secret output.

Run on the Mac, after installing the adapter. It verifies actual upstream
server/discover, tools/list, resources/list and cube_discover_surface.
"""
import pathlib
import runpy
import sys

INSTALLED = pathlib.Path.home()/'.local/share/aiaeao/codex/g5_stdio_bridge.py'
EXPECTED_TOOLS = {
    'cube_get_capabilities', 'cube_prepare_print', 'cube_check_print',
    'cube_render_svg', 'cube_read_reference', 'cube_validate',
    'cube_discover_surface'
}

def require_response(messages, label):
    if len(messages)!=1 or 'result' not in messages[0]:
        error=messages[0].get('error',{}) if messages else {}
        raise RuntimeError(label+': '+str(error.get('message','no MCP result')))
    return messages[0]['result']

def main():
    if not INSTALLED.is_file():
        raise RuntimeError('Bridge not installed: '+str(INSTALLED))
    bridge=runpy.run_path(str(INSTALLED))['Bridge']()
    try:
        # Legacy Host -> bridge local initialize -> actual modern G5 discovery.
        r=require_response(bridge.forward({'jsonrpc':'2.0','id':1,'method':'initialize',
                 'params':{'protocolVersion':'2025-11-25','capabilities':{},
                           'clientInfo':{'name':'codex-g5-probe','version':'1.0'}}}),
                 'INITIALIZE')
        assert r['protocolVersion']=='2025-11-25'
        print('INITIALIZE/DISCOVERY: PASS')
        tools=require_response(bridge.forward({'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}}),'TOOLS')
        names={item['name'] for item in tools['tools']}
        assert names==EXPECTED_TOOLS, 'Tool set differs from expected 7'
        print('TOOLS: PASS (7)')
        refs=require_response(bridge.forward({'jsonrpc':'2.0','id':3,'method':'resources/list','params':{}}),'RESOURCES')
        assert len(refs['resources'])==14, 'Resource count differs from expected 14'
        print('P0 RESOURCES: PASS (14)')
        result=require_response(bridge.forward({'jsonrpc':'2.0','id':4,'method':'tools/call',
            'params':{'name':'cube_discover_surface','arguments':{}}}),'DISCOVER_SURFACE')
        assert result.get('structuredContent',{}).get('deployment',{}).get('remote_mcp_available') is True
        assert result.get('isError') is not True
        print('CUBE DISCOVER SURFACE: PASS (real G5 call)')
        print('PASS: G5 authenticated remote MCP through installed Keychain bridge')
    except Exception as error:
        # Exception messages emitted by bridge intentionally contain no credentials.
        print('BLOCKED:',type(error).__name__,str(error))
        return 1
    return 0

if __name__=='__main__':sys.exit(main())
