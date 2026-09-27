import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const base=process.env.SEEKVERA_CERT_BASE||'http://127.0.0.1:8765/';
const b=await chromium.launch({headless:true});
const p=await b.newPage({locale:'en-US'});
const errors=[];
p.on('pageerror',e=>errors.push(String(e.message||e)));
await p.goto(base+(base.includes('?')?'&':'?')+'r96cert='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForFunction(()=>window.SEEKVERA_I18N_R32&&window.SEEKVERA_LOCALE_R15,{timeout:25000});
const cases=[['LB','ar'],['FR','fr'],['DE','de'],['TR','tr'],['CN','zh'],['IN','hi']];
const englishLeak=['Find it faster. Compare it better.','Popular categories','Request anything','Live marketplace'];
for(const [cc,ll] of cases){
  await p.selectOption('#country',cc);
  await p.waitForFunction(([c,l])=>document.querySelector('#country')?.value===c&&document.documentElement.lang===l&&document.documentElement.dataset.seekveraI18nReady===l,[cc,ll],{timeout:25000});
  await p.waitForTimeout(700);
  const out=await p.evaluate(()=>({
    lang:document.documentElement.lang,
    country:document.querySelector('#country')?.value,
    hero:document.querySelector('.r5-hero h1')?.textContent.trim()||'',
    popular:document.querySelector('#categories h2')?.textContent.trim()||'',
    request:document.querySelector('#request h2')?.textContent.trim()||'',
    cats:[...document.querySelectorAll('#categories .r5-tile-body b')].slice(0,10).map(x=>x.textContent.trim())
  }));
  assert.equal(out.country,cc); assert.equal(out.lang,ll);
  assert.ok(out.hero&&out.popular&&out.request,'critical localized labels empty');
  assert.ok(out.cats.length>=6&&out.cats.every(Boolean),'category titles empty');
  const joined=[out.hero,out.popular,out.request,...out.cats].join(' | ');
  for(const x of englishLeak) assert.ok(!joined.includes(x),`${cc}/${ll} leaked English: ${x} :: ${joined}`);
  console.log('LOCALE_PASS',cc,ll,out.popular,out.cats.slice(0,3).join('/'));
}
assert.ok(!errors.some(x=>/SyntaxError|ReferenceError/.test(x)),'page runtime errors: '+errors.join(' | '));
await b.close();
