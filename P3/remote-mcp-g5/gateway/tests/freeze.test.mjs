import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/index.mjs',import.meta.url),'utf8');
const pkg=JSON.parse(readFileSync(new URL('../package.json',import.meta.url),'utf8'));
const config=JSON.parse(readFileSync(new URL('../wrangler.jsonc',import.meta.url),'utf8'));
test('G5 patched SDK 2.4.0 handler uses fetch',()=>{
  assert.equal(pkg.dependencies['@modelcontextprotocol/server'],'2.4.0');
  assert.equal(pkg.dependencies.zod,'4.6.7');
  assert.match(src,/await handler\.fetch\(forward\)/);
  assert.doesNotMatch(src,/await handler\(forward,env,ctx\)/);
});
test('G5 private CORE binding and bearer enforced before MCP handler',()=>{
  assert.equal(config.services[0].binding,'CORE');
  assert.equal(config.services[0].service,'aiaeao-cube-g5-core');
  assert.match(src,/MCP_BEARER_TOKEN/);
  assert.ok(src.indexOf('equalSecret(')<src.indexOf('createMcpHandler('));
});
test('G5 exposes only health and authenticated MCP endpoints',()=>{
  assert.match(src,/url\.pathname === '\/health'/);
  assert.match(src,/url\.pathname !== '\/mcp'/);
  assert.match(src,/request\.method !== 'POST'/);
});
test('G5 R5 registers ten tools and leaves room above the 2 MiB plan limit',()=>{
  const names=[...src.matchAll(/add\('([a-z_]+)'/g)].map(m=>m[1]);
  assert.deepEqual(names,['cube_get_capabilities','cube_prepare_print','cube_check_print','cube_render_svg','cube_read_reference',
    'cube_validate','cube_discover_surface','cube_plan_source','cube_plan_views','cube_plan_check']);
  assert.match(src,/MAX_RESPONSE_BYTES = 2 \* 1024 \* 1024 \+ 64 \* 1024/);
  assert.match(src,/version:'0\.2\.0-proof'/);
});
