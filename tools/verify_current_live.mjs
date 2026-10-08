import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const B='https://seekveraglobal.com';
const result={startedAt:new Date().toISOString(),passed:[],failures:[],finalApproval:false,remainingChecks:['Complete current static and dynamic source coverage in all supported languages','Review linguistic accuracy, including partially English translations','Human microphone and audible speaker checks on Android, iPhone/iPad and desktop'],scope:'Recorded source phrases, country state and pack integrity; excludes linguistic accuracy and physical device audio'};
const watchdog=setTimeout(()=>{console.error('CERTIFICATION_TIMEOUT');process.exit(1)},20*60*1000);
async function bounded(label,fn,ms=20000){let timer;try{return await Promise.race([fn(),new Promise((_,reject)=>timer=setTimeout(()=>reject(Error('TIMEOUT '+label)),ms))])}finally{clearTimeout(timer)}}
const browser=await chromium.launch({headless:true,...(process.env.HTTPS_PROXY?{proxy:{server:process.env.HTTPS_PROXY}}:{})});
try {
 const ctx=await browser.newContext({ignoreHTTPSErrors:true,serviceWorkers:'block',locale:'en-US',viewport:{width:390,height:844}});
 await ctx.route('**/*',r=>{const u=new URL(r.request().url());if(['seekveraglobal.com','www.seekveraglobal.com','seekvera-main.seekvera-global.workers.dev'].includes(u.hostname))return r.continue();return r.abort()});
 const dynamic=[];
 await ctx.route('**/api/ui-translate',r=>{dynamic.push(r.request().postData());return r.fulfill({status:503,contentType:'application/json',body:'{"ok":false}'})});
 if(process.env.LIVE_OVERRIDES==='1')for(const file of ['global-ui.js','locale-r15.js','r22-category-lock.js','i18n-ui.js'])await ctx.route('**/'+file+'*',r=>r.fulfill({status:200,contentType:'application/javascript',body:fs.readFileSync(file,'utf8')}));
 const page=await ctx.newPage();await page.goto(B+'/?cert='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,null,{timeout:30000});
 const health=await page.evaluate(async()=>{const r=await fetch('/api/health');return {status:r.status,data:await r.json()}});assert.equal(health.status,200);assert(health.data.ok);result.health=health.data;result.candidateOverrides=process.env.LIVE_OVERRIDES==='1';
 const manifest=await page.evaluate(async()=>await (await fetch('/i18n-r32/manifest.json')).json());
 const source=await page.evaluate(async()=>await (await fetch('/i18n-r32-source.json')).json());
 const packs={};
 for(let i=0;i<manifest.languages.length;i+=7){const batch=await bounded('packs',()=>page.evaluate(async langs=>await Promise.all(langs.map(async l=>{const r=await fetch('/i18n-r32/'+l+'.json');return {l,status:r.status,d:await r.json()}})),manifest.languages.slice(i,i+7)),60000);for(const {l,status,d} of batch){assert.equal(status,200,l);assert.equal(d.sourceHash,manifest.sourceHash,l);assert.equal(d.count,source.count,l);assert(source.strings.every(s=>String(d.translations[s]||'').trim()),l);packs[l]=d.translations}}
 result.passed.push('98 live packs match source and contain every recorded key');console.log('LIVE_PACKS_PASS',manifest.languages.length,source.count);
 const profiles=await bounded('profiles',()=>page.evaluate(()=>SEEKVERA_LOCALE_R15.profiles));
 for(const [cc,pr] of Object.entries(profiles)){const got=await bounded('country '+cc,()=>page.evaluate(cc=>{SEEKVERA_LOCALE_R15.setCountry(cc);return {country:document.querySelector('#country').value,language:document.querySelector('#lang').value,currency:document.querySelector('#currency').value,html:document.documentElement.lang}},cc));assert.equal(got.country,cc);assert.equal(got.language,pr.language,cc);assert.equal(got.currency,pr.currency,cc);assert.equal(got.html,pr.language,cc)}
 result.countries=Object.keys(profiles).length;result.passed.push('atomic country/language/currency state');console.log('LIVE_COUNTRIES_PASS',result.countries);
 const hrefs=await page.evaluate(()=>[...new Set([...document.querySelectorAll('#categories .r5-tile')].map(a=>a.getAttribute('href')).filter(Boolean))]);assert.equal(hrefs.length,31);
 const allPaths=[...new Set(['/',...hrefs.map(h=>new URL(h,B).pathname)])];const paths=process.env.CERT_PATHS?process.env.CERT_PATHS.split(','):allPaths;result.routes=hrefs.length;result.paths=paths.length;
 const english=source.strings.filter(s=>s.length>=12&&(s.match(/[A-Za-z][A-Za-z'’+-]{2,}/g)||[]).length>=2&&!s.includes('SEEKVERA')&&!/https?:\/\/|@/.test(s));
 let combos=0;
 for(const path of paths){
  await page.goto(B+path+'?cert='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,null,{timeout:20000});
  await bounded(path+' en',()=>page.evaluate(async()=>{SEEKVERA_LOCALE_R15.setLanguage('en');await SEEKVERA_I18N_R32.apply()}));await page.waitForTimeout(150);
  const baseline=await page.evaluate(()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;const a=[];while(n=w.nextNode()){if(!n.parentElement.closest('script,style,.ai-msg'))a.push(n.nodeValue.replace(/\s+/g,' ').trim())}return a});const candidates=english.filter(s=>baseline.includes(s));
  for(const l of (process.env.CERT_LANGS?process.env.CERT_LANGS.split(','):manifest.languages)){
   await bounded(path+' '+l,()=>page.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N_R32.loadPack(l);await SEEKVERA_I18N_R32.apply()},l));await page.waitForTimeout(450);combos++;
   assert.equal(await page.evaluate(()=>document.documentElement.lang),l);
   if(l!=='en'){const body=await page.evaluate(()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;const a=[];while(n=w.nextNode()){if(!n.parentElement.closest('script,style,.ai-msg'))a.push(n.nodeValue.replace(/\s+/g,' ').trim())}return a});const leaks=candidates.filter(s=>packs[l]?.[s]&&packs[l][s]!==s&&!packs[l][s].includes(s)&&body.includes(s));if(leaks.length)result.failures.push({path,l,leaks:leaks.slice(0,5)})}
  }
  console.log('LIVE_SECTION_CHECKED',path,'combinations',combos,'failures',result.failures.length);
 }
 result.combinations=combos;result.dynamicTranslationRequests=dynamic.length;result.dynamicSources=[...new Set(dynamic.flatMap(s=>{try{return JSON.parse(s).strings||[]}catch{return []}}))];
 if(!result.failures.length)result.passed.push('No tested exact whole-node source phrases remained English on the tested section/language combinations');
 result.finishedAt=new Date().toISOString();fs.mkdirSync('docs',{recursive:true});fs.writeFileSync('docs/current-live-certification.json',JSON.stringify(result,null,2));console.log('CERTIFICATION_RESULT',JSON.stringify({release:result.health.release,countries:result.countries,routes:result.routes,paths:result.paths,combinations:combos,failures:result.failures.length,dynamicTranslationRequests:dynamic.length}));
 assert.equal(result.failures.length,0,'untranslated visible phrases');
} catch(e){result.error=String(e);fs.mkdirSync('docs',{recursive:true});fs.writeFileSync('docs/current-live-certification.json',JSON.stringify(result,null,2));throw e}
finally{clearTimeout(watchdog);await browser.close()}
