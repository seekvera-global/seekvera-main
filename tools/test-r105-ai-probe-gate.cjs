const fs = require('node:fs');
const assert = require('node:assert/strict');

const workflow = fs.readFileSync('.github/workflows/r105-final-release.yml', 'utf8');
const worker = fs.readFileSync('worker.js', 'utf8');
const stepStart = workflow.indexOf('      - name: Certify live production health and optional AI');
assert(stepStart >= 0, 'R105 production certification step missing');
const stepEnd = workflow.indexOf('\n      - name:', stepStart + 1);
const step = workflow.slice(stepStart, stepEnd < 0 ? workflow.length : stepEnd);

assert.match(workflow, /run_live_ai_probes:[\s\S]*?default: false/, 'live AI probe input must default to false');
assert.match(step, /RUN_LIVE_AI_PROBES:[\s\S]*?workflow_dispatch[\s\S]*?run_live_ai_probes/, 'live AI env must require manual opt-in');

const guard = step.indexOf('if [[ "${RUN_LIVE_AI_PROBES:-false}" == "true" ]]; then');
const countryCall = step.indexOf('change country to Iceland');
const countryCheck = step.indexOf('countryAction.code=="IS"');
const countrySkipped = step.indexOf('COUNTRY_INTENT_AI_PROBE_SKIPPED_BY_POLICY');
assert(guard >= 0, 'country intent probe must have an explicit opt-in guard');
assert(countryCall > guard, 'country intent /api/ai request must be inside the opt-in guard');
assert(countryCheck > guard, 'country intent assertion must be inside the opt-in guard');
assert(countrySkipped > guard, 'opt-out path must explicitly report the country probe was skipped');

const safetyCall = step.indexOf('I want to buy a gun');
const ruleBlock = worker.indexOf("if(q.d==='BLOCK')return j(request");
const aiLanguage = worker.indexOf('const detected=await detectedLanguage');
assert(safetyCall >= 0 && safetyCall < guard, 'deterministic safety probe should remain available without AI opt-in');
assert(ruleBlock >= 0 && aiLanguage > ruleBlock, 'prohibited request must be blocked before language detection/model calls');

console.log('PASS: R105 health and deterministic safety remain quota-neutral; country-intent and chat model probes require explicit opt-in');
