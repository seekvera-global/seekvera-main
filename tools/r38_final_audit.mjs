import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const B=process.env.SEEKVERA_BASE||'https://seekveraglobal.com';
const browser=await chromium.launch({headless:true});
const ctx=await browser.newContext({viewport:{width:390,height:844},locale:'en-US',serviceWorkers:'block'});
const page=await ctx.newPage();
const pageErrors=[]; page.on('pageerror',e=>pageErrors.push(String(e)));
await page.route('**/api/ui-translate',r=>r.abort());
await page.route('https://text.pollinations.ai/**',r=>r.abort());
await page.goto(B+'/?r38='+Date.now(),{waitUntil:'domcontentloaded',timeout:45000});
await page.waitForFunction(()=>window.SEEKVERA_I18N_R32&&window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_R14_CATEGORIES&&window.SEEKVERA_R22_CATEGORY_LOCK,{timeout:20000});
const manifest=await (await ctx.request.get(B+'/i18n-r32/manifest.json?v='+Date.now())).json();
const source=await (await ctx.request.get(B+'/i18n-r32-source.json?v='+Date.now())).json();
assert.equal(manifest.packs,98);assert.equal(manifest.languages.length,98);assert(source.count>=900);
const meta=await page.evaluate(()=>({profiles:SEEKVERA_LOCALE_R15.profiles,langs:Object.keys(SEEKVERA_R14_CATEGORIES.data)}));
assert.equal(Object.keys(meta.profiles).length,248);assert.equal(meta.langs.length,98);
const packs={};
for(let i=0;i<manifest.languages.length;i+=16){
  await Promise.all(manifest.languages.slice(i,i+16).map(async l=>{const r=await ctx.request.get(B+'/i18n-r32/'+l+'.json?v='+manifest.sourceHash,{timeout:20000});assert.equal(r.status(),200,l+' pack');const d=await r.json();assert.equal(d.count,source.count,l+' count');assert.equal(Object.keys(d.translations).length,source.count,l+' map');packs[l]=d.translations}));
}
// Screenshot regression: Iraq must be Arabic/IQD/RTL, including late marketplace content.
await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('IQ'));
await page.evaluate(async()=>{await SEEKVERA_I18N_R32.loadPack('ar');SEEKVERA_I18N_R32.schedule(0);SEEKVERA_R22_CATEGORY_LOCK.lock()});
await page.waitForFunction(()=>document.documentElement.dataset.seekveraPackReady==='ar'&&document.documentElement.dataset.seekveraI18nReady==='ar'&&document.documentElement.dir==='rtl',{timeout:12000});
const leaks=['No approved live marketplace listings are available right now','SEEKVERA does not generate fake listings','Find, compare, choose — worldwide','Popular categories','Live marketplace','Request anything'];
async function checkIraq(label){
 const x=await page.evaluate(()=>({body:document.body.innerText,cc:country.value,l:lang.value,c:currency.value,cards:document.querySelectorAll('#categories .r5-tile').length,overflow:document.documentElement.scrollWidth-innerWidth,mic:!!document.querySelector('#aiChatMic'),speaker:!!document.querySelector('#aiChatSpeaker')}));
 assert.deepEqual([x.cc,x.l,x.c],['IQ','ar','IQD'],label);for(const q of leaks)assert(!x.body.includes(q),label+' English leak '+q);assert.equal(x.cards,31,label+' categories');assert(x.overflow<=4,label+' overflow');assert(x.mic&&x.speaker,label+' voice controls');
}
await page.waitForTimeout(400);await checkIraq('0.4s');await page.waitForTimeout(2200);await checkIraq('2.6s');await page.waitForTimeout(3000);await checkIraq('5.6s');
// Every country profile: one action must atomically set country/language/currency.
const badCountries=[];
for(const [cc,pr] of Object.entries(meta.profiles)){await page.evaluate(cc=>SEEKVERA_LOCALE_R15.setCountry(cc),cc);const g=await page.evaluate(()=>({cc:country.value,l:lang.value,c:currency.value}));if(g.cc!==cc||g.l!==pr.language||g.c!==pr.currency)badCountries.push({cc,pr,g})}
assert.equal(badCountries.length,0,'country mapping '+JSON.stringify(badCountries.slice(0,8)));
// Every supported language on the live homepage, with remote translators blocked.
const critical=['No approved live marketplace listings are available right now.','SEEKVERA does not generate fake listings.','Find, compare, choose — worldwide.','Popular categories','Live marketplace','Request anything'];
for(const l of manifest.languages){
 await page.evaluate(l=>SEEKVERA_LOCALE_R15.setLanguage(l),l);
 await page.evaluate(async l=>{await SEEKVERA_I18N_R32.loadPack(l);SEEKVERA_I18N_R32.schedule(0);SEEKVERA_R22_CATEGORY_LOCK.lock()},l);
 if(l!=='en')await page.waitForFunction(l=>document.documentElement.dataset.seekveraPackReady===l&&document.documentElement.dataset.seekveraI18nReady===l,l,{timeout:10000});
 await page.waitForTimeout(45);
 const x=await page.evaluate(()=>({body:document.body.innerText,l:lang.value,tiles:[...document.querySelectorAll('#categories .r5-tile-body b')].slice(0,31).map(n=>n.textContent.trim()),small:[...document.querySelectorAll('#categories .r5-tile-body small')].filter(n=>!n.hidden).map(n=>n.textContent.trim()),overflow:document.documentElement.scrollWidth-innerWidth}));
 assert.equal(x.l,l,l+' selected');assert(x.overflow<=4,l+' overflow');assert.equal(x.tiles.length,31,l+' categories');
 const expected=await page.evaluate(l=>SEEKVERA_R14_CATEGORIES.data[l],l);assert.deepEqual(x.tiles,expected,l+' category labels');
 if(l!=='en'){assert.equal(x.small.length,0,l+' English category descriptions');for(const q of critical){const tr=packs[l][q];if(tr&&tr!==q)assert(!x.body.includes(q),l+' English leak '+q)}}
}
// All 31 category destinations must load. Then deep-check Arabic on every route.
await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('ar'));await page.evaluate(async()=>{await SEEKVERA_I18N_R32.loadPack('ar');SEEKVERA_I18N_R32.schedule(0);SEEKVERA_R22_CATEGORY_LOCK.lock()});await page.waitForTimeout(100);
const hrefs=await page.evaluate(()=>[...new Set([...document.querySelectorAll('#categories .r5-tile')].map(a=>a.getAttribute('href')).filter(Boolean))]);assert.equal(hrefs.length,31);
const routeBad=[];
for(let i=0;i<hrefs.length;i+=10){await Promise.all(hrefs.slice(i,i+10).map(async h=>{try{const r=await ctx.request.get(new URL(h,B).href,{timeout:15000});const t=await r.text();if(r.status()>=400||t.length<180)routeBad.push({h,status:r.status(),len:t.length})}catch(e){routeBad.push({h,error:String(e)})}}))}
assert.equal(routeBad.length,0,'routes '+JSON.stringify(routeBad));
const arPack=packs.ar;const arCheck=source.strings.filter(s=>s.length>=10&&arPack[s]&&arPack[s]!==s&&!/^SEEKVERA\b/.test(s));const deepBad=[];
for(const h of hrefs){const p=await ctx.newPage();const errs=[];p.on('pageerror',x=>errs.push(String(x)));await p.route('**/api/ui-translate',r=>r.abort());await p.route('https://text.pollinations.ai/**',r=>r.abort());try{await p.goto(new URL(h,B).href+'?r38deep='+Date.now(),{waitUntil:'domcontentloaded',timeout:45000});await p.waitForFunction(()=>window.SEEKVERA_I18N_R32&&window.SEEKVERA_LOCALE_R15,{timeout:15000});await p.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('ar'));await p.evaluate(async()=>{await SEEKVERA_I18N_R32.loadPack('ar');SEEKVERA_I18N_R32.schedule(0)});await p.waitForFunction(()=>document.documentElement.dataset.seekveraI18nReady==='ar',{timeout:10000});await p.waitForTimeout(100);const body=await p.evaluate(()=>document.body.innerText);const q=arCheck.filter(s=>body.includes(s)).slice(0,8);if(q.length||errs.length)deepBad.push({h,leaks:q,errors:errs.slice(0,3)})}catch(e){deepBad.push({h,error:String(e)})}finally{await p.close()}}
assert.equal(deepBad.length,0,'deep Arabic '+JSON.stringify(deepBad.slice(0,5)));assert.equal(pageErrors.length,0,'page errors '+pageErrors.join(' | '));
console.log('R38 UI PASS',JSON.stringify({countries:248,languages:98,categories:31,sourceStrings:source.count,iraq:'Arabic/IQD/no-English',remoteTranslation:'blocked'}));
// AI smoke in 7 representative languages/scripts.
const aiCases=[['IQ','ar','مرحبا'],['US','en','Hello'],['FR','fr','Bonjour'],['DE','de','Hallo'],['CN','zh','你好'],['IN','hi','नमस्ते'],['TR','tr','Merhaba']];const aiBad=[];
for(const [cc,l,msg] of aiCases){try{const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),12000);const r=await fetch(B+'/api/ai',{method:'POST',headers:{'content-type':'application/json','Origin':B},body:JSON.stringify({message:msg,country:cc,language:l,fast:true}),signal:ctl.signal});clearTimeout(to);const d=await r.json();const text=String(d?.response||'').trim();if(!r.ok||!d?.ok||text.length<2||text==='…')aiBad.push({cc,l,status:r.status,body:d})}catch(e){aiBad.push({cc,l,error:String(e)})}}
assert.equal(aiBad.length,0,'AI '+JSON.stringify(aiBad));console.log('R38 AI PASS',JSON.stringify({cases:aiCases.length}));
await browser.close();
