import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const browser=await chromium.launch({headless:true,...(process.env.HTTPS_PROXY?{proxy:{server:process.env.HTTPS_PROXY}}:{})});
try {
 const ctx=await browser.newContext({ignoreHTTPSErrors:true,serviceWorkers:'block'});
 await ctx.route('**/*',r=>['seekveraglobal.com','www.seekveraglobal.com','seekvera-main.seekvera-global.workers.dev'].includes(new URL(r.request().url()).hostname)?r.continue():r.abort());
 let translationRequests=0;await ctx.route('**/api/ui-translate',r=>{translationRequests++;return r.fulfill({status:503,body:'{"ok":false}'})});
 if(process.env.LIVE_OVERRIDES==='1')for(const f of ['global-ui.js','i18n-ui.js','r32-i18n.js','games.js'])await ctx.route('**/'+f+'*',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(f,'utf8')}));
 if(process.env.LOCALE_STAGE)for(const l of ['fr','ar'])await ctx.route('**/i18n-r32/'+l+'.json*',r=>r.fulfill({contentType:'application/json',body:fs.readFileSync(process.env.LOCALE_STAGE+'/'+l+'.json','utf8')}));
 const page=await ctx.newPage();await page.goto('https://seekveraglobal.com/games.html',{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForFunction(()=>window.SEEKVERA_I18N&&document.querySelectorAll('#gameGrid .game').length===50);
 const names=await page.locator('#gameGrid .game b').allTextContents();
 for(const l of ['fr','ar']){
  await page.evaluate(async l=>{SEEKVERA_LOCALE_R15.setLanguage(l);await SEEKVERA_I18N.apply()},l);
  const pack=JSON.parse(fs.readFileSync((process.env.LOCALE_STAGE||'i18n-r32')+'/'+l+'.json','utf8')).translations;
  const englishDescriptions=[...fs.readFileSync('games.js','utf8').matchAll(/desc:'([^']+)'/g)].map(x=>x[1]);
  const expected=englishDescriptions.map(s=>pack[s]);assert(expected.every(Boolean));
  await page.waitForFunction(expected=>JSON.stringify([...document.querySelectorAll('#gameGrid .game small span:last-child')].map(e=>e.textContent))===JSON.stringify(expected),expected,{timeout:20000});
  assert.deepEqual(await page.locator('#gameGrid .game b').allTextContents(),names);
  await page.locator('#filters button').nth(1).click();await page.evaluate(()=>SEEKVERA_I18N.apply());
  assert.equal(await page.locator('#gameGrid .game').count(),8);
  await page.waitForFunction(expected=>document.querySelector('#gameGrid .game small span:first-child')?.textContent===expected,pack['Racing games'],{timeout:20000});
  await page.locator('#filters button').first().click();await page.evaluate(()=>SEEKVERA_I18N.apply());
  console.log('ALL_50_GAME_DESCRIPTIONS_AND_FILTER_LOGIC_PASS',l);
 }
 const reply='Réponse française sauvegardée';await page.evaluate(reply=>{const box=document.querySelector('#svGlobalMessages');const row=document.createElement('div');row.className='sv-global-msg bot';row.id='locale-preserved-reply';row.textContent=reply;box.appendChild(row)},reply);
 await page.evaluate(async()=>{SEEKVERA_LOCALE_R15.setLanguage('ha');await SEEKVERA_I18N.apply()});await page.waitForTimeout(600);
 assert.equal(await page.locator('#locale-preserved-reply').textContent(),reply);
 const initial='I’m the SEEKVERA AI assistant. Tell me what you need and I’ll help you find the right section, compare options or search worldwide.';
 const expected=fs.readFileSync('global-ui.js','utf8').match(/ha:"([^"]+)"/)[1];
 assert.equal(await page.locator('#svGlobalMessages .sv-global-msg.bot').first().textContent(),expected);
 console.log('LOCALIZED_HAUSA_INTRO_AND_SAVED_REPLY_PRESERVATION_PASS');
 const before=translationRequests;
 await page.evaluate(async()=>{const label=document.createElement('span');label.id='temporary-outage-test';label.textContent='Temporary translation outage test';document.body.appendChild(label);SEEKVERA_LOCALE_R15.setLanguage('fr');await SEEKVERA_I18N.apply();setTimeout(()=>{window.__translationOutageHeartbeat=true},300)});
 await page.waitForFunction(()=>window.__translationOutageHeartbeat,null,{timeout:5000});
 await page.waitForTimeout(1200);assert(translationRequests-before<=3,'translation outage must not spin or repeatedly send requests');
 console.log('TRANSLATION_OUTAGE_PAGE_RESPONSIVENESS_PASS');
}finally{await browser.close()}
