"""G1.1 tool-only host fallback: independent offline tests, no SDK required."""
from __future__ import annotations
import hashlib
import json
import unittest
from aiaeao_mcp_local import p0_resources as p0
from aiaeao_mcp_local import p0_tool as tool
from aiaeao_mcp_local.bridge import BridgeFailure

MORPH='https://cube.lunados.net/v9.4/morphology.md'
CONCEPTS='https://cube.lunados.net/v9.4/grammar/concepts.json'

class TestFallback(unittest.TestCase):
    def test_catalog_index_one_page(self):
        p=tool.read_reference(p0.INDEX_URI)
        self.assertTrue(p['complete'])
        self.assertEqual(p['offset'],0)
        self.assertIsNone(p['next_offset'])
        self.assertEqual(json.loads(p['content'])['format'],'aiaeao.cube.mcp-p0-resources/1')
    def test_index_exact_utf8(self):
        p=tool.read_reference(p0.INDEX_URI)
        self.assertEqual(p['content'].encode('utf-8'),p0.read_bytes(p0.INDEX_URI))
        self.assertEqual(p['sha256'],hashlib.sha256(p0.read_bytes(p0.INDEX_URI)).hexdigest())
    def test_roundtrip_all_13(self):
        for entry in p0.entries():
            with self.subTest(uri=entry['uri']):
                pages=[]; offset=0; seen=set()
                while True:
                    self.assertNotIn(offset,seen)
                    seen.add(offset)
                    p=tool.read_reference(entry['uri'],offset,511)
                    self.assertEqual(p['sha256'],entry['sha256'])
                    self.assertTrue(p['integrity_verified'])
                    self.assertEqual(p['source_warrant'],'canonical_documentary_reference_only')
                    self.assertEqual(p['total_bytes'],entry['bytes'])
                    self.assertLessEqual(p['page_bytes'],511)
                    self.assertEqual(p['page_bytes'],len(p['content'].encode('utf-8')))
                    pages.append(p['content'].encode('utf-8'))
                    if p['complete']:
                        self.assertIsNone(p['next_offset'])
                        break
                    self.assertGreater(p['next_offset'],offset)
                    offset=p['next_offset']
                self.assertEqual(b''.join(pages),p0.read_bytes(entry['uri']))
    def test_unicode_page_safe(self):
        original=p0.read_bytes(MORPH)
        found=None
        for i in range(4,len(original)-4):
            if original[i]&0xC0==0x80:
                continue
            for j in range(i+4,i+35):
                if j<len(original) and original[j]&0xC0==0x80:
                    found=(i,j-i)
                    break
            if found:break
        self.assertIsNotNone(found)
        offset,count=found
        p=tool.read_reference(MORPH,offset,count)
        self.assertLess(p['page_bytes'],count)
        self.assertEqual(p['content'].encode('utf-8'),original[offset:p['next_offset']])
    def test_repeats_deterministic(self):
        self.assertEqual(tool.read_reference(CONCEPTS,0,4096),tool.read_reference(CONCEPTS,0,4096))
    def test_reference_index_uris(self):
        ids={x['uri'] for x in json.loads(tool.read_reference(p0.INDEX_URI)['content'])['resources']}
        self.assertEqual(ids,{e['uri'] for e in p0.entries()})
    def test_no_p1_claim(self):
        r=tool.read_reference(CONCEPTS)
        self.assertIs(r['p1_validation_performed'],False)
        self.assertTrue(r['read_only'])
        self.assertEqual(r['transport_role'],'mcp_tool_fallback_for_resources')
    def assert_error(self,code,uri=CONCEPTS,offset=0,max_bytes=8192):
        with self.assertRaises(BridgeFailure) as caught:
            tool.read_reference(uri,offset,max_bytes)
        self.assertEqual(caught.exception.diagnostic['code'],code)
        self.assertEqual(caught.exception.diagnostic['stage'],'p0_reference')
    def test_unknown(self):self.assert_error('P0_URI_NOT_FOUND',uri='https://example.net/manifest.json')
    def test_not_url_fetched(self):self.assert_error('P0_URI_NOT_FOUND',uri='file:///etc/passwd')
    def test_traversal(self):self.assert_error('P0_URI_NOT_FOUND',uri='https://cube.lunados.net/../manifest.json')
    def test_uri_bad_type(self):self.assert_error('P0_URI_INVALID',uri=None)
    def test_uri_empty(self):self.assert_error('P0_URI_INVALID',uri='')
    def test_uri_too_long(self):self.assert_error('P0_URI_INVALID',uri='x'*1024)
    def test_offset_negative(self):self.assert_error('P0_OFFSET_INVALID',offset=-1)
    def test_offset_boolean(self):self.assert_error('P0_OFFSET_INVALID',offset=True)
    def test_offset_out_of_range(self):self.assert_error('P0_OFFSET_INVALID',offset=1000000)
    def test_chunk_limit_zero(self):self.assert_error('P0_PAGE_LIMIT_INVALID',max_bytes=0)
    def test_chunk_limit_too_small(self):self.assert_error('P0_PAGE_LIMIT_INVALID',max_bytes=3)
    def test_chunk_limit_too_large(self):self.assert_error('P0_PAGE_LIMIT_INVALID',max_bytes=32769)
    def test_chunk_limit_bool(self):self.assert_error('P0_PAGE_LIMIT_INVALID',max_bytes=True)
    def test_split_utf8_offset(self):
        src=p0.read_bytes(MORPH)
        i=next(i for i,x in enumerate(src) if x&0xC0 == 0x80)
        self.assert_error('P0_OFFSET_INVALID',uri=MORPH,offset=i)
    def test_end_of_resource(self):
        length=len(p0.read_bytes(CONCEPTS))
        p=tool.read_reference(CONCEPTS,offset=length)
        self.assertTrue(p['complete'])
        self.assertEqual(p['content'],'')
        self.assertEqual(p['page_bytes'],0)
    def test_max_page_is_bounded(self):
        p=tool.read_reference(MORPH,0,32768)
        self.assertLessEqual(len(p['content'].encode('utf-8')),32768)
        self.assertFalse(p['complete'])
    def test_chunk_digest_is_full_digest(self):
        p=tool.read_reference(MORPH)
        self.assertEqual(p['sha256'],hashlib.sha256(p0.read_bytes(MORPH)).hexdigest())
    def test_missing_file_diagnostic_no_path(self):
        from unittest.mock import patch
        from pathlib import Path
        with patch.object(p0,'SNAPSHOT_ROOT',Path('/does-not-exist')):
            with self.assertRaises(BridgeFailure) as c: tool.read_reference(CONCEPTS)
            self.assertNotIn('/does-not-exist',str(c.exception.diagnostic))
            self.assertEqual(c.exception.diagnostic['code'],'P0_CONTENT_UNAVAILABLE')

if __name__=='__main__':unittest.main()
