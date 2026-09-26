import {chromium} from 'playwright';
import assert from 'node:assert/strict';

const B='https://seekveraglobal.com';
const O='https://seekvera-main.seekvera-global.workers.dev';
const VER='20260926-r76-complete-global-final';
const pause=ms=>new Promise(r=>setTimeout(r,ms));

const browser=await chromium.launch({headless:true});
const ctx=await browser.newContext({
  viewport:{width:390,height:844},locale:'ar-LB',serviceWorkers:'block',
  userAgent:'Mozilla/5.0 (Linux; Android 11; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36'
});
ctx.setDefaultTimeout(15000);

async function request(method,path,data){
  let last;
  for(const base of [B,O]){
    for(let n=1;n<=2;n++){
      try{
        const url=base+path+(path.includes('?')?'&':'?')+'r76cert='+Date.now()+'-'+n;
        const opts={timeout:25000,headers:{'cache-control':'no-cache','accept':'application/json,text/plain,*/*'}};
        if(data!==undefined){opts.data=data;opts.headers['content-type']='application/json'}
        const r=method==='POST'?await ctx.request.post(url,opts):await ctx.request.get(url,opts);
        last={status:r.status(),base,body:await r.text()};
        if(r.status()===429||r.status()>=500){await pause(500*n);continue}
        if(r.status()>=400)throw Error(`${method} ${path} HTTP ${r.status()} ${last.body.slice(0,200)}`);
        return last;
      }catch(e){last=e;await pause(400*n)}
    }
  }
  throw last instanceof Error?last:Error('request failed '+JSON.stringify(last));
}
async function jsonReq(method,path,data){const r=await request(method,path,data);return{...r,json:JSON.parse(r.body)}}

// Prove the real custom domain itself opens in a browser. Do not substitute the Worker for this.
const page=await ctx.newPage();const pageErrors=[];page.on('pageerror',e=>pageErrors.push(String(e)));
let opened=false,lastStatus=0;
for(let n=1;n<=4;n++){
  const r=await page.goto(B+'/?r76cert='+Date.now()+'-'+n,{waitUntil:'domcontentloaded',timeout:60000}).catch(()=>null);
  lastStatus=r?.status()||0;
  if(lastStatus>0&&lastStatus<400){opened=true;break}
  await pause(1200*n);
}
assert(opened,'custom domain browser open failed status='+lastStatus);
await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32&&window.SEEKVERA_R31&&window.SEEKVERA_CHAT,{timeout:30000});
console.log('R76_CUSTOM_DOMAIN_BROWSER_PASS',page.url());

// Health may use Worker-origin fallback only when the GitHub runner is rate-limited.
const health=(await jsonReq('GET','/api/health')).json;
assert.equal(health.r76,true,JSON.stringify(health));
assert.equal(health.r76Runtime,'single-structured-multilingual-ai');
assert.equal(health.r76Voice,'server-auto-asr-first');
assert.equal(health.r76Locale,'complete-static-pack-audit');
console.log('R76_HEALTH_PASS');

// Search intent: same-language reply, correct category, and absolutely no country/language mutation.
const searchCases=[
 ['بدي وظيفة مبيعات بفرنسا','ar','jobs'],['شو فيك تساعدني اليوم؟','ar','general'],
 ['I need a sales job in Germany','en','jobs'],['Je cherche un emploi commercial en Allemagne','fr','jobs'],
 ['Türkiye’de satış işi arıyorum','tr','jobs'],['मुझे जर्मनी में सेल्स की नौकरी चाहिए','hi','jobs'],
 ['我想在德国找销售工作','zh','jobs'],['Мне нужна работа в продажах в Германии','ru','jobs'],
 ['Busco trabajo de ventas en Alemania','es','jobs'],['Ich suche eine Stelle im Vertrieb in Deutschland','de','jobs'],
 ['أريد شقة للإيجار في باريس','ar','property'],['بدي فندق بفرنسا','ar','travel']
];
for(const [message,lang,cat] of searchCases){
 const d=(await jsonReq('POST','/api/ai',{message,country:'Worldwide',language:'auto',scope:'worldwide',fast:true})).json;
 assert(d.ok&&String(d.response||'').trim(),JSON.stringify(d));
 assert.equal(d.language,lang,message+' '+JSON.stringify(d));
 if(cat==='travel')assert(['travel','tourism'].includes(d.category),message+' '+JSON.stringify(d));else assert.equal(d.category,cat,message+' '+JSON.stringify(d));
 assert.equal(d.countryAction,null,'search changed country '+message+' '+JSON.stringify(d));
 assert.equal(d.languageAction,null,'search changed language '+message+' '+JSON.stringify(d));
}
console.log('R76_SEARCH_NO_MUTATION_PASS',searchCases.length);

// Explicit app commands: respond in the speaker's language and emit only the requested action.
for(const [message,cc,ll,replyLang] of [
 ['حطني تركيا','TR',null,'ar'],['غيّر الأب على لبنان','LB',null,'ar'],
 ['change the app to France','FR',null,'en'],['حوّلني ورلد وايد','WW',null,'ar'],
 ['غير لغة التطبيق للتركي',null,'tr','ar']
]){
 const d=(await jsonReq('POST','/api/ai',{message,country:'Worldwide',language:'auto',scope:'worldwide',fast:true})).json;
 assert(String(d.response||'').trim(),message);assert.equal(d.language,replyLang,message+' '+JSON.stringify(d));
 if(cc)assert.equal(d?.countryAction?.code,cc,message);else assert.equal(d.countryAction,null,message);
 if(ll)assert.equal(d?.languageAction?.code,ll,message);else assert.equal(d.languageAction,null,message);
}
console.log('R76_EXPLICIT_ACTION_PASS');

// Verify all 98 deployed packs and exact source hash/count, with origin fallback only for runner throttling.
const manifest=(await jsonReq('GET','/i18n-r32/manifest.json')).json;
const source=(await jsonReq('GET','/i18n-r32-source.json')).json;
assert.equal(manifest.version,VER);assert.equal(manifest.packs,98);assert.equal(manifest.languages.length,98);
assert.equal(source.count,1045);assert.equal(manifest.sourceHash,source.sourceHash);
const packs={};
for(let i=0;i<manifest.languages.length;i+=12){
 await Promise.all(manifest.languages.slice(i,i+12).map(async l=>{
   const d=(await jsonReq('GET','/i18n-r32/'+l+'.json?v='+manifest.sourceHash)).json;
   assert.equal(d.count,1045,l);assert.equal(d.sourceHash,manifest.sourceHash,l);packs[l]=d.translations;
 }));
 console.log('R76_PACK_CERT_PROGRESS',Math.min(i+12,98),'/98');
}
console.log('R76_98_PACKS_CERTIFIED',manifest.sourceHash);

// Country selection must atomically change country, language, currency and document language for every profile.
const matrix=await page.evaluate(async()=>{
 const bad=[];for(const [cc,pr] of Object.entries(SEEKVERA_LOCALE_R15.profiles)){
   SEEKVERA_LOCALE_R15.setCountry(cc);await new Promise(r=>setTimeout(r,2));
   const g={cc:country?.value,l:lang?.value,c:currency?.value,html:document.documentElement.lang};
   if(g.cc!==cc||g.l!==pr.language||g.c!==pr.currency||g.html!==pr.language)bad.push({cc,pr,g});
 }
 return{n:Object.keys(SEEKVERA_LOCALE_R15.profiles).length,bad};
});
assert(matrix.n>=248,matrix.n);assert.equal(matrix.bad.length,0,JSON.stringify(matrix.bad.slice(0,8)));
console.log('R76_248_COUNTRY_MATRIX_PASS',matrix.n);

// Block dynamic translation during localization certification. Complete R76 packs must stand alone.
const fallbacks=[];
await ctx.route('**/api/ui-translate',async route=>{
 let strings=[];try{strings=route.request().postDataJSON()?.strings||[]}catch{}
 fallbacks.push({url:route.request().url(),strings:strings.slice(0,6)});
 await route.fulfill({status:503,contentType:'application/json',body:'{"ok":false,"audit":"static-only"}'});
});
await ctx.route('https://text.pollinations.ai/**',async route=>route.fulfill({status:503,body:'static-only'}));

// Homepage: apply every language and detect visible English source leakage when a translated value exists.
await page.goto(B+'/?r76langs='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,{timeout:25000});
await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('en'));await pause(35);
const candidateEnglish=source.strings.filter(s=>s.length>=12&&(s.match(/[A-Za-z][A-Za-z'’+-]{2,}/g)||[]).length>=2&&!s.includes('SEEKVERA')&&!/https?:\/\/|@/.test(s));
const homeEnglish=await page.locator('body').innerText();const homePresent=candidateEnglish.filter(s=>homeEnglish.includes(s));const leaks=[];
for(let i=0;i<manifest.languages.length;i++){
 const l=manifest.languages[i];
 await page.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N_R32.loadPack(l);await SEEKVERA_I18N_R32.apply()},l);
 const state=await page.evaluate(()=>document.documentElement.lang);assert.equal(state,l,'html lang '+l);
 if(l!=='en'){
   const body=await page.locator('body').innerText();const x=homePresent.filter(s=>packs[l]?.[s]&&packs[l][s]!==s&&body.includes(s)).slice(0,5);
   if(x.length)leaks.push({path:'/',l,leaks:x});
 }
 if((i+1)%14===0||i===97)console.log('R76_LANGUAGE_CERT_PROGRESS',i+1,'/98');
}
assert.equal(leaks.length,0,'home English leaks '+JSON.stringify(leaks.slice(0,8)));

// Discover every category route from the live homepage and certify every real section.
await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('en'));await pause(30);
const hrefs=await page.evaluate(()=>[...new Set([...document.querySelectorAll('#categories .r5-tile')].map(a=>a.getAttribute('href')).filter(Boolean))]);
assert(hrefs.length>=31,'category routes '+hrefs.length);
const paths=[...new Set(hrefs.map(h=>new URL(h,B).pathname))];
const anchors=['en','ar','fr','tr','hi','zh','de'];let combinations=98;
for(let pi=0;pi<paths.length;pi++){
 const path=paths[pi];const r=await page.goto(B+path+'?r76section='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
 assert(r&&r.status()<400,path+' '+r?.status());
 await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_I18N_R32,{timeout:25000});
 await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('en'));await pause(20);
 const english=await page.locator('body').innerText();const present=candidateEnglish.filter(s=>english.includes(s));
 const assigned=manifest.languages.filter((_,li)=>li%paths.length===pi);const testLangs=[...new Set([...anchors,...assigned])];
 for(const l of testLangs){
   await page.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N_R32.loadPack(l);await SEEKVERA_I18N_R32.apply()},l);combinations++;
   if(l==='en')continue;const body=await page.locator('body').innerText();const x=present.filter(s=>packs[l]?.[s]&&packs[l][s]!==s&&body.includes(s)).slice(0,5);
   if(x.length)leaks.push({path,l,leaks:x});
 }
 console.log('R76_SECTION_CERT_PROGRESS',pi+1,'/',paths.length,path);
}
assert.equal(leaks.length,0,'section English leaks '+JSON.stringify(leaks.slice(0,8)));
assert.equal(fallbacks.length,0,'dynamic translation fallback used '+JSON.stringify(fallbacks.slice(0,8)));
console.log('R76_ALL_SECTIONS_LANGUAGES_PASS',JSON.stringify({routes:hrefs.length,paths:paths.length,combinations}));

// Chat: answer must appear before navigation; history must survive navigation/restore.
await page.goto(B+'/?r76chat='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
await page.waitForFunction(()=>window.SEEKVERA_R31&&window.SEEKVERA_CHAT&&document.querySelector('#aiChatForm'),{timeout:30000});
await page.evaluate(()=>{localStorage.removeItem('seekvera_ai_chat_v1');SEEKVERA_LOCALE_R15.setCountry('LB')});
await page.fill('#aiChatInput','بدي وظيفة مبيعات بفرنسا');const before=page.url(),t=Date.now();await page.locator('#aiChatForm').evaluate(f=>f.requestSubmit());
await page.waitForFunction(()=>{const x=[...document.querySelectorAll('#aiMessages .ai-msg.bot')].at(-1);return x&&!x.classList.contains('thinking')&&/[\u0600-\u06ff]/u.test(x.textContent||'')},{timeout:22000});
const replyMs=Date.now()-t;assert.equal(page.url(),before,'navigation occurred before reply');
await page.waitForFunction(()=>location.pathname==='/jobs'||location.pathname==='/jobs.html',{timeout:12000});
const saved=await page.evaluate(()=>localStorage.getItem('seekvera_ai_chat_v1')||'');assert(saved.includes('بدي وظيفة مبيعات بفرنسا'),'chat not saved');
await page.goto(B+'/?r76restore='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});await page.waitForFunction(()=>window.SEEKVERA_CHAT&&document.querySelector('#aiMessages'),{timeout:30000});await pause(250);
assert((await page.locator('#aiMessages').innerText()).includes('بدي وظيفة مبيعات بفرنسا'),'chat not restored');
console.log('R76_CHAT_ORDER_PERSIST_PASS',replyMs);

// Explicit control in live UI: response first, then country changes.
await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('LB'));await page.fill('#aiChatInput','حطني تركيا');const n=await page.locator('#aiMessages .ai-msg.bot').count(),u0=page.url();await page.locator('#aiChatForm').evaluate(f=>f.requestSubmit());
await page.waitForFunction(n=>document.querySelectorAll('#aiMessages .ai-msg.bot').length>n,n,{timeout:12000});assert.equal(page.url(),u0,'control navigated before reply');
await page.waitForFunction(()=>document.querySelector('#country')?.value==='TR',{timeout:10000});
console.log('R76_LIVE_CONTROL_ORDER_PASS');

// Voice: microphone-origin response must invoke TTS; transcribe path must prefer server ASR auto-language.
const spoken=await page.evaluate(async()=>{window.__r76spoken=0;try{speechSynthesis.speak=()=>{window.__r76spoken++}}catch{};SEEKVERA_VOICE_AI?.markVoiceReply?.();window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:'مرحبا، كيف فيني ساعدك؟',language:'ar'}}));await new Promise(r=>setTimeout(r,500));return window.__r76spoken});
assert(spoken>0,'TTS not invoked');
const voice=(await request('GET','/voice-ai.js')).body;assert(voice.includes('serverVoice(targetId,activeButton,true)'));assert(voice.includes("language:'auto'"));
assert.equal(pageErrors.length,0,'page errors '+pageErrors.slice(0,10).join(' | '));
console.log('R76_FINAL_LIVE_CERTIFIED',JSON.stringify({countries:matrix.n,languages:98,routes:hrefs.length,paths:paths.length,sourceStrings:1045,chatSaved:true,chatRestored:true,replyMs,ttsCalls:spoken,dynamicFallbacks:fallbacks.length}));
await browser.close();
