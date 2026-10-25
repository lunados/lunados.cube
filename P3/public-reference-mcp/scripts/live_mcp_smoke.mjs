#!/usr/bin/env node
// Live integration against the newly deployed PUBLIC Worker, no secrets required.
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';

const url=process.argv[2];
if (!url || !/^https:\/\/[a-z0-9.-]+\/mcp$/i.test(url) || /aiaeao-cube-g5-gateway/.test(url)) {
 console.error('Usage: node scripts/live_mcp_smoke.mjs https://<PUBLIC-WORKER>.workers.dev/mcp');
 process.exit(2);
}
let id=1;
async function call(method,params={}) {
 const body=JSON.stringify({jsonrpc:'2.0',id:id++,method,params});
 const response=await fetch(url,{method:'POST',headers:{'content-type':'application/json','accept':'application/json, text/event-stream'},body,signal:AbortSignal.timeout(30000)});
 assert.equal(response.status,200,`HTTP ${response.status} for ${method}`);
 const result=await response.json();
 assert.equal(result.jsonrpc,'2.0');
 assert.ok(!result.error, JSON.stringify(result.error));
 return result.result;
}
function digest(content) {return createHash('sha256').update(Buffer.from(content,'utf8')).digest('hex');}
const init=await call('initialize',{protocolVersion:'2025-11-25',capabilities:{},clientInfo:{name:'aiaeao-public-proof',version:'0.1.0'}});
assert.ok(init.capabilities.tools);
console.log('PASS remote MCP initialize:',init.protocolVersion);
const listed=await call('tools/list');
assert.deepEqual(listed.tools.map(x=>x.name),['cube_read_public_reference']);
console.log('PASS tool discovery:',listed.tools[0].name);
async function read(asset_key) {
 const result=await call('tools/call',{name:'cube_read_public_reference',arguments:{asset_key}});
 assert.equal(result.isError,false,JSON.stringify(result.structuredContent));
 return result.structuredContent;
}
const m=await read('manifest');
const doc=JSON.parse(m.content);
assert.equal(m.reference_version,doc.reference_version);
for(const key of ['point_of_truth','entrypoints','assets']) assert.ok(doc[key]);
assert.equal(m.sha256_verified,null);
console.log('PASS live manifest:',m.reference_version, Object.keys(doc.assets).length,'keys');
for(const key of ['core','ebnf','ast_schema']) {
 if (!Object.prototype.hasOwnProperty.call(doc.assets,key)) {
  console.log('SKIP asset absent in live manifest:',key);continue;
 }
 const item=await read(key);
 assert.equal(item.reference_version,doc.reference_version);
 assert.equal(item.source_url,doc.assets[key].href);
 const expected=doc.assets[key].sha256;
 assert.equal(item.sha256_verified,expected ? true : null);
 if (expected) assert.equal(digest(item.content),expected.toLowerCase());
 console.log('PASS asset:',key,'sha256_verified:',item.sha256_verified);
}
for(const key of ['definitely_not_in_the_cube_manifest','https://evil.example/path']) {
 const result=await call('tools/call',{name:'cube_read_public_reference',arguments:{asset_key:key}});
 assert.equal(result.isError,true);
 assert.ok(['ASSET_KEY_NOT_FOUND','INVALID_ASSET_KEY'].includes(result.structuredContent.code));
 console.log('PASS rejected:',key);
}
console.log('PASS PUBLIC REFERENCE LIVE MCP: 1 tool, live manifest, keyed grammar assets, digest parity, invalid keys');
