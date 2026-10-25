import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
from email.message import Message
from types import SimpleNamespace

ROOT=pathlib.Path(__file__).resolve().parents[1]/'scripts'

def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
b=load('g5_stdio_bridge');i=load('install_codex_g5')

class FakeHttp:
    def __init__(self,body,typ='application/json',sid=None):
        self.body=body;self.headers=Message();self.headers['Content-Type']=typ
        if sid:self.headers['Mcp-Session-Id']=sid
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def read(self,max_bytes):return self.body[:max_bytes]
class FakeOpener:
    def __init__(self):self.requests=[]
    def open(self, req, timeout):
        self.requests.append(req)
        body=json.dumps({'jsonrpc':'2.0','id':1,'result':{'ok':True}}).encode()
        return FakeHttp(body,sid='a-session')

class Tests(unittest.TestCase):
    def test_expected_url(self):
        self.assertEqual(b.REMOTE,'https://aiaeao-cube-g5-gateway.jo-885.workers.dev/mcp')
    def test_secret_only_in_http_not_stdout(self):
        op=FakeOpener();bridge=b.Bridge(opener=op)
        with patch.object(b,'keychain_token',return_value='SECRET-NOT-TO-LOG'):
            msg={'jsonrpc':'2.0','id':1,'method':'tools/list','params':{}}
            res=bridge.forward(msg)
        self.assertTrue(res[0]['result']['ok'])
        self.assertEqual(op.requests[0].get_header('Authorization'),'Bearer SECRET-NOT-TO-LOG')
        self.assertNotIn('SECRET-NOT-TO-LOG',json.dumps(res))
        self.assertEqual(bridge.session_id,'a-session')
    def test_sse_parsing(self):
        s='event: message\ndata: {"jsonrpc":"2.0","id":8,"result":{"tools":[]}}\n\n'
        items=list(b.responses(s.encode(),'text/event-stream; charset=utf-8'))
        self.assertEqual(items[0]['id'],8)
    def test_declared_redirect_refusal(self):
        self.assertRaises(ValueError,b.NoRedirects().redirect_request,None,None,302,'redirect',{},'https://evil.com')
    def test_notification_no_stdout(self):
        class FakeInput:
            def __init__(self):self.buffer=io.BytesIO(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        class DummyBridge:
            def forward(self,msg):return []
        out=io.StringIO();b.process_stream(FakeInput(),out,DummyBridge());self.assertEqual(out.getvalue(),'')
    def test_install_is_idempotent_and_preserves_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);conf=root/'config.toml';conf.write_text('[notice]\nenabled=true\n')
            dest=root/'bridge.py'
            a=i.install(conf,dest,ROOT/'g5_stdio_bridge.py',pathlib.Path('/usr/bin/python3'),dry_run=True)
            self.assertIn('[notice]',a)
            self.assertFalse(dest.exists()) # preview does not touch anything
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
            with self.assertRaises(ValueError):br.forward({'jsonrpc':'2.0','method':'tools/call','id':1,'params':{'payload':'a'*(b.MAX_INPUT_BYTES+2)}})
    def test_content_size(self):
        self.assertEqual(b.MAX_RESPONSE_BYTES,8*1024*1024)
if __name__=='__main__':unittest.main()
