import test from 'node:test';
import assert from 'node:assert/strict';
import {withinLimit,equalSecret} from '../src/security.mjs';

test('constant-time-like secret compare functional equality',()=>{
  assert.ok(equalSecret('Bearer abc','Bearer abc'));
  assert.equal(equalSecret('Bearer abc','Bearer abd'),false);
  assert.equal(equalSecret('Bearer abc','Bearer abc1'),false);
  assert.equal(equalSecret('Bearer ','Bearer abc'),false);
});

test('limited request stream preserved',async()=>{
  const data=new TextEncoder().encode('{"x":"ä"}');
  const req=new Request('https://example.test/mcp',{method:'POST',body:data});
  const out=await withinLimit(req,50);
  assert.deepEqual(Array.from(out),Array.from(data));
});

test('limit rejects excessive request even if content-length missing',async()=>{
  const data=new Uint8Array(1024);
  const req=new Request('https://example.test/mcp',{method:'POST',body:data});
  req.headers.delete('content-length');
  assert.equal(await withinLimit(req,500),null);
});

test('declared content length rejected before stream read',async()=>{
  const req=new Request('https://example.test/mcp',{method:'POST',body:'a'});
  req.headers.set('content-length','99999');
  assert.equal(await withinLimit(req,500),null);
});
