import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const B='https://seekveraglobal.com/';
const browser=await chromium.launch({headless:true});
const ctx=await browser.newContext({
  locale:'en-US',
  userAgent:'Mozilla/5.0 (Linux; Android 14; SM-A225F) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'
});
const page=await ctx.newPage();
await page.goto(B+'?r123='+Date.now(),{waitUntil:'networkidle',timeout:60000});
await page.waitForFunction(()=>window.SEEKVERA_VOICE_AI&&window.SEEKVERA_R31,{timeout:30000});
const state=await page.evaluate(async()=>{
  const api=window.SEEKVERA_VOICE_AI;
  const compact=api.compactTranscript('بدي شغل ببيروت بدي شغل ببيروت');
  const first=api.acceptVoiceTurn('دوريني على شغل');
  const second=api.acceptVoiceTurn('دوريني على شغل');
  localStorage.setItem('seekvera_voice_mode','1');
  let tts=0;
  const onTts=()=>tts++;
  window.addEventListener('seekvera:tts-request',onTts);
  window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:'أكيد، سأساعدك بالعربية.',language:'ar'}}));
  window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:'أكيد، سأساعدك بالعربية.',language:'ar'}}));
  await new Promise(r=>setTimeout(r,250));
  window.removeEventListener('seekvera:tts-request',onTts);
  return {mode:window.__seekveraVoiceMode,compact,first,second,tts};
});
assert.equal(state.mode,'20260929-r123-arabic-auto-dedupe',state);
assert.equal(state.compact,'بدي شغل ببيروت',state);
assert.equal(state.first,true,state);
assert.equal(state.second,false,state);
assert.equal(state.tts,1,state);

await page.route('**/api/ai',route=>route.fulfill({
  status:200,
  contentType:'application/json',
  body:JSON.stringify({ok:true,response:'أهلاً، كيف فيني ساعدك؟',language:'ar',category:'general',route:'marketplace.html'})
}));
await page.evaluate(()=>{document.querySelector('#aiMessages').innerHTML='';window.__seekveraLastSubmittedTurn=null});
await page.evaluate(()=>window.SEEKVERA_R31.submitAI('مرحبا',{fromVoice:true}));
await page.waitForFunction(()=>document.querySelectorAll('#aiMessages .ai-msg.user').length===1,{timeout:10000});
await page.waitForTimeout(400);
await page.evaluate(()=>window.SEEKVERA_R31.submitAI('مرحبا',{fromVoice:true}));
await page.waitForTimeout(500);
const turns=await page.locator('#aiMessages .ai-msg.user').allTextContents();
assert.equal(turns.filter(x=>x.trim()==='مرحبا').length,1,turns);
console.log('R123_BROWSER_PASS',state,{turns});
await browser.close();
