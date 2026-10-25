import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
import urllib.error
from email.message import Message
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]/'scripts'

def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
b=load('g5_stdio_bridge');i=load('install_codex_g5')

TOOLS = ['cube_get_capabilities', 'cube_prepare_print', 'cube_check_print',
         'cube_render_svg', 'cube_read_reference', 'cube_validate', 'cube_discover_surface']

class FakeHttp:
    def __init__(self,body,typ='application/json'):
        self.body=body;self.headers=Message();self.headers['Content-Type']=typ
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,max_bytes):return self.body[:max_bytes]

class FakeOpener:
    def __init__(self):self.requests=[]
    def open(self,req,timeout):
        self.requests.append(req)
        payload=json.loads(req.data)
        method=payload['method']
        if method=='server/discover':
            result={'resultType':'complete','supportedVersions':[b.UPSTREAM_VERSION],
                    'capabilities':{'tools':{},'resources':{}},
                    '_meta':{'io.modelcontextprotocol/serverInfo':{'name':'G5','version':'0.1.0-proof'}}}
        elif method=='tools/list':
            result={'resultType':'complete','tools':[{'name':n} for n in TOOLS]}
        elif method=='resources/list':
            result={'resultType':'complete','resources':[{'uri':f'aiaeao://p0/{k}'} for k in range(14)]}
        elif method=='tools/call':
            result={'resultType':'complete','content':[],
                    'structuredContent':{'deployment':{'remote_mcp_available':True}}}
        else:
            result={'resultType':'complete','ok':True}
        return FakeHttp(json.dumps({'jsonrpc':'2.0','id':payload.get('id'), 'result':result}).encode())

def header(req,name):
    return dict((k.lower(),v) for k,v in req.header_items()).get(name.lower())

class Tests(unittest.TestCase):
    def test_expected_url(self):
        self.assertEqual(b.REMOTE,'https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp')

    def test_legacy_initialize_is_locally_translated_using_live_discovery(self):
        op=FakeOpener();bridge=b.Bridge(opener=op)
        msg={'jsonrpc':'2.0','id':1,'method':'initialize',
             'params':{'protocolVersion':'2025-11-25','capabilities':{},
                       'clientInfo':{'name':'codex','version':'1'}}}
        with patch.object(b,'keychain_token',return_value='SECRET-NOT-TO-LOG'):
            response=bridge.forward(msg)[0]
        self.assertEqual(response['result']['protocolVersion'],'2025-11-25')
        self.assertEqual(response['result']['serverInfo']['name'],'G5')
        self.assertIn('tools',response['result']['capabilities'])
        self.assertEqual(json.loads(op.requests[0].data)['method'],'server/discover')
        self.assertEqual(header(op.requests[0],'Mcp-Protocol-Version'),b.UPSTREAM_VERSION)
        self.assertEqual(header(op.requests[0],'Mcp-Method'),'server/discover')
        self.assertNotIn('SECRET-NOT-TO-LOG',json.dumps(response))
        self.assertEqual(bridge.forward({'jsonrpc':'2.0','method':'notifications/initialized'}),[])
        self.assertEqual(len(op.requests),1)

    def test_obsolete_initialize_with_2026_is_not_forwarded(self):
        op=FakeOpener();bridge=b.Bridge(opener=op)
        with patch.object(b,'keychain_token',return_value='TOKEN'):
            msg={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2026-07-28'}}
            result=bridge.forward(msg)[0]
        self.assertEqual(result['result']['protocolVersion'],'2025-11-25')
        self.assertEqual(json.loads(op.requests[0].data)['method'],'server/discover')

    def test_modern_metadata_and_mirror_headers(self):
        op=FakeOpener();bridge=b.Bridge(opener=op)
        with patch.object(b,'keychain_token',return_value='SENSITIVE'):
            response=bridge.forward({'jsonrpc':'2.0','id':2,'method':'tools/call',
                                     'params':{'name':'cube_discover_surface','arguments':{}}})
        self.assertTrue(response[0]['result']['structuredContent']['deployment']['remote_mcp_available'])
        req=op.requests[0]
        self.assertEqual(header(req,'Authorization'),'Bearer SENSITIVE')
        self.assertEqual(header(req,'Mcp-Protocol-Version'),b.UPSTREAM_VERSION)
        self.assertEqual(header(req,'Mcp-Method'),'tools/call')
        self.assertEqual(header(req,'Mcp-Name'),'cube_discover_surface')
        self.assertEqual(header(req,'User-Agent'),'Lunados-Cube-Codex-Bridge/0.1')
        payload=json.loads(req.data)
        meta=payload['params']['_meta']
        self.assertEqual(meta['io.modelcontextprotocol/protocolVersion'],b.UPSTREAM_VERSION)
        self.assertEqual(meta['io.modelcontextprotocol/clientCapabilities'],{})
        self.assertEqual(meta['io.modelcontextprotocol/clientInfo']['name'],b.BRIDGE_NAME)
        self.assertNotIn('SENSITIVE',json.dumps(response))
        self.assertNotIn('SENSITIVE',req.data.decode())

    def test_tools_and_14_resources(self):
        op=FakeOpener();bridge=b.Bridge(opener=op)
        with patch.object(b,'keychain_token',return_value='TOKEN'):
            t=bridge.forward({'jsonrpc':'2.0','id':2,'method':'tools/list'})
            r=bridge.forward({'jsonrpc':'2.0','id':3,'method':'resources/list'})
        self.assertEqual([x['name'] for x in t[0]['result']['tools']],TOOLS)
        self.assertEqual(len(r[0]['result']['resources']),14)

    def test_resource_uri_mirror_header(self):
        op=FakeOpener();bridge=b.Bridge(opener=op)
        uri='aiaeao://p0/resources/v1'
        with patch.object(b,'keychain_token',return_value='TOKEN'):
            bridge.forward({'jsonrpc':'2.0','id':1,'method':'resources/read','params':{'uri':uri}})
        self.assertEqual(header(op.requests[0],'Mcp-Name'),uri)

    def test_secret_only_in_http_not_stdout(self):
        op=FakeOpener();bridge=b.Bridge(opener=op)
        with patch.object(b,'keychain_token',return_value='SECRET-NOT-TO-LOG'):
            msg={'jsonrpc':'2.0','id':1,'method':'tools/list','params':{}}
            res=bridge.forward(msg)
        self.assertEqual(len(res[0]['result']['tools']),7)
        self.assertEqual(header(op.requests[0],'Authorization'),'Bearer SECRET-NOT-TO-LOG')
        self.assertNotIn('SECRET-NOT-TO-LOG',json.dumps(res))

    def test_sse_parsing(self):
        s='event: message\ndata: {"jsonrpc":"2.0","id":8,"result":{"tools":[]}}\n\n'
        items=list(b.responses(s.encode(),'text/event-stream; charset=utf-8'))
        self.assertEqual(items[0]['id'],8)

    def test_declared_redirect_refusal(self):
        self.assertRaises(b.BridgeFailure,b.NoRedirects().redirect_request,None,None,302,'redirect',{},'https://evil.com')

    def test_notification_no_stdout(self):
        class FakeInput:
            def __init__(self):self.buffer=io.BytesIO(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        class DummyBridge:
            def forward(self,msg):return []
        out=io.StringIO();b.process_stream(FakeInput(),out,DummyBridge());self.assertEqual(out.getvalue(),'')

    def test_error_response_is_sanitized(self):
        class FailingOpener:
            def open(self,req,timeout):
                raise urllib.error.HTTPError(req.full_url,403,'no',
                                             {'Content-Type':'text/plain'},io.BytesIO(b'1010'))
        bridge=b.Bridge(opener=FailingOpener())
        with patch.object(b,'keychain_token',return_value='SUPERSECRET'):
            with self.assertRaisesRegex(b.BridgeFailure,'G5_UPSTREAM_HTTP_403'):
                bridge.forward({'jsonrpc':'2.0','id':1,'method':'tools/list'})

    def test_install_is_idempotent_and_preserves_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);conf=root/'config.toml';conf.write_text('[notice]\nenabled=true\n')
            dest=root/'bridge.py'
            a=i.install(conf,dest,ROOT/'g5_stdio_bridge.py',pathlib.Path('/usr/bin/python3'),dry_run=True)
            self.assertIn('[notice]',a)
            self.assertFalse(dest.exists())
            applied=i.install(conf,dest,ROOT/'g5_stdio_bridge.py',pathlib.Path('/usr/bin/python3'),dry_run=False)
            self.assertTrue(dest.exists())
            self.assertEqual(applied,conf.read_text())
            again=i.install(conf,dest,ROOT/'g5_stdio_bridge.py',pathlib.Path('/usr/bin/python3'),dry_run=False)
            self.assertEqual(applied,again)
            self.assertTrue((root/'config.toml.aiaeao-g5.backup').exists())

    def test_refuses_unmanaged_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            conf=pathlib.Path(tmp)/'config.toml';conf.write_text('[mcp_servers.aiaeao_cube_g5]\nurl="https://test"\n')
            with self.assertRaises(RuntimeError):i.install(conf,pathlib.Path(tmp)/'b',ROOT/'g5_stdio_bridge.py',pathlib.Path('/usr/bin/python3'))

    def test_no_bearer_literal_in_toml(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg=i.install(pathlib.Path(tmp)/'cfg',pathlib.Path(tmp)/'dest',ROOT/'g5_stdio_bridge.py',pathlib.Path('/usr/bin/python3'))
            self.assertNotIn('Bearer ',cfg)
            self.assertNotIn('MCP_BEARER_TOKEN',cfg)

    def test_input_limit(self):
        with patch.object(b,'keychain_token',return_value='secret'):
            op=FakeOpener();br=b.Bridge(opener=op)
            with self.assertRaises(ValueError):
                br.forward({'jsonrpc':'2.0','method':'tools/call','id':1,
                            'params':{'payload':'a'*(b.MAX_INPUT_BYTES+2)}})

    def test_content_size(self):
        self.assertEqual(b.MAX_RESPONSE_BYTES,8*1024*1024)

if __name__=='__main__':unittest.main()
