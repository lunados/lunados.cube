// AIAEAO Cube public documentary reference MCP – stateless, read-only.
// Deliberately independent from the authenticated G5 MCP.
const ORIGIN = 'https://cube.lunados.net';
const MANIFEST_URL = `${ORIGIN}/manifest.json`;
const SERVER_VERSION = '0.1.0';
const TOOL_NAME = 'cube_read_public_reference';
const MAX_REQUEST_BYTES = 32 * 1024;
const MAX_MANIFEST_BYTES = 256 * 1024;
const MAX_ASSET_BYTES = 512 * 1024;
const MAX_REDIRECTS = 3;
const FETCH_TIMEOUT_MS = 10000;
const SUPPORTED_PROTOCOLS = new Set(['2026-07-28', '2025-11-25', '2025-06-18', '2025-03-26']);
const DEFAULT_PROTOCOL = '2025-11-25';
const TEXT_TYPES = /^(text\/[a-z0-9.+-]+|application\/(json|[\w.+-]+\+json|xml|[\w.+-]+\+xml))(?:$|;)/i;

export class ReferenceError extends Error {
  constructor(code, message, details = {}) {
    super(message);
    this.name = 'ReferenceError';
    this.code = code;
    this.details = details;
  }
}

function canonicalURL(candidate, base = undefined) {
  let url;
  try { url = new URL(candidate, base); }
  catch { throw new ReferenceError('INVALID_SOURCE_URL', 'Manifest contains an invalid asset URL'); }
  if (url.protocol !== 'https:' || url.hostname !== 'cube.lunados.net' ||
      url.username || url.password || url.port || url.search || url.hash) {
    throw new ReferenceError('SOURCE_NOT_ALLOWED', 'Only plain HTTPS URLs on cube.lunados.net are allowed');
  }
  return url.href;
}

async function boundedRead(response, limit) {
  const declared = response.headers.get('content-length');
  if (declared && /^\d+$/.test(declared) && Number(declared) > limit) {
    throw new ReferenceError('ASSET_TOO_LARGE', 'Content-Length exceeds the configured limit');
  }
  if (!response.body) return new Uint8Array(0);
  const reader = response.body.getReader();
  const parts = []; let total = 0;
  try {
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > limit) throw new ReferenceError('ASSET_TOO_LARGE', 'Response exceeds the configured byte limit');
      parts.push(value);
    }
  } finally { try { await reader.cancel(); } catch {} }
  const bytes = new Uint8Array(total); let offset = 0;
  for (const part of parts) { bytes.set(part, offset); offset += part.byteLength; }
  return bytes;
}

async function restrictedGet(url, limit, fetchImpl) {
  let current = canonicalURL(url);
  for (let attempt = 0; attempt <= MAX_REDIRECTS; attempt++) {
    let response;
    try {
      response = await fetchImpl(current, {
        method: 'GET', redirect: 'manual', cache: 'no-store',
        headers: {'Accept': 'application/json, text/plain, text/markdown, */*;q=0.1'},
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS)
      });
    } catch (error) {
      throw new ReferenceError('FETCH_FAILED', 'Cannot fetch public reference', {cause: String(error?.name || 'network_error')});
    }
    if ([301, 302, 303, 307, 308].includes(response.status)) {
      if (attempt === MAX_REDIRECTS) throw new ReferenceError('REDIRECT_LIMIT', 'Too many redirects');
      const location = response.headers.get('location');
      if (!location) throw new ReferenceError('REDIRECT_INVALID', 'Missing redirect Location');
      current = canonicalURL(location, current);
      continue;
    }
    if (response.status === 403 || response.status === 401)
      throw new ReferenceError('RESOURCE_FORBIDDEN', 'Source refused public access');
    if (response.status === 404)
      throw new ReferenceError('RESOURCE_NOT_FOUND', 'Public reference asset was not found');
    if (!response.ok)
      throw new ReferenceError('SOURCE_HTTP_ERROR', 'Source returned a non-success HTTP status', {status: response.status});
    return {bytes: await boundedRead(response, limit), url: current, type: response.headers.get('content-type')};
  }
  throw new ReferenceError('REDIRECT_LIMIT', 'Too many redirects');
}

async function sha256(bytes) {
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
  return Array.from(digest, n => n.toString(16).padStart(2, '0')).join('');
}

function decodeText(bytes) {
  try { return new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(bytes); }
  catch { throw new ReferenceError('INVALID_ENCODING', 'Source is not valid UTF-8 text'); }
}

async function loadManifest(fetchImpl) {
  const result = await restrictedGet(MANIFEST_URL, MAX_MANIFEST_BYTES, fetchImpl);
  let manifest;
  try { manifest = JSON.parse(decodeText(result.bytes)); }
  catch { throw new ReferenceError('MANIFEST_INVALID', 'Manifest is not valid JSON'); }
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest) ||
    typeof manifest.reference_version !== 'string' || !manifest.reference_version ||
    !manifest.assets || typeof manifest.assets !== 'object' || Array.isArray(manifest.assets) ||
    !manifest.point_of_truth || !manifest.entrypoints) {
    throw new ReferenceError('MANIFEST_INVALID', 'Manifest is missing required reference fields');
  }
  return {manifest, result};
}

export async function readPublicReference(assetKey = 'manifest', fetchImpl = fetch) {
  if (typeof assetKey !== 'string' || !/^[a-zA-Z0-9_-]{1,128}$/.test(assetKey))
    throw new ReferenceError('INVALID_ASSET_KEY', 'asset_key must be a valid manifest key, not a URL or path');
  const {manifest, result: manifestResult} = await loadManifest(fetchImpl);
  const reference_version = manifest.reference_version;
  if (assetKey === 'manifest') return {
    reference_version, asset_key: 'manifest', source_url: manifestResult.url,
    content_type: 'application/json', content: decodeText(manifestResult.bytes),
    sha256_verified: null, retrieved_at: new Date().toISOString()
  };
  if (!Object.prototype.hasOwnProperty.call(manifest.assets, assetKey))
    throw new ReferenceError('ASSET_KEY_NOT_FOUND', 'asset_key is not listed in current manifest', {asset_key: assetKey});
  const asset = manifest.assets[assetKey];
  if (!asset || typeof asset !== 'object' || typeof asset.href !== 'string')
    throw new ReferenceError('MANIFEST_INVALID', 'Asset entry is missing href', {asset_key: assetKey});
  const assetURL = canonicalURL(asset.href, MANIFEST_URL);
  const contentType = asset.media_type || 'application/octet-stream';
  if (typeof contentType !== 'string' || !TEXT_TYPES.test(contentType))
    throw new ReferenceError('UNSUPPORTED_CONTENT_TYPE', 'Asset is not a supported text reference', {asset_key: assetKey});
  const downloaded = await restrictedGet(assetURL, MAX_ASSET_BYTES, fetchImpl);
  if (typeof asset.bytes === 'number' && (!Number.isSafeInteger(asset.bytes) || downloaded.bytes.length !== asset.bytes))
    throw new ReferenceError('INTEGRITY_MISMATCH', 'Asset byte length does not match manifest', {asset_key: assetKey, sha256_verified: false});
  let verified = null;
  if (asset.sha256 !== undefined && asset.sha256 !== null) {
    if (typeof asset.sha256 !== 'string' || !/^[a-f0-9]{64}$/i.test(asset.sha256))
      throw new ReferenceError('MANIFEST_INVALID', 'Malformed asset digest', {asset_key: assetKey});
    verified = (await sha256(downloaded.bytes)) === asset.sha256.toLowerCase();
    if (!verified) throw new ReferenceError('INTEGRITY_MISMATCH', 'SHA-256 does not match manifest', {asset_key: assetKey, sha256_verified: false});
  }
  return {
    reference_version, asset_key: assetKey, source_url: downloaded.url,
    content_type: contentType, content: decodeText(downloaded.bytes),
    sha256_verified: verified, retrieved_at: new Date().toISOString()
  };
}

const outputSchema = {
  type: 'object', required: ['reference_version','asset_key','source_url','content_type','content','sha256_verified','retrieved_at'],
  properties: {
    reference_version: {type:'string'}, asset_key:{type:'string'}, source_url:{type:'string'},
    content_type:{type:'string'}, content:{type:'string'}, sha256_verified:{type:['boolean','null']},
    retrieved_at:{type:'string'}
  }
};


const tool = {
  name: TOOL_NAME,
  description: 'Read the live public Lunados Cube reference manifest or one manifest-listed asset by key; verifies SHA-256 where supplied. Read-only, no auth. Never calls G5.',
  outputSchema,
  inputSchema: {
    type: 'object', properties: {
      asset_key: {type: 'string', default: 'manifest', description: 'manifest or exact key from the current manifest.assets object. URLs/paths are forbidden.'}
    }, additionalProperties: false
  }
};


function rpcResult(id, result) { return {jsonrpc:'2.0', id, result}; }
function rpcError(id, code, message) { return {jsonrpc:'2.0', id, error:{code,message}}; }
function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {status, headers:{
    'content-type':'application/json; charset=utf-8',
    'cache-control':'no-store', 'x-content-type-options':'nosniff'
  }});
}
async function readRequest(request) {
  if (Number(request.headers.get('content-length')) > MAX_REQUEST_BYTES)
    throw new ReferenceError('REQUEST_TOO_LARGE','Request body exceeds size limit');
  const bytes = await boundedRead(request, MAX_REQUEST_BYTES);
  try { return JSON.parse(decodeText(bytes)); }
  catch { throw new ReferenceError('INVALID_JSON','Request body must be valid JSON'); }
}

export async function handleMcpRequest(request, fetchImpl = fetch) {
  const url = new URL(request.url);
  if (request.method === 'GET' && url.pathname === '/health')
    return jsonResponse({status:'PUBLIC_REFERENCE_MCP_PROOF', version:SERVER_VERSION, authenticated:false});
  if (url.pathname !== '/mcp') return jsonResponse({error:'NOT_FOUND'},404);
  const origin = request.headers.get('origin');
  if (origin && !['https://chatgpt.com','https://chat.openai.com'].includes(origin))
    return jsonResponse({error:'ORIGIN_FORBIDDEN'},403);
  if (request.method !== 'POST') return new Response(null,{status:405,headers:{'allow':'POST'}});
  if (!(request.headers.get('content-type') || '').toLowerCase().startsWith('application/json'))
    return jsonResponse({error:'CONTENT_TYPE_REQUIRED'},415);
  let call;
  try { call = await readRequest(request); }
  catch (e) {return jsonResponse(rpcError(null,-32700,e.code === 'REQUEST_TOO_LARGE'?'Request too large':'Parse error'), e.code === 'REQUEST_TOO_LARGE'?413:400);}
  if (!call || typeof call !== 'object' || Array.isArray(call) || call.jsonrpc !== '2.0' || typeof call.method !== 'string')
    return jsonResponse(rpcError(call?.id ?? null,-32600,'Invalid Request'),400);
  if (call.method.startsWith('notifications/')) return new Response(null,{status:202});
  if (!Object.hasOwn(call, 'id')) return jsonResponse(rpcError(null,-32600,'Request ID required'),400);
  if (call.method === 'initialize') {
    const incoming = call.params?.protocolVersion;
    const protocolVersion = SUPPORTED_PROTOCOLS.has(incoming) ? incoming : DEFAULT_PROTOCOL;
    return jsonResponse(rpcResult(call.id, {
      protocolVersion, capabilities:{tools:{listChanged:false}},
      serverInfo:{name:'lunados-cube-public-reference',version:SERVER_VERSION},
      instructions:'Public, read-only documentary reference. No G5 access, validation, execution, admission or authority.'
    }));
  }
  if (call.method === 'ping') return jsonResponse(rpcResult(call.id,{}));
  if (call.method === 'tools/list') return jsonResponse(rpcResult(call.id,{tools:[tool]}));
  if (call.method === 'tools/call') {
    if (call.params?.name !== TOOL_NAME) return jsonResponse(rpcError(call.id,-32602,'Unknown tool'));
    const args = call.params?.arguments ?? {};
    if (!args || typeof args !== 'object' || Array.isArray(args) ||
        Object.keys(args).some(k=>k!=='asset_key'))
      return jsonResponse(rpcError(call.id,-32602,'Invalid tool arguments'));
    try {
      const value = await readPublicReference(args.asset_key ?? 'manifest', fetchImpl);
      const content = [{type:'text',text:JSON.stringify(value)}];
      return jsonResponse(rpcResult(call.id,{content,structuredContent:value,isError:false}));
    } catch (error) {
      const err = error instanceof ReferenceError ? error : new ReferenceError('INTERNAL_ERROR','Unexpected reference reader error');
      const data = {code:err.code,message:err.message, ...err.details};
      return jsonResponse(rpcResult(call.id,{isError:true,content:[{type:'text',text:JSON.stringify(data)}],structuredContent:data}));
    }
  }
  return jsonResponse(rpcError(call.id,-32601,'Method not found'));
}

export default {async fetch(request) {return handleMcpRequest(request);}};
