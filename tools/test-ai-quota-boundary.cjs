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
  [new Error('daily_free_ai_limit'), true],
  [new Error('daily free AI limit'), true],
  [new AggregateError([new Error('capacity busy'), new Error('daily_free_ai_limit')], 'all models failed'), true],
  [new Error('HTTP 429 Too Many Requests'), true],
  [new Error('provider rate limit exceeded'), true],
  [new AggregateError([new Error('capacity busy'), new Error('HTTP 429 Too Many Requests')], 'all models failed'), true],
  [new Error('capacity temporarily exceeded'), false],
  [new Error('model timeout'), false]
];
for (const [error, expected] of cases) assert.equal(context.quotaLimited(error), expected);

const quotaGuard = worker.indexOf('if(quotaBlocked||uncertainFailure||aiRaceTimedOut)return null;');
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


const audioWorkflow = fs.readFileSync('.github/workflows/r123-production-cert.yml', 'utf8');
assert.match(audioWorkflow, /run_live_audio_probes:[\s\S]*?default: false/);
assert.ok(audioWorkflow.includes("github.event.inputs.run_live_audio_probes == 'true'"));
assert.ok(audioWorkflow.includes("if: ${{ github.event_name == 'workflow_dispatch' && github.event.inputs.run_live_audio_probes == 'true' }}"),
  'automatic deploys must skip live audio/chat probes');
assert.ok(!audioWorkflow.includes('for attempt in range(3)'),
  'live audio/chat probes must not retry quota or rate-limit responses');
assert.ok(audioWorkflow.includes("str(d.get('model','')).startswith('@cf/')"),
  'live chat certification must require an actual Workers AI model');

function extractFunction(source, signature) {
  const start = source.indexOf(signature);
  assert.notEqual(start, -1, signature + ' missing');
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < source.length; i++) {
    if (source[i] === '{') depth++;
    else if (source[i] === '}' && --depth === 0) return source.slice(start, i + 1);
  }
  assert.fail(signature + ' is incomplete');
}

const baseWorker = fs.readFileSync('worker.js', 'utf8');
const translationQuota = extractFunction(baseWorker, 'function translationQuotaReason(');
const translationContext = {};
vm.createContext(translationContext);
vm.runInContext(translationQuota + '\nthis.translationQuotaReason = translationQuotaReason;', translationContext);
for (const [message, expected] of [
  ['daily_free_ai_limit', 'daily_free_ai_limit'],
  ['daily free AI limit', 'daily_free_ai_limit'],
  ['Error 3036: daily free allocation exhausted', 'daily_free_ai_limit'],
  ['Google HTTP 429 Too Many Requests', 'provider_rate_limited'],
  ['provider rate limit exceeded', 'provider_rate_limited'],
  [new AggregateError([new Error('capacity busy'), new Error('daily_free_ai_limit')], 'all models failed'), 'daily_free_ai_limit'],
  ['capacity temporarily exceeded', '']
]) assert.equal(translationContext.translationQuotaReason(message), expected);

const translationStart = baseWorker.indexOf("if(u.pathname==='/api/ui-translate')");
const translationEnd = baseWorker.indexOf("if(u.pathname==='/api/transcribe')", translationStart);
const translationHandler = baseWorker.slice(translationStart, translationEnd);
assert.ok(translationHandler.includes('quotaReason=translationQuotaReason(e)'), 'UI translation must classify quota and rate-limit errors');
assert.ok(translationHandler.includes('if(quotaReason)return j('), 'UI translation must stop before trying the next model on quota/rate-limit errors');

const translationBuilder = fs.readFileSync('tools/build_current_locale_delta.py', 'utf8');
assert.ok(translationBuilder.includes('def quota_or_rate_limit(detail):'), 'translation builder must classify quota/rate-limit responses');
assert.ok(translationBuilder.includes('if quota_or_rate_limit(detail):raise RuntimeError(detail) from e'), 'translation builder must stop immediately on quota/rate-limit errors');
const stopIndex = translationBuilder.indexOf('if quota_or_rate_limit(detail):raise RuntimeError(detail) from e');
const splitIndex = translationBuilder.indexOf("print('SPLIT_RETRY'");
assert.ok(stopIndex >= 0 && splitIndex > stopIndex, 'translation builder must stop before splitting/retrying a quota/rate-limit failure');

const baseAi = extractFunction(baseWorker, 'async function ai(');
const baseSafety = extractFunction(baseWorker, 'async function safety(');
assert.ok(
  baseAi.includes('daily[_\\s-]*free[_\\s-]*(?:ai[_\\s-]*)?(?:limit|allocation)') &&
  baseAi.includes('\\b429\\b') &&
  baseAi.includes('rate.?limit'),
  'base-worker AI helper must identify daily quota and rate-limit errors'
);
assert.ok(baseAi.indexOf('AI quota/rate limit reached') < baseAi.indexOf('https://text.pollinations.ai/'),
  'base-worker moderation must stop before external fallback on quota/rate-limit errors');

let externalCalls = 0;
const baseContext = {
  PRIMARY: '@cf/google/gemma-4-26b-a4b-it',
  FALLBACK: '@cf/zai-org/glm-4.7-flash',
  LIGHT: '@cf/qwen/qwen3-30b-a3b-fp8',
  FASTCHAT: '@cf/meta/llama-3.1-8b-instruct-fast',
  clean: (v, n = 400) => String(v ?? '').replace(/[\u0000-\u001F\u007F]/g, ' ').trim().slice(0, n),
  out: x => typeof x === 'string' ? x.trim() : '',
  rules: () => ({ d: 'CLEAR', reason: 'safe' }),
  console: { warn() {} },
  AbortSignal: { timeout: () => ({}) },
  fetch: async () => {
    externalCalls++;
    return { ok: true, status: 200, text: async () => 'external fallback response' };
  }
};
vm.createContext(baseContext);
vm.runInContext(baseAi + '\n' + baseSafety + '\nthis.ai = ai; this.safety = safety;', baseContext);

(async () => {
  for (const message of [
    'Error 3036: daily free allocation exhausted',
    'daily_free_ai_limit',
    'Google HTTP 429 Too Many Requests',
    'provider rate limit exceeded'
  ]) {
    externalCalls = 0;
    const result = await baseContext.safety(
      { AI: { run: async () => { throw new Error(message); } } },
      'ordinary lawful hotel request',
      'request'
    );
    assert.equal(result.allowed, false, message);
    assert.equal(result.reviewRequired, true, message);
    assert.equal(result.reason, 'moderation_unavailable_hold', message);
    assert.equal(externalCalls, 0, 'external provider must not run after ' + message);
  }

  externalCalls = 0;
  const nonQuotaFallback = await baseContext.ai(
    { AI: { run: async () => { throw new Error('capacity temporarily exceeded'); } } },
    [{ role: 'user', content: 'hello' }]
  );
  assert.equal(nonQuotaFallback.model, 'pollinations-private-backup');
  assert.equal(externalCalls, 1, 'non-quota availability fallback should remain available');


  const structured = extractFunction(worker, 'async function runStructured(');
  function makeR76Context() {
    let nextTimer = 1;
    const timers = new Map();
    const context = {
      FAST: 'fast',
      PRIMARY: 'primary',
      FALLBACK: 'fallback',
      ROUTES: { marketplace: 'marketplace.html' },
      CATS: ['general'],
      quotaLimited: error => {
        const nested = Array.isArray(error?.errors) ? error.errors.map(item => item?.message || item) : [];
        return /3036|daily[_\\s-]*free[_\\s-]*(?:ai[_\\s-]*)?(?:limit|allocation)|\\b429\\b|rate.?limit|too many requests/i.test([String(error?.message ?? error ?? ''), ...nested].join(' '));
      },
      clean: (v, n = 3500) => String(v ?? '').replace(/[\u0000-\u001F\u007F]/g, ' ').trim().slice(0, n),
      modelText: value => typeof value === 'string' ? value : String(value?.response ?? value?.text ?? ''),
      parseJSON: value => { try { return JSON.parse(value); } catch { return null; } },
      messageLanguage: () => 'en',
      languageSafeHistory: () => '',
      metaConversation: () => false,
      conversationOnly: () => false,
      directCategoryIntent: () => 'general',
      category: () => 'general',
      actionState: () => ({ isAction: false, cc: null, ll: null }),
      arabicDialect: () => '',
      routeReplyFor: () => null,
      guardedReply: value => String(value ?? ''),
      translationRequest: () => false,
      languageCode: () => 'en',
      replyMatchesLanguage: () => true,
      speechLocaleFor: () => 'en',
      AbortController,
      fetch: async () => ({
        ok: true,
        text: async () => JSON.stringify({ reply: 'External fallback response', languageCode: 'en', category: 'general' })
      }),
      setTimeout: (fn, ms) => {
        const id = nextTimer++;
        const delay = ms >= 3300 ? 100 : ms >= 3000 ? 10 : 20;
        timers.set(id, global.setTimeout(fn, delay));
        return id;
      },
      clearTimeout: id => {
        const timer = timers.get(id);
        if (timer) global.clearTimeout(timer);
        timers.delete(id);
      }
    };
    vm.createContext(context);
    vm.runInContext(structured + '\nthis.runStructured = runStructured;', context);
    return context;
  }

  let lateQuotaFallbackCalls = 0;
  const lateQuotaContext = makeR76Context();
  lateQuotaContext.fetch = async () => {
    lateQuotaFallbackCalls++;
    return { ok: true, text: async () => JSON.stringify({ reply: 'Should not be used', languageCode: 'en', category: 'general' }) };
  };
  const lateQuotaResult = await lateQuotaContext.runStructured(
    { url: 'https://seekveraglobal.com' },
    { AI: { run: () => new Promise((_, reject) => global.setTimeout(() => reject(new Error('HTTP 429 Too Many Requests')), 25)) } },
    null,
    { message: 'hello', language: 'en', history: [] },
    'hello'
  );
  assert.equal(lateQuotaResult, null, 'a timed-out AI request must fail closed');
  assert.equal(lateQuotaFallbackCalls, 0, 'external fallback must not start while a late 429 is still possible');

  let capacityFallbackCalls = 0;
  const capacityContext = makeR76Context();
  capacityContext.fetch = async () => {
    capacityFallbackCalls++;
    return { ok: true, text: async () => JSON.stringify({ reply: 'External fallback response', languageCode: 'en', category: 'general' }) };
  };
  const capacityResult = await capacityContext.runStructured(
    { url: 'https://seekveraglobal.com' },
    { AI: { run: async () => { throw new Error('capacity temporarily exceeded'); } } },
    null,
    { message: 'hello', language: 'en', history: [] },
    'hello'
  );
  assert.equal(capacityFallbackCalls, 1, 'ordinary capacity failures should retain the existing non-quota fallback');
  assert.equal(capacityResult?.model, 'pollinations-private-conversation-fallback');

  console.log('R76_AND_BASE_SAFETY_QUOTA_BOUNDARY_PASS');
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
