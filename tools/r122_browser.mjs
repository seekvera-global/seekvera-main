import{chromium}from'playwright';import assert from'node:assert/strict';
const B='https://seekveraglobal.com/';
const ua='Mozilla/5.0 (Linux; Android 11; SM-A225F) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36';
const b=await chromium.launch({headless:true});
const p=await b.newPage({viewport:{width:390,height:844},locale:'en-US',userAgent:ua});
const errs=[];p.on('pageerror',e=>errs.push(String(e)));
const isJobs=u=>/^\/jobs(?:\.html)?\/?$/.test(u.pathname);

async function home(tag){
  await p.goto(B+'?'+tag+'='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
  await p.waitForFunction(()=>window.SEEKVERA_VOICE_AI&&window.SEEKVERA_R31?.submitAI&&window.SEEKVERA_R24_CONTROLLER&&document.querySelector('#aiChatForm'),null,{timeout:25000});
}

await home('r122typed');
let state=await p.evaluate(()=>({voice:window.__seekveraVoiceMode,r31:window.SEEKVERA_R31?.version}));
assert.equal(state.voice,'20260929-r122-language-independent-voice');
assert.equal(state.r31,'20260929-r122-unified-direct-routing');
const hybrid=await p.evaluate(()=>window.SEEKVERA_VOICE_AI.chooseHybridTranscript('Halið á að leita að vinnu',.97,{text:'دوريني على شغل',language:'ar',engine:'server-whisper-auto'}));
assert.match(hybrid.text,/[\u0600-\u06ff]/u);assert.equal(hybrid.language,'ar');
const before=await p.locator('#aiMessages .ai-msg.bot:not(.thinking)').count(),t0=Date.now();
await p.fill('#aiChatInput','دوريني على شغل');await p.locator('#aiChatForm').evaluate(f=>f.requestSubmit());
await p.waitForFunction(n=>document.querySelectorAll('#aiMessages .ai-msg.bot:not(.thinking)').length>n,before,{timeout:3500});
const typedReply=await p.locator('#aiMessages .ai-msg.bot:not(.thinking)').last().innerText();assert.match(typedReply,/[\u0600-\u06ff]/u);
await p.waitForURL(isJobs,{timeout:3500,waitUntil:'domcontentloaded'});
const typedMs=Date.now()-t0;assert(typedMs<3500,{typedMs,url:p.url(),typedReply});
console.log('TYPED_DIRECT_ROUTE_PASS',JSON.stringify({typedMs,url:p.url(),typedReply}));

await home('r122control');
const c0=Date.now();
await p.fill('#aiChatInput','حوليني على تركيا');await p.locator('#aiChatForm').evaluate(f=>f.requestSubmit());
await p.waitForFunction(()=>document.querySelector('#country')?.value==='TR',{timeout:2500});
await p.waitForFunction(()=>document.querySelector('#lang')?.value==='tr'&&document.querySelector('#currency')?.value==='TRY'&&document.documentElement.lang==='tr',{timeout:3500});
const ctl=await p.evaluate(()=>({country:document.querySelector('#country')?.value,lang:document.querySelector('#lang')?.value,currency:document.querySelector('#currency')?.value,htmlLang:document.documentElement.lang}));
const ctlMs=Date.now()-c0;assert.deepEqual(ctl,{country:'TR',lang:'tr',currency:'TRY',htmlLang:'tr'});assert(ctlMs<3500,{ctlMs,ctl});
console.log('ATOMIC_COUNTRY_PASS',JSON.stringify({ctlMs,ctl}));

await home('r122voice');
await p.evaluate(()=>{localStorage.setItem('seekvera_voice_mode','1');localStorage.setItem('seekvera_voice_muted','0');window.SEEKVERA_VOICE_AI?.markVoiceReply?.()});
const v0=Date.now();
await p.evaluate(()=>window.SEEKVERA_R31.submitAI('دوريني على شغل',{fromVoice:true}));
await p.waitForURL(isJobs,{timeout:4500,waitUntil:'domcontentloaded'});
const voiceMs=Date.now()-v0;assert(voiceMs<4500,{voiceMs,url:p.url()});
console.log('VOICE_DIRECT_ROUTE_PASS',JSON.stringify({voiceMs,url:p.url()}));

assert.equal(errs.length,0,errs.join('\n'));
await b.close();
