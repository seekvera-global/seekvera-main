import {chromium} from 'playwright';
const B='https://seekveraglobal.com';
const browser=await chromium.launch({headless:true});
const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
const page=await ctx.newPage();
await page.goto(B+'/?r47='+Date.now(),{waitUntil:'domcontentloaded',timeout:45000});
await page.waitForFunction(()=>window.SEEKVERA_I18N_R32&&window.SEEKVERA_LOCALE_R15&&window.SEEKVERA_R22_CATEGORY_LOCK,{timeout:20000});
await page.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('xh'));
await page.evaluate(async()=>{await SEEKVERA_I18N_R32.loadPack('xh');SEEKVERA_I18N_R32.schedule(0);SEEKVERA_R22_CATEGORY_LOCK.lock()});
async function snap(label,ms){
  await page.waitForTimeout(ms);
  const x=await page.evaluate(()=>{
    const hits=[];
    const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
    while((n=w.nextNode())) if((n.nodeValue||'').includes('Live marketplace')){
      const e=n.parentElement;hits.push({text:n.nodeValue.trim(),tag:e?.tagName,id:e?.id,cls:e?.className,outer:e?.outerHTML?.slice(0,500)});
    }
    return {lang:document.querySelector('#lang')?.value,ready:document.documentElement.dataset.seekveraI18nReady,pack:document.documentElement.dataset.seekveraPackReady,hits,bodyHas:document.body.innerText.includes('Live marketplace')};
  });
  console.log(label,JSON.stringify(x));
}
await snap('T45',45);await snap('T150',105);await snap('T500',350);await snap('T1500',1000);
await browser.close();
