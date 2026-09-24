import { chromium } from 'playwright';
import fs from 'node:fs';
import assert from 'node:assert';

const BASE=process.env.SEEKVERA_AUDIT_BASE||'http://127.0.0.1:4173';
const nav=fs.readFileSync('navigation.js','utf8');
const lm=nav.match(/const WORLD_LANGS=\[([^\]]+)\]/s);
assert(lm,'WORLD_LANGS missing');
const langs=[...lm[1].matchAll(/'([^']+)'/g)].map(m=>m[1]);
const routes=['marketplace.html','travel.html','tourism.html','property.html','cars-auto.html','jobs.html','shopping.html','restaurants-food.html','local-services.html','import-export.html','shipping-logistics.html','business-software.html','software.html','web-hosting.html','solar.html','education.html','health.html','money-insurance.html','entertainment.html','media.html','games.html','connectivity.html','wifi.html','deal-agent.html','everyday.html','scan.html','post-ad.html','seller-plans.html','hub.html','app.html'];
const browser=await chromium.launch({headless:true});
try{
  const context=await browser.newContext({locale:'en-US',geolocation:{latitude:9.0765,longitude:7.3986},permissions:['geolocation']});
  await context.addInitScript(()=>{
    localStorage.setItem('seekvera_country','WW');
    localStorage.setItem('seekvera_lang','nl');
    localStorage.setItem('seekvera_currency','PHP');
    localStorage.setItem('seekvera_country_explicit','1');
    localStorage.removeItem('seekvera_locale_source');
  });
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  if(BASE.startsWith('http://127.0.0.1')){
    await page.route('**/api/ui-translate',async route=>{
      let body={};try{body=route.request().postDataJSON()||{}}catch{}
      const strings=Array.isArray(body.strings)?body.strings:[];
      await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,translations:strings})});
    });
  }
  await page.goto(BASE+'/index.html?r15audit='+Date.now(),{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&document.querySelector('.sv-controls select#country'),null,{timeout:15000});
  await page.waitForTimeout(250);
  const snap=()=>page.evaluate(()=>{const s=SEEKVERA_LOCALE_R15.state();return {country:s.country,language:s.language,currency:s.currency,docLang:document.documentElement.lang,dir:document.documentElement.dir,applying:document.documentElement.classList.contains('sv-r15-applying')}});
  let s=await snap();
  assert.deepEqual([s.country,s.language,s.currency],['WW','en','USD'],'old inconsistent Worldwide state was not healed');
  const data=await page.evaluate(()=>({profiles:SEEKVERA_LOCALE_R15.profiles,lp:SEEKVERA_LOCALE_R15.languagePrimary,cp:SEEKVERA_LOCALE_R15.currencyPrimary}));

  let countryCount=0;
  for(const [cc,p] of Object.entries(data.profiles)){
    await page.evaluate(v=>SEEKVERA_LOCALE_R15.setCountry(v),cc);
    s=await snap();
    assert.deepEqual([s.country,s.language,s.currency],[cc,p.language,p.currency],cc+' country sync');
    assert.equal(s.docLang,p.language,cc+' html language');
    assert.equal(s.dir,['ar','fa','ur','he','ps','dv'].includes(p.language)?'rtl':'ltr',cc+' direction');
    countryCount++;
  }
  assert.equal(countryCount,248);

  for(const lg of langs){
    await page.evaluate(v=>SEEKVERA_LOCALE_R15.setLanguage(v),lg);
    s=await snap();
    const cc=data.lp[lg];
    assert(cc,lg+' canonical country missing');
    assert.deepEqual([s.country,s.language,s.currency],[cc,lg,data.profiles[cc].currency],lg+' language sync');
  }
  assert.equal(langs.length,98);

  let currencyCount=0;
  for(const [cur,cc] of Object.entries(data.cp)){
    await page.evaluate(v=>SEEKVERA_LOCALE_R15.setCurrency(v),cur);
    s=await snap();
    assert.deepEqual([s.country,s.language,s.currency],[cc,data.profiles[cc].language,cur],cur+' currency sync');
    currencyCount++;
  }
  assert(currencyCount>=150);

  // Exact user examples and screenshot regressions.
  await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('WW'));
  assert.deepEqual((await snap()),{country:'WW',language:'en',currency:'USD',docLang:'en',dir:'ltr',applying:true});
  await page.waitForTimeout(100);
  s=await snap();assert.deepEqual([s.country,s.language,s.currency],['WW','en','USD']);
  await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('hi'));s=await snap();assert.deepEqual([s.country,s.language,s.currency],['IN','hi','INR']);
  await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCurrency('USD'));s=await snap();assert.deepEqual([s.country,s.language,s.currency],['US','en','USD']);
  await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('PH'));await page.waitForTimeout(100);s=await snap();assert.deepEqual([s.country,s.language,s.currency],['PH','fil','PHP']);
  await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('nl'));await page.waitForTimeout(100);s=await snap();assert.deepEqual([s.country,s.language,s.currency],['NL','nl','EUR']);
  await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('SA'));await page.waitForTimeout(100);s=await snap();assert.deepEqual([s.country,s.language,s.currency],['SA','ar','SAR']);

  // Actual UI select changes, not only API calls.
  await page.selectOption('.sv-controls select#lang','hi');await page.waitForTimeout(90);s=await snap();assert.deepEqual([s.country,s.language,s.currency],['IN','hi','INR']);
  await page.selectOption('.sv-controls select#currency','USD');await page.waitForTimeout(90);s=await snap();assert.deepEqual([s.country,s.language,s.currency],['US','en','USD']);
  await page.selectOption('.sv-controls select#country','SA');await page.waitForTimeout(90);s=await snap();assert.deepEqual([s.country,s.language,s.currency],['SA','ar','SAR']);

  // One second stability check: no country/language/currency oscillation.
  const stable=[];
  for(let i=0;i<12;i++){await page.waitForTimeout(85);const q=await snap();stable.push([q.country,q.language,q.currency,q.docLang,q.dir].join('|'))}
  assert.equal(new Set(stable).size,1,'locale state oscillated/shook after selection');
  assert.equal((await snap()).applying,false,'atomic applying state did not settle');

  // Reload persistence must remain coherent.
  await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('nl'));
  await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>SEEKVERA_LOCALE_R15?.state?.());await page.waitForTimeout(140);
  s=await snap();assert.deepEqual([s.country,s.language,s.currency],['NL','nl','EUR']);

  // Home location/map is explicit-permission only.
  await page.goto(BASE+'/index.html?r15map='+Date.now(),{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>SEEKVERA_LOCALE_R15?.location&&document.querySelector('#nearMe'));
  await page.click('#nearMe');
  await page.waitForSelector('#svNearMap',{state:'visible',timeout:5000});
  assert((await page.getAttribute('#svNearMap','href')).includes('google.com/maps/search'));

  // Every core department must load R15 and receive coherent state changes.
  for(const route of routes){
    const response=await page.goto(BASE+'/'+route+'?r15dept='+Date.now(),{waitUntil:'domcontentloaded',timeout:30000});
    assert(response&&response.status()===200,route+' HTTP');
    await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15,null,{timeout:10000});
    await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('SA'));await page.waitForTimeout(70);
    let q=await page.evaluate(()=>[localStorage.getItem('seekvera_country'),localStorage.getItem('seekvera_lang'),localStorage.getItem('seekvera_currency'),document.documentElement.lang,document.documentElement.dir]);
    assert.deepEqual(q,['SA','ar','SAR','ar','rtl'],route+' Arabic sync');
    await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCurrency('USD'));await page.waitForTimeout(50);
    q=await page.evaluate(()=>[localStorage.getItem('seekvera_country'),localStorage.getItem('seekvera_lang'),localStorage.getItem('seekvera_currency'),document.documentElement.lang]);
    assert.deepEqual(q,['US','en','USD','en'],route+' USD sync');
  }

  // Critical regression: marketplace input#country is a search filter, not locale control.
  await page.goto(BASE+'/marketplace.html?r15collision='+Date.now(),{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>SEEKVERA_LOCALE_R15);
  await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('SA'));
  await page.fill('input#country','Nigeria');
  await page.locator('input#country').dispatchEvent('change');await page.waitForTimeout(70);
  const collision=await page.evaluate(()=>[document.querySelector('input#country').value,localStorage.getItem('seekvera_country'),localStorage.getItem('seekvera_lang'),localStorage.getItem('seekvera_currency')]);
  assert.deepEqual(collision,['Nigeria','SA','ar','SAR']);

  if(errors.length)throw new Error('Page errors: '+errors.join(' | '));
  console.log('R15 BROWSER PASS:',countryCount,'countries;',langs.length,'languages;',currencyCount,'currencies;',routes.length,'departments; stable reload; map; collision isolation');
  await context.close();
}finally{
  await browser.close();
}
