/** Standalone, independently testable security helpers (no npm dependencies). */
export async function withinLimit(request, max) {
  const hdr = request.headers.get('content-length');
  if (hdr && Number(hdr) > max) return null;
  if (!request.body) return new Uint8Array(0);
  const reader = request.body.getReader();
  const chunks = []; let count = 0;
  try {
    for (;;) {
      const {done,value} = await reader.read();
      if (done) break;
      count += value.byteLength;
      if (count > max) { await reader.cancel(); return null; }
      chunks.push(value);
    }
  } finally {reader.releaseLock();}
  const out = new Uint8Array(count); let pos = 0;
  for (const chunk of chunks) {out.set(chunk,pos);pos+=chunk.length;}
  return out;
}

export function equalSecret(value, expected) {
  // Both strings are server-configured or request-supplied; compare the digest
  // in constant-time at the byte level without leaking secret length.
  const a = new TextEncoder().encode(value); const b = new TextEncoder().encode(expected);
  let result = a.length ^ b.length;
  for (let i=0; i<Math.max(a.length,b.length);i++) result |= (a[i] ?? 0) ^ (b[i] ?? 0);
  return result === 0;
}

// Optional beta credentials are separate Worker Secrets. Empty slots have no effect.
export const BETA_TOKEN_KEYS = Object.freeze(Array.from(
  {length: 12}, (_, index) => `MCP_BETA_TOKEN_${String(index + 1).padStart(2, '0')}`));

export function bearerDecision(authorization, env) {
  const developer = env?.MCP_BEARER_TOKEN;
  if (typeof developer !== 'string' || developer.length < 32) return '503';

  const supplied = typeof authorization === 'string' ? authorization : '';
  let accepted = equalSecret(supplied, `Bearer ${developer}`);
  const beta = BETA_TOKEN_KEYS.map(key => env[key]);
  for (let index = 0; index < beta.length; index++) {
    const value = beta[index];
    if (typeof value !== 'string' || value.length < 32) continue;
    // A duplicated beta credential cannot be revoked one slot at a time.
    const duplicated = beta.some((other, otherIndex) =>
      otherIndex !== index && typeof other === 'string' && equalSecret(value, other));
    const matches = equalSecret(supplied, `Bearer ${value}`);
    accepted = (matches && !duplicated) || accepted;
  }
  return accepted ? 'pass' : '401';
}

export function requestAccessDecision(authorization, origin, env) {
  const bearer = bearerDecision(authorization, env);
  if (bearer !== 'pass') return bearer;
  if (origin && (!env.MCP_ALLOWED_ORIGIN || origin !== env.MCP_ALLOWED_ORIGIN)) return '403';
  return 'pass';
}

