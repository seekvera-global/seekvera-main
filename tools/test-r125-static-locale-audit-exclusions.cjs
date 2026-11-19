const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('tools/r125_static_locale_section_audit.mjs','utf8');
const start=source.indexOf('  function classifyLeakEvidence(');
const end=source.indexOf('\n  let languageApplications',start);
assert(start>=0&&end>start,'audit classifier source not found');
const context={};vm.createContext(context);
vm.runInContext(source.slice(start,end)+'\nthis.classifyLeakEvidence=classifyLeakEvidence;',context);
const classify=context.classifyLeakEvidence;
const excluded=classify(['AI Deal Agent'],{nodes:[],options:[],elements:[],excluded:[{phrase:'AI Deal Agent',reason:'data-no-translate'}]});
assert.deepEqual(Array.from(excluded.excludedOnly),['AI Deal Agent']);
assert.equal(excluded.unresolved.length,0);
const visible=classify(['Back'],{nodes:[{phrase:'Back',text:'Back'}],options:[],elements:[],excluded:[{phrase:'Back'}]});
assert.deepEqual(Array.from(visible.exact),['Back']);
const partial=classify(['Courier & last mile'],{nodes:[{phrase:'Courier & last mile',text:'I-Courier & last mile'}],options:[],elements:[],excluded:[]});
assert.deepEqual(Array.from(partial.partial),['Courier & last mile']);
const unresolved=classify(['Missing label'],{nodes:[],options:[],elements:[],excluded:[]});
assert.deepEqual(Array.from(unresolved.unresolved),['Missing label']);
console.log('PASS: explicit no-translate/user-content occurrences are separated from real visible leaks');

const navigation=fs.readFileSync('navigation.js','utf8');
const residualStart=navigation.indexOf('async function translateResidualUI(){');
const residualEnd=navigation.indexOf('\nfunction runLocaleEngines',residualStart);
assert(residualStart>=0&&residualEnd>residualStart,'navigation residual-localizer source not found');
const residual=navigation.slice(residualStart,residualEnd);
assert.match(residual,/if\s*\(\s*window\.SEEKVERA_I18N_R32\s*\)\s*return\s*;/,
  'R32 must own visible UI localization and prevent a second pass over already-localized dock/hero text');
console.log('PASS: R32-owned visible UI is not re-translated by the legacy residual fallback');
