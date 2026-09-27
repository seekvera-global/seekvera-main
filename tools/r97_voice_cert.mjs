import { chromium } from 'playwright';
import fs from 'node:fs';
import assert from 'node:assert/strict';

const en=fs.readFileSync('/tmp/r97-en.wav').toString('base64');
const ar=fs.readFileSync('/tmp/r97-ar.wav').toString('base64');
const b=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage({locale:'en-US'});

await p.addInitScript(()=>{
  window.__r97Spoken=[];
  window.__r97TtsEvents=[];
  class FakeUtterance{
    constructor(text){this.text=String(text||'');this.lang='';this.voice=null;this.rate=1;this.pitch=1;this.volume=1;this.onstart=null;this.onend=null;this.onerror=null}
  }
  const synth={
    speaking:false,
    getVoices(){return[
      {name:'R97 Arabic Female',lang:'ar-SA',voiceURI:'r97-ar',default:false},
      {name:'R97 English Female',lang:'en-US',voiceURI:'r97-en',default:true},
      {name:'R97 French Female',lang:'fr-FR',voiceURI:'r97-fr',default:false}
    ]},
    cancel(){this.speaking=false}, resume(){}, pause(){}, addEventListener(){}, removeEventListener(){},
    speak(u){
      this.speaking=true;
      window.__r97Spoken.push({text:String(u.text||''),lang:String(u.lang||'')});
      setTimeout(()=>{try{u.onstart?.()}catch{};setTimeout(()=>{this.speaking=false;try{u.onend?.()}catch{}},25)},5)
    }
  };
  try{Object.defineProperty(window,'SpeechSynthesisUtterance',{value:FakeUtterance,configurable:true})}catch{window.SpeechSynthesisUtterance=FakeUtterance}
  try{Object.defineProperty(window,'speechSynthesis',{value:synth,configurable:true})}catch{window.speechSynthesis=synth}
  window.addEventListener('seekvera:tts-start',e=>window.__r97TtsEvents.push({type:'start',...(e.detail||{})}));
  window.addEventListener('seekvera:tts-end',e=>window.__r97TtsEvents.push({type:'end',...(e.detail||{})}));
});

p.on('console',m=>console.log('BROWSER',m.type(),m.text()));
p.on('pageerror',e=>console.log('PAGEERROR',e.message));
await p.goto('https://seekveraglobal.com/?r97=voice-'+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForFunction(()=>window.SEEKVERA_VOICE_AI&&window.SEEKVERA_I18N_R32&&window.SEEKVERA_LOCALE_R15,{timeout:30000});

// Real multilingual local Whisper transcription from actual WAV audio fixtures.
const trans=await p.evaluate(async({en,ar})=>{
  const mk=b64=>{const raw=atob(b64),u=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)u[i]=raw.charCodeAt(i);return new Blob([u],{type:'audio/wav'})};
  const t=window.SEEKVERA_VOICE_AI.localWhisperTranscribe;
  const english=await t(mk(en));
  const arabic=await t(mk(ar));
  return {english,arabic};
},{en,ar});
console.log('R97_TRANSCRIPTS',JSON.stringify(trans));
assert.ok(String(trans.english?.text||'').trim().length>2,'English transcript empty');
assert.ok(String(trans.arabic?.text||'').trim().length>2,'Arabic transcript empty');
assert.ok(/[\u0600-\u06ff]/.test(String(trans.arabic.text)),'Arabic was not recognized as Arabic: '+trans.arabic.text);

// Actual home chat in Arabic, with the real AI reply flowing into the spoken-reply path.
await p.selectOption('#country','LB');
await p.waitForFunction(()=>document.documentElement.lang==='ar'&&document.documentElement.dataset.seekveraI18nReady==='ar',{timeout:25000});
await p.evaluate(()=>{localStorage.setItem('seekvera_voice_mode','1');localStorage.setItem('seekvera_voice_muted','0');window.__r97Spoken.length=0});
const beforeAr=await p.locator('#aiMessages .ai-msg.bot:not(.thinking)').count();
await p.fill('#aiChatInput','مرحبا كيفك اليوم؟');
await p.locator('#aiChatForm').evaluate(f=>f.requestSubmit());
await p.waitForFunction(n=>document.querySelectorAll('#aiMessages .ai-msg.bot:not(.thinking)').length>n,beforeAr,{timeout:35000});
await p.waitForFunction(()=>window.__r97Spoken.some(x=>/[\u0600-\u06ff]/.test(x.text)),{timeout:12000});
const arabicUi=await p.evaluate(()=>({reply:[...document.querySelectorAll('#aiMessages .ai-msg.bot:not(.thinking)')].at(-1)?.textContent?.trim()||'',spoken:window.__r97Spoken.slice(),events:window.__r97TtsEvents.slice()}));
assert.ok(arabicUi.reply.length>3,'Arabic UI AI reply empty');
assert.ok(/[\u0600-\u06ff]/.test(arabicUi.reply),'Arabic user got non-Arabic reply: '+arabicUi.reply);
assert.ok(arabicUi.spoken.some(x=>/^ar/i.test(x.lang)),'Arabic spoken reply did not select Arabic voice: '+JSON.stringify(arabicUi.spoken));
console.log('R97_ARABIC_CHAT_TTS_PASS',arabicUi.reply.slice(0,120));

// Same live UI path in English after country switch.
await p.selectOption('#country','US');
await p.waitForFunction(()=>document.documentElement.lang==='en'&&document.documentElement.dataset.seekveraI18nReady==='en',{timeout:25000});
await p.evaluate(()=>{window.__r97Spoken.length=0});
const beforeEn=await p.locator('#aiMessages .ai-msg.bot:not(.thinking)').count();
await p.fill('#aiChatInput','Hello, how are you today?');
await p.locator('#aiChatForm').evaluate(f=>f.requestSubmit());
await p.waitForFunction(n=>document.querySelectorAll('#aiMessages .ai-msg.bot:not(.thinking)').length>n,beforeEn,{timeout:35000});
await p.waitForFunction(()=>window.__r97Spoken.some(x=>String(x.text||'').trim().length>2),{timeout:12000});
const englishUi=await p.evaluate(()=>({reply:[...document.querySelectorAll('#aiMessages .ai-msg.bot:not(.thinking)')].at(-1)?.textContent?.trim()||'',spoken:window.__r97Spoken.slice()}));
assert.ok(englishUi.reply.length>3,'English UI AI reply empty');
assert.ok(englishUi.spoken.some(x=>/^en/i.test(x.lang)),'English spoken reply did not select English voice: '+JSON.stringify(englishUi.spoken));
console.log('R97_ENGLISH_CHAT_TTS_PASS',englishUi.reply.slice(0,120));

await b.close();
console.log('R97_REAL_MULTILINGUAL_VOICE_PASS');
