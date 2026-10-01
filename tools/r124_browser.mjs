import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,...(process.env.HTTPS_PROXY?{proxy:{server:process.env.HTTPS_PROXY}}:{})});
try{
 const page=await browser.newPage({ignoreHTTPSErrors:true,locale:'en-US',userAgent:'Mozilla/5.0 (Linux; Android 11; SM-A225F) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'});
 await page.route('**/*',r=>{const u=new URL(r.request().url());if(['seekveraglobal.com','www.seekveraglobal.com','seekvera-main.seekvera-global.workers.dev'].includes(u.hostname))return r.continue();return r.abort()});
 await page.addInitScript(()=>{for(const name of ['seekvera:tts-start','seekvera:tts-end'])window.addEventListener(name,e=>{const log=JSON.parse(sessionStorage.getItem('r124-audio-events')||'[]');log.push({name,at:Date.now(),engine:e.detail?.engine});sessionStorage.setItem('r124-audio-events',JSON.stringify(log))})});
 await page.goto('https://seekveraglobal.com/?r124=browser',{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForFunction(()=>window.SEEKVERA_R31?.submitAI&&window.SEEKVERA_VOICE_AI,{timeout:30000});
 // A one-second PCM tone verifies real AudioContext decoding and completion,
 // including a delayed server response, rather than a synthetic onstart alone.
 const wav=Buffer.alloc(44+32000);wav.write('RIFF');wav.writeUInt32LE(wav.length-8,4);wav.write('WAVE',8);wav.write('fmt ',12);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(16000,24);wav.writeUInt32LE(32000,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(32000,40);for(let n=0;n<16000;n++)wav.writeInt16LE(Math.round(Math.sin(n*2*Math.PI*440/16000)*3000),44+n*2);
 await page.route('**/api/ai',r=>r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,response:'أكيد، عم بفتحلك القسم المناسب.',language:'ar',category:'travel',route:'travel.html'})}));
 await page.route('**/api/tts',async r=>{await new Promise(resolve=>setTimeout(resolve,1200));await r.fulfill({status:200,contentType:'audio/wav',body:wav})});
 await page.evaluate(()=>{const b=document.createElement('button');b.id='r124-unlock';b.textContent='Prepare';b.onclick=()=>window.SEEKVERA_VOICE_AI.prepareVoice();document.body.append(b)});
 await page.locator('#r124-unlock').click();
 await page.evaluate(()=>{sessionStorage.removeItem('r124-audio-events');window.SEEKVERA_R31.submitAI('بدي أسافر',{fromVoice:true})});
 await page.waitForURL(/\/travel(?:\.html)?(?:\?|$)/,{timeout:20000,waitUntil:'domcontentloaded'});
 const logs=await page.evaluate(()=>JSON.parse(sessionStorage.getItem('r124-audio-events')||'[]'));
 const start=logs.find(e=>e.name==='seekvera:tts-start'&&e.engine==='server'),end=logs.find(e=>e.name==='seekvera:tts-end'&&e.engine==='server');
 assert.ok(start&&end,JSON.stringify(logs));assert.equal(logs.filter(e=>e.name==='seekvera:tts-start'&&e.engine==='server').length,1,'short replies must use a single audio request');assert.ok(end.at-start.at>=900,JSON.stringify(logs));
 const chat=await page.evaluate(()=>JSON.parse(localStorage.getItem('seekvera_ai_chat_v1')||'[]'));
 assert.ok(chat.some(x=>x.role==='user'&&x.text==='بدي أسافر'),'chat must survive navigation');
 console.log('PASS: delayed server audio decoded and completed before navigation on Android browser profile',logs,chat);
}finally{await browser.close()}
