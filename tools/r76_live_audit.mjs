import {chromium} from 'playwright';
import assert from 'node:assert/strict';

const B='https://seekveraglobal.com';
const VER='20260926-r76-complete-global-final';
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function postAI(message,extra={}){
  let last;
  for(let attempt=1;attempt<=3;attempt++){
    try{
      const c=new AbortController();const t=setTimeout(()=>c.abort(),25000);
      const r=await fetch(B+'/api/ai',{method:'POST',headers:{'content-type':'application/json','user-agent':'SEEKVERA-R76-AUDIT'},body:JSON.stringify({message,country:'Worldwide',language:'auto',scope:'worldwide',fast:true,...extra}),signal:c.signal});
      clearTimeout(t);const d=await r.json();if(!r.ok)throw Error('HTTP '+r.status+' '+JSON.stringify(d).slice(0,300));return d;
    }catch(e){last=e;await pause(attempt*1200)}
  }
  throw last;
}

// API understanding + routing + app controls. These cases intentionally mix dialects and scripts.
const languageCases=[
  ['بدي وظيفة مبيعات بفرنسا','ar','jobs'],
  ['شو فيك تساعدني اليوم؟','ar','general'],
  ['I need a sales job in Germany','en','jobs'],
  ['Je cherche un emploi commercial en Allemagne','fr','jobs'],
  ['Türkiye’de satış işi arıyorum','tr','jobs'],
  ['मुझे जर्मनी में सेल्स की नौकरी चाहिए','hi','jobs'],
  ['我想在德国找销售工作','zh','jobs'],
  ['Мне нужна работа в продажах в Германии','ru','jobs'],
  ['Busco trabajo de ventas en Alemania','es','jobs'],
  ['Ich suche eine Stelle im Vertrieb in Deutschland','de','jobs'],
  ['أريد شقة للإيجار في باريس','ar','property'],
];
for(const [q,lang,cat] of languageCases){
  const d=await postAI(q);console.log('AI_CASE',lang,cat,JSON.stringify(d).slice(0,650));
  assert(d?.ok&&String(d.response||'').trim(),[q,d]);
  assert.equal(d.category,cat,'category '+q);
  assert(String(d.language||'').toLowerCase().startsWith(lang),'language '+q+' => '+JSON.stringify(d));
}
for(const [q,cc,ll] of [
  ['حطني تركيا','TR',null],['غيّر الأب على لبنان','LB',null],['change the app to France','FR',null],['حوّلني ورلد وايد','WW',null],['غير لغة التطبيق للتركي',null,'tr']
]){
  const d=await postAI(q);console.log('APP_ACTION',q,JSON.stringify(d).slice(0,650));assert(String(d?.response||'').trim(),q);
  if(cc)assert.equal(d?.countryAction?.code,cc,q);
  if(ll)assert.equal(d?.languageAction?.code,ll,q);
}
const searchNotControl=await postAI('بدي فندق بفرنسا');assert(!searchNotControl.countryAction,searchNotControl);assert(['travel','tourism'].includes(searchNotControl.category),searchNotControl);
console.log('R76_API_LANGUAGE_ACTION_PASS');

const browser=await chromium.launch({headless:true});
const ctx=await browser.newContext({viewport:{width:390,height:844},locale:'ar-LB',serviceWorkers:'block',userAgent:'Mozilla/5.0 (Linux; Android 11; SM-A225F) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'});
ctx.setDefaultTimeout(15000);

// R76 promises complete static packs. During UI localization verification, never let a slow
// cloud/public translation fallback hide a missing static string. Fail fast and report it.
const translationFallbacks=[];
await ctx.route('**/api/ui-translate',async route=>{
  let strings=[];try{strings=route.request().postDataJSON()?.strings||[]}catch{}
  translationFallbacks.push({page:route.request().frame()?.url?.()||'',strings:strings.slice(0,8)});
  await route.fulfill({status:503,contentType:'application/json',body:'{"ok":false,"audit":"static-pack-only"}'});
});
await ctx.route('https://text.pollinations.ai/**',async route=>route.fulfill({status:503,contentType:'text/plain',body:'R76 static-pack-only audit'}));

const p=await ctx.newPage();const errors=[];p.on('pageerror',e=>errors.push(String(e)));
await p.goto(B+'/?r76audit='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32&&window.SEEKVERA_R31&&window.SEEKVERA_CHAT,{timeout:30000});
const manifest=await (await ctx.request.get(B+'/i18n-r32/manifest.json?v='+Date.now())).json();
const source=await (await ctx.request.get(B+'/i18n-r32-source.json?v='+Date.now())).json();
assert.equal(manifest.version,VER);assert.equal(manifest.packs,98);assert.equal(manifest.languages.length,98);assert(source.count>=1045,source.count);
const packs={};for(let i=0;i<manifest.languages.length;i+=14){
  await Promise.all(manifest.languages.slice(i,i+14).map(async l=>{const r=await ctx.request.get(B+'/i18n-r32/'+l+'.json?v='+manifest.sourceHash,{timeout:25000});assert.equal(r.status(),200,l);const d=await r.json();assert.equal(d.count,source.count,l);assert.equal(d.sourceHash,manifest.sourceHash,l);packs[l]=d.translations}));
  console.log('R76_PACK_PROGRESS',Math.min(i+14,manifest.languages.length),'/',manifest.languages.length);
}
console.log('R76_98_LIVE_PACKS_PASS',source.count,manifest.sourceHash);

// Every configured country must atomically set country, language, currency and html language.
const matrix=await p.evaluate(async()=>{const bad=[];for(const [cc,pr] of Object.entries(SEEKVERA_LOCALE_R15.profiles)){SEEKVERA_LOCALE_R15.setCountry(cc);await new Promise(r=>setTimeout(r,3));const g={cc:country?.value,l:lang?.value,c:currency?.value,html:document.documentElement.lang,dir:document.documentElement.dir};if(g.cc!==cc||g.l!==pr.language||g.c!==pr.currency||g.html!==pr.language)bad.push({cc,pr,g})}return{n:Object.keys(SEEKVERA_LOCALE_R15.profiles).length,bad}});
assert(matrix.n>=248,matrix.n);assert.equal(matrix.bad.length,0,'country sync '+JSON.stringify(matrix.bad.slice(0,8)));
console.log('R76_COUNTRY_MATRIX_PASS',matrix.n);

// Discover every category route. Validate every language on the real homepage, then
// distribute all 98 languages across all real section paths while keeping major-script
// anchors on every section. Static-pack-only mode keeps this exhaustive audit fast and
// makes missing localizations visible instead of waiting on network translation fallbacks.
const hrefs=await p.evaluate(()=>[...new Set([...document.querySelectorAll('#categories .r5-tile')].map(a=>a.getAttribute('href')).filter(Boolean))]);
assert(hrefs.length>=31,'category routes '+hrefs.length);const paths=[...new Set(hrefs.map(h=>new URL(h,B).pathname))];
const candidateEnglish=source.strings.filter(s=>s.length>=12&&(s.match(/[A-Za-z][A-Za-z'’+-]{2,}/g)||[]).length>=2&&!s.includes('SEEKVERA')&&!/https?:\/\/|@/.test(s));
let combinations=0;const leakBad=[];

// Every one of the 98 packs must actually apply in the live UI at least once.
await p.goto(B+'/?r76alllangs='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,{timeout:25000});
await p.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('en'));await pause(40);
const homeEnglish=await p.locator('body').innerText();const homePresent=candidateEnglish.filter(s=>homeEnglish.includes(s));
for(let li=0;li<manifest.languages.length;li++){
  const l=manifest.languages[li];
  await p.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N_R32.loadPack(l);await SEEKVERA_I18N_R32.apply()},l);
  const state=await p.evaluate(()=>({lang:document.documentElement.lang,dir:document.documentElement.dir}));
  assert.equal(state.lang,l,'live language application '+l);combinations++;
  if(l!=='en'){
    const body=await p.locator('body').innerText();
    const leaks=homePresent.filter(s=>packs[l]?.[s]&&packs[l][s]!==s&&body.includes(s)).slice(0,6);
    if(leaks.length)leakBad.push({path:'/',l,leaks});
  }
  if((li+1)%14===0||li===manifest.languages.length-1)console.log('R76_HOME_LANGUAGE_PROGRESS',li+1,'/',manifest.languages.length,'fallbacks',translationFallbacks.length);
}

// Every section is tested in English plus major scripts. Remaining languages are
// deterministically distributed so each of the 98 languages is tested on a section.
const anchors=['en','ar','fr','tr','hi','zh','de'];
for(let pi=0;pi<paths.length;pi++){
  const path=paths[pi];
  await p.goto(B+path+'?r76section='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
  await p.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,{timeout:25000});
  await p.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('en'));await pause(25);
  const english=await p.locator('body').innerText();const present=candidateEnglish.filter(s=>english.includes(s));
  const assigned=manifest.languages.filter((_,li)=>li%paths.length===pi);
  const testLangs=[...new Set([...anchors,...assigned])];
  for(const l of testLangs){
    await p.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N_R32.loadPack(l);await SEEKVERA_I18N_R32.apply()},l);
    combinations++;if(l==='en')continue;
    const body=await p.locator('body').innerText();
    const leaks=present.filter(s=>packs[l]?.[s]&&packs[l][s]!==s&&body.includes(s)).slice(0,6);
    if(leaks.length){leakBad.push({path,l,leaks});break}
  }
  console.log('R76_SECTION_PROGRESS',pi+1,'/',paths.length,path,'langs',testLangs.length,'fallbacks',translationFallbacks.length);
  if(leakBad.length>6)break;
}
assert.equal(leakBad.length,0,'English UI leaks '+JSON.stringify(leakBad.slice(0,7)));
assert.equal(translationFallbacks.length,0,'Static pack coverage gaps attempted dynamic translation '+JSON.stringify(translationFallbacks.slice(0,8)));
console.log('R76_SECTION_LANGUAGE_PASS',JSON.stringify({routes:hrefs.length,paths:paths.length,languages:manifest.languages.length,combinations,coverage:'all-languages-and-all-sections-distributed',dynamicFallbacks:0}));

// User message must be visible before navigation, and conversation must survive navigation.
await p.goto(B+'/?r76chat='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForFunction(()=>window.SEEKVERA_R31&&window.SEEKVERA_CHAT&&document.querySelector('#aiChatForm'),{timeout:30000});
await p.evaluate(()=>{localStorage.removeItem('seekvera_ai_chat_v1');SEEKVERA_LOCALE_R15.setCountry('LB')});
await p.fill('#aiChatInput','بدي وظيفة مبيعات بفرنسا');const before=p.url(),t=Date.now();await p.locator('#aiChatForm').evaluate(f=>f.requestSubmit());
await p.waitForFunction(()=>{const x=[...document.querySelectorAll('#aiMessages .ai-msg.bot')].at(-1);return x&&!x.classList.contains('thinking')&&/[\u0600-\u06ff]/u.test(x.textContent||'')},{timeout:18000});
const replyMs=Date.now()-t;assert.equal(p.url(),before,'route happened before reply was visible');
await p.waitForFunction(()=>location.pathname==='/jobs'||location.pathname==='/jobs.html',{timeout:12000});
const saved=await p.evaluate(()=>localStorage.getItem('seekvera_ai_chat_v1')||'');assert(saved.includes('بدي وظيفة مبيعات بفرنسا'),'chat not saved');
await p.goto(B+'/?r76restore='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});await p.waitForFunction(()=>window.SEEKVERA_CHAT&&document.querySelector('#aiMessages'),{timeout:30000});await pause(250);assert((await p.locator('#aiMessages').innerText()).includes('بدي وظيفة مبيعات بفرنسا'),'chat not restored');

// Explicit app command must answer first and then apply the setting.
await p.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('LB'));await p.fill('#aiChatInput','حطني تركيا');const n=await p.locator('#aiMessages .ai-msg.bot').count();const u0=p.url();await p.locator('#aiChatForm').evaluate(f=>f.requestSubmit());await p.waitForFunction(n=>document.querySelectorAll('#aiMessages .ai-msg.bot').length>n,n,{timeout:8000});assert.equal(p.url(),u0,'control navigated before reply');await p.waitForFunction(()=>document.querySelector('#country')?.value==='TR',{timeout:8000});

// Voice output path: microphone-origin reply must invoke TTS; voice input source must prefer server auto-ASR.
const spoken=await p.evaluate(async()=>{window.__r76spoken=0;try{speechSynthesis.speak=()=>{window.__r76spoken++}}catch{};SEEKVERA_VOICE_AI?.markVoiceReply?.();window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:'مرحبا، كيف فيني ساعدك؟',language:'ar'}}));await new Promise(r=>setTimeout(r,450));return window.__r76spoken});
assert(spoken>0,'voice reply did not invoke TTS');
const voiceText=await (await ctx.request.get(B+'/voice-ai.js?v='+Date.now())).text();assert(voiceText.includes('serverVoice(targetId,activeButton,true)'),'server ASR is not first');assert(voiceText.includes("language:'auto'"),'server ASR is not auto-language');
assert.equal(errors.length,0,'page errors '+errors.slice(0,12).join(' | '));
console.log('R76_FINAL_LIVE_PASS',JSON.stringify({countries:matrix.n,languages:manifest.languages.length,categoryRoutes:hrefs.length,sectionPaths:paths.length,languageSectionCombinations:combinations,sourceStrings:source.count,replyMs,chatSaved:true,chatRestored:true,appControl:true,ttsCalls:spoken,dynamicTranslationFallbacks:translationFallbacks.length}));
await browser.close();
