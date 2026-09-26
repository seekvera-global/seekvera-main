import {chromium} from 'playwright';
import assert from 'node:assert/strict';

const B='https://seekveraglobal.com';
const VER='20260926-r76-complete-global-final';
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const browser=await chromium.launch({headless:true});
const ctx=await browser.newContext({viewport:{width:390,height:844},locale:'ar-LB',serviceWorkers:'block',userAgent:'Mozilla/5.0 (Linux; Android 11; SM-A225F) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'});
ctx.setDefaultTimeout(18000);
const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));

let opened=false,status=0;
for(let i=1;i<=5;i++){
 const r=await page.goto(B+'/?r76resilient='+Date.now()+'-'+i,{waitUntil:'domcontentloaded',timeout:60000}).catch(()=>null);
 status=r?.status()||0;if(status>0&&status<400){opened=true;break}await pause(800*i);
}
assert(opened,'custom domain did not open '+status);
await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32&&window.SEEKVERA_R31&&window.SEEKVERA_CHAT&&window.SEEKVERA_R24_CONTROLLER,{timeout:30000});
console.log('R76_STATIC_CUSTOM_DOMAIN_PASS',status);

// Record Worker state without making quota exhaustion block static/browser certification.
const health=await ctx.request.get(B+'/api/health?r76resilient='+Date.now(),{timeout:20000}).catch(()=>null);
const apiStatus=health?.status()||0;let apiRuntime='';
if(apiStatus===200){try{apiRuntime=(await health.json()).r76Runtime||''}catch{}}
console.log(apiStatus===200?'R76_API_CURRENTLY_HEALTHY':'R76_API_CURRENTLY_DEGRADED',apiStatus,apiRuntime);

const manifestResp=await ctx.request.get(B+'/i18n-r32/manifest.json?v='+Date.now(),{timeout:25000});
assert.equal(manifestResp.status(),200);const manifest=await manifestResp.json();
const sourceResp=await ctx.request.get(B+'/i18n-r32-source.json?v='+Date.now(),{timeout:25000});
assert.equal(sourceResp.status(),200);const source=await sourceResp.json();
assert.equal(manifest.version,VER);assert.equal(manifest.packs,98);assert.equal(manifest.languages.length,98);assert.equal(source.count,1045);assert.equal(manifest.sourceHash,'b371f2422f8b5416');
const packs={};
for(let i=0;i<98;i+=14){await Promise.all(manifest.languages.slice(i,i+14).map(async l=>{const r=await ctx.request.get(B+'/i18n-r32/'+l+'.json?v='+manifest.sourceHash,{timeout:25000});assert.equal(r.status(),200,l);const d=await r.json();assert.equal(d.count,1045,l);assert.equal(d.sourceHash,manifest.sourceHash,l);packs[l]=d.translations}));}
console.log('R76_98_STATIC_PACKS_PASS',manifest.sourceHash);

const matrix=await page.evaluate(async()=>{const bad=[];for(const [cc,pr] of Object.entries(SEEKVERA_LOCALE_R15.profiles)){SEEKVERA_LOCALE_R15.setCountry(cc);await new Promise(r=>setTimeout(r,2));const g={cc:country?.value,l:lang?.value,c:currency?.value,html:document.documentElement.lang};if(g.cc!==cc||g.l!==pr.language||g.c!==pr.currency||g.html!==pr.language)bad.push({cc,pr,g})}return{n:Object.keys(SEEKVERA_LOCALE_R15.profiles).length,bad}});
assert(matrix.n>=248,matrix.n);assert.equal(matrix.bad.length,0,JSON.stringify(matrix.bad.slice(0,8)));
console.log('R76_COUNTRY_ATOMIC_PASS',matrix.n);

// Complete static packs must localize without calling dynamic translation. Wait for one-time
// bootstrap timers to settle, then validate each language after its own UI update settles.
const uiFallbacks=[];await ctx.route('**/api/ui-translate',async route=>{uiFallbacks.push(route.request().url());await route.fulfill({status:503,contentType:'application/json',body:'{"ok":false}'});});
await page.goto(B+'/?r76alllangs='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,{timeout:25000});
await pause(700);await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('en'));await pause(250);
const candidateEnglish=source.strings.filter(s=>s.length>=12&&(s.match(/[A-Za-z][A-Za-z'’+-]{2,}/g)||[]).length>=2&&!s.includes('SEEKVERA')&&!/https?:\/\/|@/.test(s));
const englishBody=await page.locator('body').innerText();const present=candidateEnglish.filter(s=>englishBody.includes(s));const leaks=[];
for(const l of manifest.languages){
 await page.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N_R32.loadPack(l);await SEEKVERA_I18N_R32.apply()},l);
 await pause(150);
 assert.equal(await page.evaluate(()=>document.documentElement.lang),l,l);
 if(l!=='en'){
  const body=await page.locator('body').innerText();
  const x=present.filter(s=>{const tr=String(packs[l]?.[s]||'');return tr&&tr!==s&&!tr.includes(s)&&body.includes(s)}).slice(0,4);
  if(x.length)leaks.push({l,x});
 }
}
assert.equal(leaks.length,0,'home English leaks '+JSON.stringify(leaks.slice(0,8)));assert.equal(uiFallbacks.length,0,'dynamic translation used');
console.log('R76_98_HOME_LANGUAGES_PASS');

await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('en'));await pause(120);const hrefs=await page.evaluate(()=>[...new Set([...document.querySelectorAll('#categories .r5-tile')].map(a=>a.getAttribute('href')).filter(Boolean))]);assert(hrefs.length>=31,'category routes '+hrefs.length);const paths=[...new Set(hrefs.map(h=>new URL(h,B).pathname))];
for(const path of paths){const r=await page.goto(B+path+'?r76section='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});assert(r&&r.status()<400,path+' '+r?.status());await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,{timeout:25000});await pause(250);for(const l of ['ar','fr','tr','hi','zh','de']){await page.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N_R32.loadPack(l);await SEEKVERA_I18N_R32.apply()},l);await pause(80);const txt=(await page.locator('body').innerText()).trim();assert(txt.length>20,path+' '+l)}}
console.log('R76_ALL_CATEGORY_PAGES_PASS',hrefs.length,paths.length);

// Browser fetch must stay functional even if /api/ai itself is 429.
await page.goto(B+'/?r76fallback='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});await page.waitForFunction(()=>window.SEEKVERA_R24_CONTROLLER&&window.SEEKVERA_R31&&document.querySelector('#aiChatForm'),{timeout:30000});await pause(250);
const fallback=await page.evaluate(async()=>{const r=await fetch('/api/ai',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:'شو فيك تساعدني اليوم؟',country:'Worldwide',language:'auto',fast:true})});let d={};try{d=await r.json()}catch{}return{status:r.status,mode:r.headers.get('x-seekvera-ai-mode'),d}});
assert.equal(fallback.status,200,JSON.stringify(fallback));assert(String(fallback.d?.response||'').trim(),JSON.stringify(fallback));assert(/[\u0600-\u06ff]/u.test(fallback.d.response),JSON.stringify(fallback));
console.log('R76_BROWSER_AI_RESILIENCE_PASS',fallback.mode||fallback.d.model);

// A jobs request must show an Arabic reply before navigation, then route, and persist chat.
await page.evaluate(()=>{localStorage.removeItem('seekvera_ai_chat_v1');SEEKVERA_LOCALE_R15.setCountry('LB')});await pause(160);await page.fill('#aiChatInput','بدي وظيفة مبيعات بفرنسا');const before=page.url(),t=Date.now();await page.locator('#aiChatForm').evaluate(f=>f.requestSubmit());
await page.waitForFunction(()=>{const x=[...document.querySelectorAll('#aiMessages .ai-msg.bot')].at(-1);return x&&!x.classList.contains('thinking')&&/[\u0600-\u06ff]/u.test(x.textContent||'')},{timeout:22000});const replyMs=Date.now()-t;assert.equal(page.url(),before,'navigated before reply');await page.waitForFunction(()=>location.pathname==='/jobs'||location.pathname==='/jobs.html',{timeout:12000});const saved=await page.evaluate(()=>localStorage.getItem('seekvera_ai_chat_v1')||'');assert(saved.includes('بدي وظيفة مبيعات بفرنسا'),'chat not saved');
await page.goto(B+'/?r76restore='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});await page.waitForFunction(()=>window.SEEKVERA_CHAT&&document.querySelector('#aiMessages'),{timeout:30000});await pause(300);assert((await page.locator('#aiMessages').innerText()).includes('بدي وظيفة مبيعات بفرنسا'),'chat not restored');
console.log('R76_CHAT_REPLY_ROUTE_PERSIST_PASS',replyMs);

// Local app control: natural reply first, then country actually changes.
await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('LB'));await pause(120);await page.fill('#aiChatInput','حطني تركيا');const n=await page.locator('#aiMessages .ai-msg.bot').count(),u0=page.url();await page.locator('#aiChatForm').evaluate(f=>f.requestSubmit());await page.waitForFunction(n=>document.querySelectorAll('#aiMessages .ai-msg.bot').length>n,n,{timeout:5000});assert.equal(page.url(),u0);const controlReply=await page.locator('#aiMessages .ai-msg.bot').last().innerText();assert(/[\u0600-\u06ff]/u.test(controlReply),controlReply);await page.waitForFunction(()=>document.querySelector('#country')?.value==='TR',{timeout:5000});
console.log('R76_CONTROL_REPLY_FIRST_PASS',controlReply);

// Voice reply path and server-first/native-fallback configuration.
const spoken=await page.evaluate(async()=>{window.__r76spoken=0;try{speechSynthesis.speak=()=>{window.__r76spoken++}}catch{};SEEKVERA_VOICE_AI?.markVoiceReply?.();window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:'مرحبا، كيف فيني ساعدك؟',language:'ar'}}));await new Promise(r=>setTimeout(r,500));return window.__r76spoken});assert(spoken>0,'TTS not invoked');const voiceResp=await ctx.request.get(B+'/voice-ai.js?v='+Date.now(),{timeout:25000});assert.equal(voiceResp.status(),200);const voice=await voiceResp.text();assert(voice.includes('serverVoice(targetId,activeButton,true)'));assert(voice.includes("language:'auto'"));assert(voice.includes('fallbackNative'));
console.log('R76_VOICE_TTS_AND_NATIVE_FALLBACK_PASS',spoken);

const idx=await (await ctx.request.get(B+'/?r76marker='+Date.now(),{timeout:25000})).text();assert(idx.includes('20260926-r76-complete-global-final'));assert(!idx.includes('r74-ai-failover.js'));assert(!idx.includes('r66-final-controller.js'));
assert.equal(errors.length,0,'page errors '+errors.slice(0,10).join(' | '));
console.log('R76_RESILIENT_LIVE_CERTIFIED',JSON.stringify({apiStatus,countries:matrix.n,languages:manifest.languages.length,categoryRoutes:hrefs.length,sectionPaths:paths.length,replyMs,chatSaved:true,ttsCalls:spoken,browserAi:true}));
await browser.close();
