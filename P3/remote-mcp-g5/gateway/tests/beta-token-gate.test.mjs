import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {BETA_TOKEN_KEYS,requestAccessDecision} from '../src/security.mjs';

const contract=JSON.parse(readFileSync(new URL('./beta-token-contract.json',import.meta.url),'utf8'));
assert.equal(contract.format,'aiaeao.cube.g5-beta-token-contract/1');
assert.equal(BETA_TOKEN_KEYS.length,12);

function synthetic(label) {
  if (label === null) return null;
  if (label === 'SHORT') return 'x'.repeat(8);
  return createHash('sha256').update(`beta-gate-fixture:${label}`).digest('hex');
}

function testEnvironment(example) {
  const env={};
  if (example.developer !== null) env.MCP_BEARER_TOKEN=synthetic(example.developer);
  for (const [slot,label] of Object.entries(example.beta_slots)) {
    const key=`MCP_BETA_TOKEN_${slot}`;
    assert.ok(BETA_TOKEN_KEYS.includes(key),key);
    env[key]=synthetic(label);
  }
  return env;
}

test('fixed MILE-019 beta-token contract',async t=>{
  assert.equal(contract.cases.length,9);
  assert.equal(contract.cases.flatMap(example=>example.checks).length,36);
  for (const example of contract.cases) {
    await t.test(example.id,async()=>{
      const env=testEnvironment(example);
      for (const check of example.checks) {
        const value=synthetic(check.credential);
        const authorization=value === null ? '' : `Bearer ${value}`;
        assert.equal(requestAccessDecision(authorization,check.origin ?? null,env),check.expected,
          `${example.id}: ${check.credential ?? 'none'} decision`);
      }
    });
  }
});
