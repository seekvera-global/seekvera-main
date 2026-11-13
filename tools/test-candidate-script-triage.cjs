const assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const path=require('node:path');
const script=path.join(__dirname,'audit-candidate-scripts.cjs');
const worker=process.env.WORKER_VALIDATOR_SOURCE||path.join(__dirname,'..','worker.js');
const packs={
 ar:{'SV-YYYYMMDD-XXXXXXXX':'SV-YYYYMMDD-XXXXXXXXX'},
 pa:{'Pop colorful balloons.':'रंगीन बैलून फूटो'},
 el:{'2026-09-26 · R74':'26-09-2026 · R74'},
 hi:{'SEEKVERA finder':'SEEKVERA Finder'},
 am:{'Open QR →':'QR →'}
};
const result=spawnSync(process.execPath,[script],{input:JSON.stringify(packs),encoding:'utf8',env:{...process.env,WORKER_VALIDATOR_SOURCE:worker}});
assert.equal(result.status,0,result.stderr);
const out=JSON.parse(result.stdout);
assert.equal(out.ar.categoryCounts.reserved_identifier_mutation,1);
assert.equal(out.pa.categoryCounts.wrong_or_unverified_script,1);
assert.equal(out.el.categoryCounts.date_version_format_review,1);
assert.equal(out.hi.categoryCounts.case_or_punctuation_only_review,1);
assert.equal(out.am.categoryCounts.latin_only_or_mixed_without_target_script,1);
for(const code of Object.keys(packs)) assert.equal(out[code].count,1);
console.log('PASS: candidate warning triage classifies mutated identifiers, wrong scripts, date formatting, case-only labels and incomplete Latin values without suppressing warnings.');
