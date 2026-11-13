'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const worker = fs.readFileSync('worker-r76.js', 'utf8');
const start = worker.indexOf('function quotaLimited(error){');
assert.notEqual(start, -1, 'quotaLimited helper must exist');
let depth = 0, end = -1;
for (let i = worker.indexOf('{', start); i < worker.length; i++) {
  if (worker[i] === '{') depth++;
  else if (worker[i] === '}' && --depth === 0) { end = i + 1; break; }
}
assert.notEqual(end, -1, 'quotaLimited helper must be complete');
const context = {};
vm.createContext(context);
vm.runInContext(worker.slice(start, end) + '\nthis.quotaLimited = quotaLimited;', context);

const cases = [
  [new Error('Error 3036: daily free allocation exhausted'), true],
  [new Error('HTTP 429 Too Many Requests'), true],
  [new Error('provider rate limit exceeded'), true],
  [new AggregateError([new Error('capacity busy'), new Error('HTTP 429 Too Many Requests')], 'all models failed'), true],
  [new Error('capacity temporarily exceeded'), false],
  [new Error('model timeout'), false]
];
for (const [error, expected] of cases) assert.equal(context.quotaLimited(error), expected);

const quotaGuard = worker.indexOf('if(quotaBlocked)return null;');
const pollinationsFallback = worker.indexOf('https://text.pollinations.ai/');
assert.ok(quotaGuard >= 0 && pollinationsFallback > quotaGuard,
  'quota/rate-limit failures must stop before the external conversational fallback');
assert.ok(worker.includes('if(quotaLimited(e))quotaBlocked=true;'),
  'individual model quota errors must be recorded');

const workflow = fs.readFileSync('.github/workflows/r105-final-release.yml', 'utf8');
assert.match(workflow, /run_live_ai_probes:[\s\S]*?default: false/);
assert.ok(workflow.includes('RUN_LIVE_AI_PROBES'));
const gateIndex = workflow.indexOf('if [[ "${RUN_LIVE_AI_PROBES:-false}" == "true" ]]');
const chatProbeIndex = workflow.indexOf('Hello, how are you?');
assert.ok(gateIndex >= 0 && chatProbeIndex > gateIndex,
  'automatic deployments must not send live chat probes');

assert.ok(workflow.includes('((.model // "")|startswith("@cf/"))'),
  'manual AI certification must require an actual Workers AI model response');
assert.ok(workflow.includes('AI_PROBES_SKIPPED_BY_POLICY'),
  'automatic deploys must state that live AI probes were skipped');

console.log('R76_QUOTA_BOUNDARY_PASS');
