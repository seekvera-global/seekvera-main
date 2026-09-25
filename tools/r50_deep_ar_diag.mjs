import {chromium} from 'playwright';
const B='https://seekveraglobal.com';
const browser=await chromium.launch({headless:true});
const ctx=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'});
async function inspect(path,needles){
 const p=await ctx.newPage();await p.route('**/api/ui-translate',r=>r.abort());await p.route('https://text.pollinations.ai/**',r=>r.abort());
 await p.goto(B+'/'+path+'?r50='+Date.now(),{waitUntil:'domcontentloaded',timeout:45000});
 await p.waitForFunction(()=>window.SEEKVERA_I18N_R32&&window.SEEKVERA_LOCALE_R15,{timeout:15000});
 await p.evaluate(()=>SEEKVERA_LOCALE_R15.setLanguage('ar'));
 await p.evaluate(async()=>{await SEEKVERA_I18N_R32.loadPack('ar');SEEKVERA_I18N_R32.schedule(0)});
 await p.waitForTimeout(500);
 const out=await p.evaluate(needles=>{
   const rows=[];for(const el of document.querySelectorAll('body *')){const own=[...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.nodeValue||'').join(' ').trim();if(!own)continue;for(const q of needles)if(own.includes(q))rows.push({q,tag:el.tagName,id:el.id,cls:el.className,text:own.slice(0,300),html:el.outerHTML.slice(0,700)})}
   return {ready:document.documentElement.dataset.seekveraI18nReady,pack:document.documentElement.dataset.seekveraPackReady,rows};
 },needles);
 console.log('PAGE',path,JSON.stringify(out));await p.close();
}
await inspect('marketplace.html',['Cars & Auto','Solar & Energy','Import & Export','Fashion & Beauty','Shipping & Logistics']);
await inspect('deal-agent.html',['Deal Agent','Not signed in.']);
const pack=await (await ctx.request.get(B+'/i18n-r32/ar.json?r50='+Date.now())).json();
for(const k of ['Cars & Auto','Solar & Energy','Import & Export','Fashion & Beauty','Shipping & Logistics','Deal Agent','Not signed in.','Not signed in. Deal Agent remains OFF by default.','AI DEAL AGENT','SEEKVERA Deal Agent · Server records are private per authenticated owner.'])console.log('PACK',JSON.stringify([k,pack.translations?.[k]??null]));
await browser.close();
