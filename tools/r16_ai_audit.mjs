import { chromium } from 'playwright';
import assert from 'node:assert';

const BASE=process.env.SEEKVERA_AUDIT_BASE||'http://127.0.0.1:4173';
const browser=await chromium.launch({headless:true});
let aiRequests=0;
try{
  const context=await browser.newContext({viewport:{width:360,height:800},locale:'en-US'});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('request',r=>{if(new URL(r.url()).pathname==='/api/ai')aiRequests++});
  if(BASE.startsWith('http://127.0.0.1')){
    await page.route('**/api/ui-translate',async r=>{
      let body={};try{body=r.request().postDataJSON()||{}}catch{}
      const strings=Array.isArray(body.strings)?body.strings:[];
      await r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,translations:strings})});
    });
    await page.route('**/api/ai',async r=>r.fulfill({status:503,contentType:'application/json',body:JSON.stringify({ok:false,error:'audit_should_not_call_ai'})}));
  }
  await page.goto(BASE+'/?r16ai='+Date.now(),{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.SEEKVERA_LOCALE_R15&&document.getElementById('aiChat')&&document.getElementById('aiChatInput'),null,{timeout:15000});
  await page.waitForFunction(()=>document.querySelectorAll('#country option').length>=248,null,{timeout:10000});
  await page.waitForTimeout(150);

  const snapshot=()=>page.evaluate(()=>{
    const s=SEEKVERA_LOCALE_R15.state();
    const chat=document.getElementById('aiChat'), form=document.getElementById('aiChatForm'), speaker=document.getElementById('aiChatSpeaker'), camera=document.getElementById('aiChatCamera'), mic=document.getElementById('aiChatMic'), send=form?.querySelector('.send');
    const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,display:getComputedStyle(e).display,vis:getComputedStyle(e).visibility}};
    const cr=rect(chat),fr=rect(form),sr=rect(speaker),car=rect(camera),mr=rect(mic),sendr=rect(send);
    const inside=r=>r.x>=cr.x-2&&r.right<=cr.right+2&&r.y>=cr.y-2&&r.bottom<=cr.bottom+2;
    return {state:s,lang:document.documentElement.lang,dir:document.documentElement.dir,chat:cr,form:fr,speaker:sr,camera:car,mic:mr,send:sendr,inside:[inside(sr),inside(car),inside(mr),inside(sendr)],overflowChat:chat.scrollWidth-chat.clientWidth,overflowForm:form.scrollWidth-form.clientWidth,speakerBefore:getComputedStyle(speaker,'::before').content,cameraBefore:getComputedStyle(camera,'::before').content,micBefore:getComputedStyle(mic,'::before').content,sendBefore:getComputedStyle(send,'::before').content,brand:document.querySelector('#aiChat .sv-chat-head b')?.textContent||'',observed:chat.dataset.r16Observed||''};
  });
  const assertAI=(q,label)=>{
    assert(q.chat.w>300,label+' chat width');
    for(const [i,r] of [q.speaker,q.camera,q.mic,q.send].entries()){
      assert(r.w>=40&&r.h>=40,label+' control '+i+' size');
      assert(r.display!=='none'&&r.vis!=='hidden',label+' control '+i+' hidden');
    }
    assert(q.inside.every(Boolean),label+' control escaped chat');
    assert(q.overflowChat<=2,label+' chat horizontal overflow '+q.overflowChat);
    assert(q.overflowForm<=2,label+' form horizontal overflow '+q.overflowForm);
    assert(q.speakerBefore.includes('🔊'),label+' speaker icon missing');
    assert(q.cameraBefore.includes('📷'),label+' camera icon missing');
    assert(q.micBefore.includes('🎤'),label+' mic icon missing');
    assert(q.sendBefore.includes('➤'),label+' send icon missing');
    assert(/SEEKVERA\s+AI/i.test(q.brand),label+' SEEKVERA AI brand was translated away');
    assert.equal(q.observed,'1',label+' AI stabilizer not active');
  };

  const data=await page.evaluate(()=>({profiles:SEEKVERA_LOCALE_R15.profiles,langs:Object.keys(SEEKVERA_LOCALE_R15.languagePrimary)}));
  let countries=0;
  for(const [cc,p] of Object.entries(data.profiles)){
    await page.evaluate(cc=>SEEKVERA_LOCALE_R15.setCountry(cc),cc);
    const q=await snapshot();
    assert.deepEqual([q.state.country,q.state.language,q.state.currency],[cc,p.language,p.currency],cc+' locale state');
    assert.equal(q.lang,p.language,cc+' html lang');
    assertAI(q,cc);
    countries++;
  }
  assert.equal(countries,248,'all countries not checked');

  let languages=0;
  for(const lg of data.langs){
    await page.evaluate(lg=>SEEKVERA_LOCALE_R15.setLanguage(lg),lg);
    const q=await snapshot();assert.equal(q.state.language,lg,lg+' language state');assertAI(q,'lang '+lg);languages++;
  }
  assert.equal(languages,98,'all languages not checked');

  // Every country must be switchable by a normal AI command without consuming /api/ai.
  for(const cc of Object.keys(data.profiles)){
    await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('US'));
    const name=await page.evaluate(cc=>new Intl.DisplayNames(['en'],{type:'region'}).of(cc),cc);
    await page.evaluate(({name})=>{const i=document.getElementById('aiChatInput'),f=document.getElementById('aiChatForm');i.value='switch to '+name;f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));},{name});
    const got=await page.evaluate(()=>SEEKVERA_LOCALE_R15.state().country);
    assert.equal(got,cc,'AI command failed for '+cc+' '+name);
  }
  assert.equal(aiRequests,0,'country control leaked into paid/quota AI calls');

  // Exact regression reported by the user.
  for(const phrase of ['switch to Lebanon','Lebanon','Up Control, Lebanon']){
    await page.evaluate(()=>SEEKVERA_LOCALE_R15.setCountry('IN'));
    await page.evaluate(phrase=>{const i=document.getElementById('aiChatInput'),f=document.getElementById('aiChatForm');i.value=phrase;f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));},phrase);
    const q=await snapshot();assert.deepEqual([q.state.country,q.state.language,q.state.currency],['LB','ar','LBP'],phrase+' did not switch to Lebanon');assertAI(q,phrase);
  }

  // Stability/no-shake proof on the scripts from the screenshots plus RTL.
  for(const lg of ['hi','ar','nl','fil','zh','ja','ru','ur','bn','am']){
    await page.evaluate(lg=>SEEKVERA_LOCALE_R15.setLanguage(lg),lg);
    await page.waitForTimeout(120);
    const series=[];
    for(let i=0;i<10;i++){await page.waitForTimeout(70);const q=await snapshot();series.push([q.chat.x,q.chat.w,q.form.x,q.form.y,q.form.w,q.speaker.x,q.speaker.y].map(v=>Math.round(v)).join('|'));assertAI(q,'stable '+lg)}
    assert.equal(new Set(series).size,1,'AI UI shifted/shook in '+lg+': '+series.join(','));
  }

  // Speaker interaction path: visible control must be clickable after an AI response event.
  await page.evaluate(()=>{window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:'SEEKVERA voice check',language:'en'}}));document.getElementById('aiChatSpeaker').click()});
  await page.waitForTimeout(80);
  assertAI(await snapshot(),'speaker click');

  if(errors.length)throw new Error('Page errors: '+errors.join(' | '));
  console.log(`R16 AI PASS: ${countries} countries; ${languages} languages; 248 direct country commands; Lebanon regression; stable AI card; speaker/camera/mic/send contained; zero /api/ai calls for country control`);
  await context.close();
}finally{await browser.close();}
