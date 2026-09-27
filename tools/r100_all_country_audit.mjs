import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const base='https://seekveraglobal.com/';
const b=await chromium.launch({headless:true});
const p=await b.newPage({locale:'en-US'});
const pageErrors=[];
p.on('pageerror',e=>pageErrors.push(String(e.message||e)));
await p.goto(base+'?r100=all-countries-'+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,{timeout:30000});
const profiles=await p.evaluate(()=>window.SEEKVERA_LOCALE_R15.profiles);
const entries=Object.entries(profiles);
assert.ok(entries.length>=240,`expected >=240 country/territory profiles, got ${entries.length}`);
const englishLeaks=['Find it faster. Compare it better.','Popular categories','Request anything','Live marketplace','Ask AI anything','Search what you need'];
const failures=[];
let n=0;
for(const [cc,profile] of entries){
  try{
    await p.evaluate(cc=>window.SEEKVERA_LOCALE_R15.setCountry(cc),cc);
    await p.waitForFunction(([cc,lang,cur])=>{
      const s=window.SEEKVERA_LOCALE_R15?.state?.();
      return s?.country===cc&&s?.language===lang&&s?.currency===cur&&document.documentElement.lang===lang&&document.querySelector('#country')?.value===cc&&document.querySelector('#currency')?.value===cur;
    },[cc,profile.language,profile.currency],{timeout:12000});
    await p.waitForFunction(lang=>document.documentElement.dataset.seekveraI18nReady===lang,profile.language,{timeout:12000});
    await p.waitForTimeout(45);
    const out=await p.evaluate(()=>({
      lang:document.documentElement.lang,
      dir:document.documentElement.dir,
      country:document.querySelector('#country')?.value,
      currency:document.querySelector('#currency')?.value,
      hero:document.querySelector('.r5-hero h1')?.textContent?.trim()||'',
      popular:document.querySelector('#categories h2')?.textContent?.trim()||'',
      request:document.querySelector('#request h2')?.textContent?.trim()||'',
      categoryTitles:[...document.querySelectorAll('#categories .r5-tile-body b')].slice(0,12).map(x=>x.textContent.trim())
    }));
    assert.equal(out.lang,profile.language);assert.equal(out.country,cc);assert.equal(out.currency,profile.currency);
    assert.ok(out.hero&&out.popular&&out.request,'empty critical UI label');
    assert.ok(out.categoryTitles.length>=8&&out.categoryTitles.every(Boolean),'empty category title');
    if(profile.language!=='en'){
      const joined=[out.hero,out.popular,out.request,...out.categoryTitles].join(' | ');
      for(const leak of englishLeaks)assert.ok(!joined.includes(leak),`English leak: ${leak}`);
    }
    if(['ar','fa','ur','he','ps','dv'].includes(profile.language))assert.equal(out.dir,'rtl');
    n++;if(n%25===0)console.log('COUNTRY_AUDIT_PROGRESS',n,'/',entries.length,cc,profile.language,profile.currency);
  }catch(e){failures.push({cc,profile,error:String(e.message||e)});console.log('COUNTRY_AUDIT_FAIL',cc,profile.language,profile.currency,String(e.message||e));}
}
console.log('COUNTRY_AUDIT_TOTAL',entries.length,'PASS',entries.length-failures.length,'FAIL',failures.length);
if(failures.length)console.log('COUNTRY_AUDIT_FAILURES',JSON.stringify(failures.slice(0,50)));
assert.equal(failures.length,0,'all-country audit failures');
assert.ok(!pageErrors.some(x=>/SyntaxError|ReferenceError/.test(x)),'runtime errors: '+pageErrors.join(' | '));
await b.close();
console.log('R100_ALL_COUNTRIES_PASS');
