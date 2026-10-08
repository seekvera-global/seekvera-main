import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const browser=await chromium.launch({headless:true,...(process.env.HTTPS_PROXY?{proxy:{server:process.env.HTTPS_PROXY}}:{})});
try {
 const ctx=await browser.newContext({ignoreHTTPSErrors:true,serviceWorkers:'block'});
 await ctx.route('**/*',r=>['seekveraglobal.com','www.seekveraglobal.com','seekvera-main.seekvera-global.workers.dev'].includes(new URL(r.request().url()).hostname)?r.continue():r.abort());
 await ctx.route('**/api/ui-translate',r=>r.fulfill({status:503,body:'{"ok":false}'}));
 if(process.env.LIVE_OVERRIDES==='1')for(const f of ['i18n-ui.js','voice-ai.js'])await ctx.route('**/'+f+'*',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(f,'utf8')}));
 await ctx.addInitScript(()=>{window.SpeechRecognition=undefined;window.webkitSpeechRecognition=undefined;window.MediaRecorder=undefined});
 const page=await ctx.newPage();await page.goto('https://seekveraglobal.com/',{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForFunction(()=>window.SEEKVERA_I18N?.setAttributeSource&&window.SEEKVERA_VOICE_AI);
 for(const l of ['fr','ar']){
  await page.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N.apply();SEEKVERA_VOICE_AI.start('aiChatInput')},l);
  const expected=await page.evaluate(()=>SEEKVERA_I18N.t('Voice recognition is not supported in this browser.'));
  await page.waitForTimeout(700);assert.equal(await page.locator('#aiChatInput').getAttribute('placeholder'),expected);
  await page.evaluate(()=>SEEKVERA_I18N.setAttributeSource(document.getElementById('aiChatInput'),'placeholder','Understanding your speech…'));
  const understanding=await page.evaluate(()=>SEEKVERA_I18N.t('Understanding your speech…'));
  await page.waitForTimeout(700);assert.equal(await page.locator('#aiChatInput').getAttribute('placeholder'),understanding);
  await page.evaluate(async()=>{SEEKVERA_LOCALE_R15.setLanguage('en');await SEEKVERA_I18N.apply()});
  assert.equal(await page.locator('#aiChatInput').getAttribute('placeholder'),'Understanding your speech…');
  await page.evaluate(()=>SEEKVERA_I18N.setAttributeSource(document.getElementById('aiChatInput'),'placeholder','Message SEEKVERA AI…'));
  await page.waitForTimeout(400);assert.equal(await page.locator('#aiChatInput').getAttribute('placeholder'),'Message SEEKVERA AI…');
  console.log('VOICE_PLACEHOLDER_STATE_PASS',l);
 }
}finally{await browser.close()}
