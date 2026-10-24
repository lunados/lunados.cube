"""CP-001 G1 independent stdlib tests. No MCP SDK or internet required."""
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from aiaeao_mcp_local import p0_resources as p0

class TestPinnedResourceIndex(unittest.TestCase):
    def test_full_snapshot_passes(self):
        v=p0.verify_snapshot()
        self.assertEqual(v['status'],'PASS')
        self.assertEqual(v['resources'],13)
        self.assertEqual(v['reference_version'],'v9.4')
    def test_count_and_order(self):
        uris=[e['uri'] for e in p0.entries()]
        self.assertEqual(uris,sorted(set(uris)))
        self.assertEqual(len(uris),13)
    def test_no_remote_targets(self):
        self.assertTrue(all(e['uri'].startswith('https://cube.lunados.net/') for e in p0.entries()))
    def test_lock_hash(self):
        self.assertEqual(hashlib.sha256(p0.LOCK_FILE.read_bytes()).hexdigest(),p0.PINNED_LOCK_SHA256)
    def test_pinned_bytes_all(self):
        for e in p0.entries():
            with self.subTest(uri=e['uri']):
                b=p0.read_bytes(e['uri'])
                self.assertEqual(hashlib.sha256(b).hexdigest(),e['sha256'])
                self.assertEqual(len(b),e['bytes'])
    def test_utf8_byte_roundtrip_all(self):
        for e in p0.entries():
            with self.subTest(uri=e['uri']):
                self.assertEqual(p0.read_text(e['uri']).encode('utf-8'),p0.read_bytes(e['uri']))
    def test_morphology_key(self):
        text=p0.read_text('https://cube.lunados.net/v9.4/morphology.md')
        self.assertGreater(len(text),100000)
    def test_concepts_is_json(self):
        data=json.loads(p0.read_text('https://cube.lunados.net/v9.4/grammar/concepts.json'))
        self.assertIsInstance(data,(dict,list))
    def test_notation_is_json(self):
        self.assertIsInstance(json.loads(p0.read_text('https://cube.lunados.net/v9.4/notation/ast.schema.json')),dict)
    def test_visual_glyphs_json(self):
        self.assertIsInstance(json.loads(p0.read_text('https://cube.lunados.net/v9.4/visual/symbols.json')),dict)
    def test_manifest_references_match(self):
        self.assertEqual(p0.verify_snapshot()['status'],'PASS')
    def test_index_is_json(self):
        index=json.loads(p0.read_text(p0.INDEX_URI))
        self.assertEqual(index['format'],'aiaeao.cube.mcp-p0-resources/1')
        self.assertEqual(len(index['resources']),13)
    def test_index_no_local_paths(self):
        raw=p0.read_text(p0.INDEX_URI)
        self.assertNotIn('/mnt/',raw)
        self.assertNotIn('/Users/',raw)
        self.assertNotIn('p0_snapshot',raw)
    def test_index_not_truth_claim(self):
        self.assertEqual(p0.catalog()['source_warrant'],'canonical_documentary_reference_only')
    def test_index_offline_flag(self):
        self.assertIs(p0.catalog()['offline'], True)
    def test_index_source_sha_each(self):
        expected={e['uri']:e['sha256'] for e in p0.entries()}
        self.assertEqual({e['uri']:e['sha256'] for e in p0.catalog()['resources']},expected)
    def test_index_deterministic(self):
        self.assertEqual(p0.read_bytes(p0.INDEX_URI),p0.read_bytes(p0.INDEX_URI))
    def test_root_uri(self):
        self.assertGreater(len(p0.read_bytes('https://cube.lunados.net/manifest.json')),1000)
    def test_line_endings_preserved(self):
        for e in p0.entries():
            t=p0.read_text(e['uri'])
            self.assertEqual(len(t.encode('utf-8')),e['bytes'])
    def test_all_uri_types(self):
        extensions={Path(e['path']).suffix for e in p0.entries()}
        self.assertEqual(extensions,{'.json','.md','.ebnf'})

class TestURIAllowlist(unittest.TestCase):
    def assert_reject(self,uri):
        with self.assertRaises(p0.P0ResourceError) as caught:
            p0.read_text(uri)
        self.assertEqual(caught.exception.code,'P0_URI_NOT_FOUND' if isinstance(uri,str) else 'P0_URI_INVALID')
    def test_arbitrary_https(self):self.assert_reject('https://example.org/secret')
    def test_arbitrary_file(self):self.assert_reject('file:///etc/passwd')
    def test_arbitrary_ssh(self):self.assert_reject('ssh://localhost/etc/passwd')
    def test_path_traversal(self):self.assert_reject('https://cube.lunados.net/v9.4/../manifest.json')
    def test_url_encoded_traversal(self):self.assert_reject('https://cube.lunados.net/v9.4/%2e%2e/manifest.json')
    def test_query_params(self):self.assert_reject('https://cube.lunados.net/v9.4/morphology.md?x=1')
    def test_fragment(self):self.assert_reject('https://cube.lunados.net/v9.4/morphology.md#ignore')
    def test_other_host(self):self.assert_reject('https://evil.example.net/v9.4/morphology.md')
    def test_null_uri(self):self.assert_reject(None)
    def test_dictionary_uri(self):self.assert_reject({'uri':'manifest.json'})
    def test_case_sensitive(self):self.assert_reject('https://cube.lunados.net/V9.4/morphology.md')
    def test_empty(self):self.assert_reject('')
    def test_lookalike(self):self.assert_reject('https://cube.lunados.net.evil.io/manifest.json')
    def test_no_network(self):
        import socket
        with patch.object(socket,'create_connection',side_effect=AssertionError('unexpected HTTP fetch')):
            self.assertGreater(len(p0.read_bytes('https://cube.lunados.net/v9.4/morphology.md')),1)

class TestTampering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td=tempfile.TemporaryDirectory()
        cls.tmp=Path(cls.td.name)
        shutil.copytree(p0.SNAPSHOT_ROOT, cls.tmp/'p0_snapshot')
    @classmethod
    def tearDownClass(cls):cls.td.cleanup()
    def test_tampered_content_rejected(self):
        path=self.tmp/'p0_snapshot/v9.4/notation/syntax.json'
        orig=path.read_bytes()
        try:
            path.write_bytes(orig[:-1]+b' ')
            with patch.object(p0,'SNAPSHOT_ROOT',self.tmp/'p0_snapshot'):
                with self.assertRaises(p0.P0ResourceError) as c:
                    p0.read_bytes('https://cube.lunados.net/v9.4/notation/syntax.json')
                self.assertEqual(c.exception.code,'P0_CONTENT_MISMATCH')
        finally:path.write_bytes(orig)
    def test_missing_content_fails(self):
        path=self.tmp/'p0_snapshot/v9.4/time.json'
        path.rename(path.with_suffix('.bak'))
        try:
            with patch.object(p0,'SNAPSHOT_ROOT',self.tmp/'p0_snapshot'):
                with self.assertRaises(p0.P0ResourceError) as c:p0.read_bytes('https://cube.lunados.net/v9.4/time.json')
                self.assertEqual(c.exception.code,'P0_CONTENT_UNAVAILABLE')
        finally:path.with_suffix('.bak').rename(path)
    def test_tampered_lock_rejected(self):
        path=self.tmp/'p0_snapshot/lock.json'
        old=path.read_bytes()
        try:
            path.write_bytes(old+b'\n')
            with patch.object(p0,'LOCK_FILE',path):
                with self.assertRaises(p0.P0ResourceError) as c:p0.entries()
                self.assertEqual(c.exception.code,'P0_LOCK_MISMATCH')
        finally:path.write_bytes(old)
    def test_symlink_escape_rejected(self):
        path=self.tmp/'p0_snapshot/v9.4/time.json'
        real=path.read_bytes()
        with tempfile.TemporaryDirectory() as external:
            target=Path(external)/'copy';target.write_bytes(real)
            path.unlink();path.symlink_to(target)
            try:
                with patch.object(p0,'SNAPSHOT_ROOT',self.tmp/'p0_snapshot'):
                    with self.assertRaises(p0.P0ResourceError) as c:p0.read_bytes('https://cube.lunados.net/v9.4/time.json')
                    self.assertEqual(c.exception.code,'P0_PATH_INVALID')
            finally:path.unlink();path.write_bytes(real)

class TestMCPRegistration(unittest.TestCase):
    def test_registration_exactly_14(self):
        class Stub:
            def __init__(self):self.data=[]
            def resource(self,uri,**kw):
                def decorator(fn):self.data.append((uri,kw,fn));return fn
                return decorator
        server=Stub()
        p0.register_resources(server)
        self.assertEqual(len(server.data),14)
        self.assertEqual([v[0] for v in server.data], [e['uri'] for e in p0.entries()]+[p0.INDEX_URI])
        for uri,meta,fn in server.data:
            with self.subTest(uri=uri):
                self.assertEqual(fn(),p0.read_text(uri))
                self.assertEqual(meta['mime_type'],'application/json' if uri==p0.INDEX_URI or uri.endswith('.json') else meta['mime_type'])
    def test_resource_metadata_digest(self):
        class Stub:
            def __init__(self):self.data=[]
            def resource(self,uri,**kw):
                def decorate(fn):self.data.append((uri,kw));return fn
                return decorate
        m=Stub();p0.register_resources(m)
        for item in p0.entries():
            _, props=next((uri,kwargs) for uri,kwargs in m.data if uri==item['uri'])
            self.assertEqual(props['meta']['sha256'],item['sha256'])
            self.assertEqual(props['meta']['bytes'],item['bytes'])
            self.assertIn(item['sha256'],props['description'])

if __name__=='__main__':unittest.main()
