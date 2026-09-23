const {chromium,webkit,devices}=require('playwright');
const SITE='https://seekveraglobal.com';
const assert=(v,m)=>{if(!v)throw new Error(m)};
const profiles=[
  ['Android Chrome',chromium,devices['Pixel 5']],
  ['iPhone Safari',webkit,devices['iPhone 13']]
];
function overlap(a,b){return !(a.right<=b.left||b.right<=a.left||a.bottom<=b.top||b.bottom<=a.top)}
(async()=>{
 for(const [name,engine,dev] of profiles){
  const browser=await engine.launch({headless:true});
  const ctx=await browser.newContext({...dev});
  const page=await ctx.newPage();
  const errs=[];page.on('pageerror',e=>errs.push(String(e)));
  await page.goto(SITE+'/?r5b2-visual='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>document.querySelector('#country')?.options?.length>=249&&document.querySelector('#lang')?.options?.length===29,null,{timeout:60000});
  await page.waitForTimeout(600);
  await page.selectOption('#lang','pt');
  await page.dispatchEvent('#lang','change');
  await page.waitForFunction(()=>document.documentElement.lang.toLowerCase().startsWith('pt'),null,{timeout:15000});
  await page.waitForFunction(()=>/Encontre mais rápido/i.test(document.querySelector('.r5-hero h1')?.textContent||''),null,{timeout:10000});
  await page.waitForTimeout(500);
  const s=await page.evaluate(()=>{
    const r=e=>{const x=e.getBoundingClientRect();return {left:x.left,right:x.right,top:x.top,bottom:x.bottom,width:x.width,height:x.height}};
    const cs=e=>getComputedStyle(e);
    const country=document.querySelector('#country'),lang=document.querySelector('#lang'),currency=document.querySelector('#currency');
    const h1=document.querySelector('.r5-hero h1');
    const bot=document.querySelector('#aiMessages .ai-msg.bot:first-child');
    const input=document.querySelector('#aiChatInput');
    return {
      viewport:innerWidth,
      overflow:Math.max(0,document.documentElement.scrollWidth-innerWidth),
      leftDisplay:cs(document.querySelector('.r5-left')).display,
      rightDisplay:cs(document.querySelector('.r5-right')).display,
      attachDisplay:cs(document.querySelector('#aiChatAttach')).display,
      aiNoteDisplay:cs(document.querySelector('.r5-ai-note')).display,
      country:r(country),lang:r(lang),currency:r(currency),input:r(input),
      header:r(document.querySelector('.r5-top')),
      hero:r(document.querySelector('.r5-hero')),
      h1Text:h1.textContent.trim(),
      h1Font:parseFloat(cs(h1).fontSize),
      langCode:document.documentElement.lang,
      botRaw:bot.textContent.trim(),
      botFont:parseFloat(cs(bot).fontSize),
      tiles:[...document.querySelectorAll('.r5-tile')].slice(0,6).map(x=>r(x)),
      labelsVisible:[...document.querySelectorAll('.r5-controls small,.r5-controls .sv-control-caption')].some(x=>cs(x).display!=='none'&&r(x).height>0)
    };
  });
  console.log(name,s);
  assert(s.overflow<=2,name+' horizontal overflow '+s.overflow);
  assert(s.leftDisplay==='none'&&s.rightDisplay==='none',name+' desktop rails still visible on mobile');
  assert(s.attachDisplay==='none',name+' attach still squeezes composer');
  assert(s.aiNoteDisplay==='none',name+' long AI note still visible');
  assert(!s.labelsVisible,name+' mixed-language control captions still visible');
  assert(s.input.width>=150,name+' chat input too narrow '+s.input.width);
  assert(s.header.height<=155,name+' header too tall '+s.header.height);
  assert(!overlap(s.country,s.lang)&&!overlap(s.lang,s.currency)&&!overlap(s.country,s.currency),name+' top selectors overlap');
  assert(/Encontre mais rápido\. Compare melhor\./i.test(s.h1Text),name+' Portuguese hero not localized: '+s.h1Text);
  assert(s.h1Font>=24,name+' hero accidentally hidden');
  assert(/SEEKVERA/i.test(s.botRaw)&&/(assistente|IA)/i.test(s.botRaw),name+' Portuguese AI intro not localized: '+s.botRaw);
  assert(s.botFont>=12,name+' AI intro accidentally hidden');
  assert(s.tiles.length>=6&&s.tiles.every(t=>t.width>100&&t.height>80),name+' marketplace tiles collapsed');
  assert(!errs.length,name+' page errors '+errs.join(' | '));
  console.log('R5B2_VISUAL_PASS',name);
  await browser.close();
 }
 console.log('SEEKVERA_R5B2_ANDROID_IPHONE_VISUAL_PASS');
})().catch(e=>{console.error(e);process.exit(1)});
