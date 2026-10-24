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

