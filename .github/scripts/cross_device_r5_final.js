const { chromium, firefox, webkit, devices } = require('playwright');
const SITE='https://seekveraglobal.com';
const assert=(v,m)=>{if(!v)throw new Error(m)};
const profiles=[
  {name:'Android Chrome / Samsung-class',engine:chromium,ctx:{...devices['Pixel 5']}},
  {name:'iPhone Safari / WebKit',engine:webkit,ctx:{...devices['iPhone 13']}},
  {name:'iPad Safari / WebKit',engine:webkit,ctx:{...devices['iPad Pro 11']}},
  {name:'Desktop Chrome / Edge-class',engine:chromium,ctx:{viewport:{width:1440,height:900},userAgent:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36'}},
  {name:'Desktop Firefox',engine:firefox,ctx:{viewport:{width:1366,height:850}}},
  {name:'Desktop Safari / WebKit',engine:webkit,ctx:{viewport:{width:1440,height:900},userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/18.0 Safari/605.1.15'}}
];
async function auditProfile(p){
  const browser=await p.engine.launch({headless:true});
  const context=await browser.newContext({...p.ctx});
  const page=await context.newPage();
  const errs=[]; page.on('pageerror',e=>errs.push(String(e)));
  await page.goto(SITE+'/?r5-final-cross-device=1',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>document.querySelector('#country')?.options?.length>=249&&document.querySelector('#lang')?.options?.length===29,null,{timeout:60000});
  await page.waitForTimeout(500);
  const s=await page.evaluate(()=>({
    release:document.body.dataset.release,
    country:document.querySelector('#country')?.value,
    countryText:document.querySelector('#country')?.selectedOptions?.[0]?.textContent?.trim(),
    countries:document.querySelector('#country')?.options?.length,
    langs:document.querySelector('#lang')?.options?.length,
    tiles:[...document.querySelectorAll('.r5-tile')].map(x=>({text:x.innerText.trim(),w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height})),
    chat:!!document.querySelector('#aiChatInput')&&!!document.querySelector('#aiChatMic')&&!!document.querySelector('#aiChatSpeaker'),
    media:!!document.querySelector('a[href="media.html"]'),games:!!document.querySelector('a[href="games.html"]'),
    overflow:Math.max(0,document.documentElement.scrollWidth-window.innerWidth)
  }));
  console.log('PROFILE',p.name,s);
  assert(s.release==='20260923-market-r5',p.name+' wrong release');
  assert(s.country==='WW'&&/Worldwide/i.test(s.countryText||''),p.name+' not Worldwide');
  assert(s.countries>=249&&s.langs===29,p.name+' country/language list incomplete');
  assert(s.tiles.length>=16&&s.tiles.every(t=>t.text.length>2&&t.w>70&&t.h>45),p.name+' blank/collapsed marketplace tile');
  assert(s.chat&&s.media&&s.games,p.name+' core controls/routes missing');
  assert(s.overflow<=3,p.name+' horizontal overflow '+s.overflow);
  assert(!errs.length,p.name+' page errors '+errs.join(' | '));

  await page.selectOption('#lang','ar'); await page.dispatchEvent('#lang','change');
  await page.waitForFunction(()=>document.documentElement.dir==='rtl'&&/العالم/.test(document.querySelector('#country')?.selectedOptions?.[0]?.textContent||''),null,{timeout:30000});
  const ar=await page.evaluate(()=>({intro:document.querySelector('#aiMessages .ai-msg.bot')?.textContent||'',overflow:Math.max(0,document.documentElement.scrollWidth-window.innerWidth)}));
  assert(/[\u0600-\u06ff]/.test(ar.intro),p.name+' Arabic AI intro missing');
  assert(ar.overflow<=3,p.name+' Arabic overflow');

  await page.selectOption('#lang','en'); await page.dispatchEvent('#lang','change');
  await page.fill('#aiChatInput','Reply only with: Hello.'); await page.click('#aiChatForm .send');
  await page.waitForFunction(()=>[...document.querySelectorAll('#aiMessages .ai-msg.bot')].some(x=>/hello/i.test(x.textContent||'')),null,{timeout:75000});
  console.log('CHAT_PASS',p.name);
  await browser.close();
}
async function auditWebKitVoiceFallback(){
  const browser=await webkit.launch({headless:true});
  const context=await browser.newContext({...devices['iPhone 13']});
  await context.addInitScript(()=>{
    Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:async()=>({getTracks:()=>[{stop(){}}]})}});
    class FakeRecorder{
      constructor(stream,opts={}){this.stream=stream;this.mimeType=opts.mimeType||'audio/webm';this.state='inactive'}
      static isTypeSupported(){return true}
      start(){this.state='recording'}
      stop(){this.state='inactive';const data=new Blob(['fake-audio'],{type:this.mimeType});this.ondataavailable?.({data});this.onstop?.()}
    }
    Object.defineProperty(window,'MediaRecorder',{configurable:true,value:FakeRecorder});
    Object.defineProperty(window,'SpeechRecognition',{configurable:true,value:undefined});
    Object.defineProperty(window,'webkitSpeechRecognition',{configurable:true,value:undefined});
  });
  const page=await context.newPage();
  await page.route('**/api/transcribe',async route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,text:'Hello from voice',model:'test'})}));
  await page.goto(SITE+'/?webkit-voice-fallback=1',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForSelector('#aiChatMic',{timeout:30000});
  await page.click('#aiChatMic');
  await page.waitForFunction(()=>/Listening/i.test(document.querySelector('#aiChatInput')?.placeholder||''),null,{timeout:10000});
  await page.click('#aiChatMic');
  await page.waitForFunction(()=>[...document.querySelectorAll('#aiMessages .ai-msg.user')].some(x=>/Hello from voice/i.test(x.textContent||'')),null,{timeout:30000});
  console.log('IPHONE_WEBKIT_SERVER_VOICE_FALLBACK_PASS');
  await browser.close();
}
async function auditAppShellAndRuntime(){
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage();
  await page.goto(SITE+'/app.html#home',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>document.body?.dataset?.release==='20260923-market-r5',null,{timeout:30000});
  assert(await page.locator('iframe').count()===0,'app launch ended with iframe nesting');
  const [health,voice,manifest,sw]=await Promise.all([
    page.request.get(SITE+'/api/health?r5-final=1').then(r=>r.json()),
    page.request.get(SITE+'/voice-ai.js?r5-final=1').then(r=>r.text()),
    page.request.get(SITE+'/manifest.webmanifest?r5-final=1').then(r=>r.text()),
    page.request.get(SITE+'/sw.js?r5-final=1').then(r=>r.text())
  ]);
  assert(health.ok===true&&health.voiceInputFallback==='server-asr-v1','live server ASR health missing');
  assert(String(health.asrModel||'').includes('whisper-large-v3-turbo'),'live ASR model missing');
  assert(health.centralSafetyGate==='enabled'&&health.failClosed===true,'Safety Gate health failed');
  assert(voice.includes('serverVoice')&&voice.includes('MediaRecorder')&&voice.includes('/api/transcribe'),'live cross-device voice JS missing');
  assert(manifest.includes('index.html?v=20260923-market-r5'),'PWA start URL wrong');
  assert(sw.includes('seekvera-market-r5-20260923'),'service worker cache wrong');
  const invalid=await page.request.post(SITE+'/api/transcribe',{data:{audio:'invalid',language:'en'}});
  const bad=await invalid.json(); assert(invalid.status()===400&&/recorded audio/i.test(bad.error||''),'transcribe route not active');
  console.log('APP_PWA_ASR_SAFETY_PASS');
  await browser.close();
}
(async()=>{
  for(const p of profiles)await auditProfile(p);
  await auditWebKitVoiceFallback();
  await auditAppShellAndRuntime();
  console.log('SEEKVERA R5 FINAL ALL-DEVICE AUDIT PASS');
})().catch(e=>{console.error(e);process.exit(1)});
