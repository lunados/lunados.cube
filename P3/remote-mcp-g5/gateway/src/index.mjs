/** G5 Cloudflare Worker: authenticated, stateless MCP v2 HTTP ingress.
 *
 * This gateway contains NO P0/P1/P2 logic. All operations execute via the
 * private CORE Service Binding; it never fetches public URLs on behalf of tools.
 */
import { McpServer, createMcpHandler } from '@modelcontextprotocol/server';
import { z } from 'zod';
import registry from './p0-registry.json';
import { withinLimit, equalSecret } from './security.mjs';

const MAX_REQUEST_BYTES = 2 * 1024 * 1024 + 4096;
const MAX_RESPONSE_BYTES = 2 * 1024 * 1024;
const TEXT_HEADERS = { 'content-type': 'text/plain; charset=utf-8',
  'cache-control': 'no-store', 'x-content-type-options': 'nosniff' };

function unavailable(status, message) { return new Response(message, {status, headers: TEXT_HEADERS}); }

async function coreCall(env, operation, args = {}) {
  const body = JSON.stringify({operation,arguments:args});
  if (new TextEncoder().encode(body).byteLength > MAX_REQUEST_BYTES)
    return {ok:false,diagnostic:{code:'G5_REQUEST_TOO_LARGE',message:'Operation exceeds remote limit'}};
  const response = await env.CORE.fetch(new Request('https://core.internal/execute',
    {method:'POST',headers:{'content-type':'application/json'},body}));
  if (!response.ok) throw new Error('G5_CORE_UNAVAILABLE');
  const data = await response.arrayBuffer();
  if (data.byteLength > MAX_RESPONSE_BYTES) throw new Error('G5_CORE_OUTPUT_TOO_LARGE');
  return JSON.parse(new TextDecoder().decode(data));
}

async function callTool(env,name,args){
  try {
    const reply=await coreCall(env,name,args);
    const payload=reply.ok?reply.result:reply.diagnostic;
    return {content:[{type:'text',text:JSON.stringify(payload)}],
            structuredContent:payload,isError:!reply.ok};
  } catch {
    const diagnostic={format:'aiaeao.cube.mcp-g5-diagnostic/1',code:'G5_CORE_UNAVAILABLE',
       message:'Remote core unavailable or exceeded limits',status:'FAIL',files_written:false};
    return {content:[{type:'text',text:JSON.stringify(diagnostic)}],structuredContent:diagnostic,isError:true};
  }
}

function createServer(env) {
  const server = new McpServer({name:'aiaeao-cube-mcp-remote-g5',version:'0.1.0-proof'},
     {instructions:'Use cube_discover_surface for P0/P1/P2; all P1 and P2 outcomes are independent. ' +
      'P0 resources are documentary only. No truth, Authority or Admission is inferred.'});
  const add = (name,desc,schema) => server.registerTool(name,
     {description:desc,inputSchema:schema},async (args)=>callTool(env,name,args));
  add('cube_get_capabilities','Legacy P2 printer capability card; use cube_discover_surface for whole Cube.',z.object({}));
  add('cube_prepare_print','Bind declared VP-03 bundle to VP-04 print job; no inferred facets.',z.object({
    bundle:z.record(z.string(),z.unknown()),lens:z.string(),granularity:z.enum(['overview','standard','detail']),
    overflow:z.enum(['summarize','reject']).optional(),focus:z.object({kind:z.string(),id:z.string()}).nullable().optional(),
    max_items:z.number().int().positive().nullable().optional(),max_edges:z.number().int().positive().nullable().optional()}));
  add('cube_check_print','Evaluate VP-04 job and immutable audit report; no P1 validation.',z.object({job:z.record(z.string(),z.unknown())}));
  add('cube_render_svg','Return UTF-8 SVG and VP-06 report; declared content remains unverified.',z.object({job:z.record(z.string(),z.unknown())}));
  add('cube_read_reference','Read pinned P0 reference with bounded UTF-8 byte pagination, no arbitrary URLs.',z.object({
    uri:z.string(),offset:z.number().int().min(0).optional(),max_bytes:z.number().int().min(4).max(32768).optional()}));
  add('cube_validate','Run unchanged P1 validation; PASS/FAIL/UNRESOLVED are valid results.',z.object({
    input_text:z.string(),input_format:z.enum(['acg_text','json_ast']).optional(),
    context:z.record(z.string(),z.unknown()).nullable().optional(),
    qualification_profiles:z.record(z.string(),z.unknown()).nullable().optional()}));
  add('cube_discover_surface','Describe whole P0/P1/P2 capability surface and trust boundaries.',z.object({}));
  // Resources use the *same* pinned bytes as the fallback tool.
  for (const item of registry.resources) {
    server.registerResource(item.name,item.uri,{mimeType:item.mime_type},async(uri)=>{
      const reply=await coreCall(env,'p0_resource_read',{uri:String(uri)});
      if (!reply.ok) throw new Error(reply.diagnostic.code);
      return {contents:[{uri:String(uri),mimeType:item.mime_type,text:reply.result.text}]};
    });
  }
  return server;
}

export default {
  async fetch(request,env,ctx) {
    const url=new URL(request.url);
    if (url.pathname === '/health' && request.method === 'GET')
      return new Response(JSON.stringify({status:'G5_REMOTE_PROOF_CANDIDATE',version:'0.1.0-proof',authenticated:false}),
        {headers:{'content-type':'application/json','cache-control':'no-store'}});
    if (url.pathname !== '/mcp') return unavailable(404,'Not Found');
    if (request.method !== 'POST') return unavailable(405,'MCP requires POST');
    if (!env.MCP_BEARER_TOKEN || env.MCP_BEARER_TOKEN.length < 32) return unavailable(503,'Authentication not configured');
    const auth=request.headers.get('authorization') ?? '';
    if (!equalSecret(auth,`Bearer ${env.MCP_BEARER_TOKEN}`)) return unavailable(401,'Unauthorized');
    const origin=request.headers.get('origin');
    // Native MCP clients normally send no Origin; browser origins need an exact match.
    if (origin && (!env.MCP_ALLOWED_ORIGIN || origin !== env.MCP_ALLOWED_ORIGIN))
      return unavailable(403,'Unapproved origin');
    const bytes=await withinLimit(request,MAX_REQUEST_BYTES);
    if (bytes === null) return unavailable(413,'MCP request too large');
    const fHeaders=new Headers(request.headers);fHeaders.delete('content-length');
    const forward=new Request(request,{body:bytes,headers:fHeaders});
    const handler=createMcpHandler(()=>createServer(env),{legacy:'reject'});
    const response=await handler.fetch(forward);
    const headers=new Headers(response.headers);
    headers.set('cache-control','no-store');headers.set('x-content-type-options','nosniff');
    return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
  }
};
