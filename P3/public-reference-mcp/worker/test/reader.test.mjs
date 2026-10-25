import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readPublicReference, ReferenceError, handleMcpRequest} from '../src/worker.mjs';

const ORIGIN='https://cube.lunados.net';
const path=ORIGIN+'/vNext/notation/grammar.ebnf';
const assetContent='cube ::= X Y Z;\n';
const sha = createHash('sha256').update(assetContent).digest('hex');
const manifest={reference_version:'vNext',point_of_truth:ORIGIN+'/vNext/morphology.md',entrypoints:{core:ORIGIN+'/vNext/core.json'},assets:{ebnf:{href:path,media_type:'text/plain',sha256:sha,bytes:Buffer.byteLength(assetContent)}}};
function source(extra={}) {
  const requests=[];
  const f=async (url,options) => {
    requests.push({url,options});
    if(url===ORIGIN+'/manifest.json') return new Response(JSON.stringify(extra.manifest ?? manifest), {headers:{'content-type':'application/json'}});
    if(url===path) return new Response(extra.assetText ?? assetContent, {headers:{'content-type':'text/plain'}});
    if(extra.redirectFrom && url===extra.redirectFrom) return new Response(null, {status:302, headers:{location:extra.redirectTo}});
    throw new Error('Unexpected request '+url);
  };
  return {f,requests};
}
function rpc(method,params,id=1) {return new Request('https://public.example.workers.dev/mcp',{method:'POST',headers:{'content-type':'application/json','accept':'application/json, text/event-stream'},body:JSON.stringify({jsonrpc:'2.0',id,method,params})});}

// Basic end-to-end tool envelope and live version / manifest dynamic selection.
test('AC01/02: MCP initialize, list tool and live raw manifest read', async()=>{
 const {f,requests}=source();
 const init=await (await handleMcpRequest(rpc('initialize',{protocolVersion:'2026-07-28'}),f)).json();
 assert.equal(init.result.protocolVersion,'2026-07-28');
 const listing=await (await handleMcpRequest(rpc('tools/list',{}),f)).json();
 assert.deepEqual(listing.result.tools.map(x=>x.name),['cube_read_public_reference']);
 const result=await (await handleMcpRequest(rpc('tools/call',{name:'cube_read_public_reference',arguments:{}}),f)).json();
 assert.equal(result.result.structuredContent.reference_version,'vNext');
 assert.equal(result.result.structuredContent.sha256_verified,null);
 assert.deepEqual(JSON.parse(result.result.structuredContent.content),manifest);
 assert.deepEqual(requests.map(x=>x.url),[ORIGIN+'/manifest.json']);
 assert.equal(requests[0].options.method,'GET');
 assert.equal(requests[0].options.redirect,'manual');
});

test('AC03/05: reads keyed asset and validates original byte digest',async()=>{
 const {f,requests}=source();
 const data=await readPublicReference('ebnf',f);
 assert.equal(data.content,assetContent);
 assert.equal(data.sha256_verified,true);
 assert.equal(data.reference_version,'vNext');
 assert.deepEqual(requests.map(x=>x.url),[ORIGIN+'/manifest.json',path]);
});

test('AC04: unknown keys, paths, URLs rejected without second GET',async()=>{
 for(const key of ['../core','https://evil.test/x','foo/bar','a?x=1','missing','__proto__']) {
   const {f,requests}=source();
   await assert.rejects(readPublicReference(key,f),e=>e instanceof ReferenceError && ['INVALID_ASSET_KEY','ASSET_KEY_NOT_FOUND'].includes(e.code));
   assert.deepEqual(requests.map(x=>x.url),/^[a-zA-Z0-9_-]{1,128}$/.test(key) ? [ORIGIN+'/manifest.json'] : []);
 }
});

test('AC04: malicious manifest URLs and redirects to other hosts fail closed',async()=>{
 let m=structuredClone(manifest);m.assets.ebnf.href='https://evil.test/payload';
 await assert.rejects(readPublicReference('ebnf',source({manifest:m}).f),{code:'SOURCE_NOT_ALLOWED'});
 m=structuredClone(manifest);m.assets.ebnf.href=ORIGIN+'/redirect';
 const {f}=source({manifest:m,redirectFrom:ORIGIN+'/redirect',redirectTo:'https://evil.test/payload'});
 await assert.rejects(readPublicReference('ebnf',f),{code:'SOURCE_NOT_ALLOWED'});
});

test('AC05: no raw content on digest or length mismatch',async()=>{
 const {f}=source({assetText:'cube ::= MALICIOUS;\n'});
 await assert.rejects(readPublicReference('ebnf',f),{code:'INTEGRITY_MISMATCH'});
 let m=structuredClone(manifest);m.assets.ebnf.bytes=1;
 await assert.rejects(readPublicReference('ebnf',source({manifest:m}).f),{code:'INTEGRITY_MISMATCH'});
 const r=await (await handleMcpRequest(rpc('tools/call',{name:'cube_read_public_reference',arguments:{asset_key:'ebnf'}}),source({assetText:'bad'}).f)).json();
 assert.equal(r.result.isError,true);
 assert.equal(r.result.structuredContent.code,'INTEGRITY_MISMATCH');
 assert.equal(Object.hasOwn(r.result.structuredContent,'content'),false);
});

test('limits oversized declared assets and streamed content',async()=>{
 const large=async u=>u.endsWith('/manifest.json')?new Response(JSON.stringify(manifest)):
 new Response('small',{headers:{'content-length':'9999999'}});
 await assert.rejects(readPublicReference('ebnf',large),{code:'ASSET_TOO_LARGE'});
 const streamed=async u=>u.endsWith('/manifest.json')?new Response(JSON.stringify(manifest)):
 new Response(new Uint8Array(512*1024+1));
 await assert.rejects(readPublicReference('ebnf',streamed),{code:'ASSET_TOO_LARGE'});
});

test('structured source failures, origins and malformed arguments',async()=>{
 let result=await handleMcpRequest(new Request('https://public.example.workers.dev/mcp',{method:'POST',headers:{origin:'https://evil.test','content-type':'application/json'},body:'{}'}));
 assert.equal(result.status,403);
 result=await handleMcpRequest(rpc('tools/call',{name:'cube_read_public_reference',arguments:{asset_key:'missing'}}),source().f);
 assert.equal((await result.json()).result.structuredContent.code,'ASSET_KEY_NOT_FOUND');
 result=await handleMcpRequest(rpc('tools/call',{name:'cube_read_public_reference',arguments:{url:'https://evil.test'}}),source().f);
 assert.equal((await result.json()).error.code,-32602);
 result=await handleMcpRequest(new Request('https://public.example.workers.dev/mcp',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',method:'notifications/initialized'})}),source().f);
 assert.equal(result.status,202);
});
