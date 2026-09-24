/* SEEKVERA R21 — own translation, remove mixed-language category duplicates */
(()=>{'use strict';
if(window.__SEEKVERA_R21_CARD_CLEANUP)return;window.__SEEKVERA_R21_CARD_CLEANUP=true;
const EN_DESC=new Set([
'Buy, sell and compare worldwide','Trips, transport and stays','Search flight routes','Search stays worldwide','Places and experiences','Homes, land and rentals','Vehicles, parts and auto','Local and global careers','Products and deals','Food, cafes and dining','Everyday skilled help','Machines and equipment','Boats and marine listings','Factories and suppliers','Freight, cargo and delivery','POS, accounting and SaaS','Apps and digital tools','Domains, hosting and websites','Power and energy solutions','Schools, courses and skills','Clinics, labs and pharmacies','Licensed provider discovery','Movies, music and family','Trusted media and official sources','Play inside SEEKVERA','Internet, SIM and eSIM','Public Wi‑Fi discovery','Sourcing and business missions','Nearby daily needs','Share and install SEEKVERA','Business plans and promotion'
]);
const norm=s=>String(s||'').replace(/\s+/g,' ').trim();
function lang(){let v=document.getElementById('lang')?.value||document.documentElement.lang||navigator.language||'en';if(v==='auto')v=navigator.language||'en';return String(v).toLowerCase().split('-')[0]||'en'}
function blockBrowserTranslation(){
 document.documentElement.setAttribute('translate','no');document.documentElement.classList.add('notranslate');
 if(document.body){document.body.setAttribute('translate','no');document.body.classList.add('notranslate')}
 if(!document.querySelector('meta[name="google"][content="notranslate"]')){const m=document.createElement('meta');m.name='google';m.content='notranslate';document.head?.appendChild(m)}
}
function removeEnglishFromNode(node){
 if(lang()==='en')return;
 const w=document.createTreeWalker(node,NodeFilter.SHOW_TEXT);let n;
 while((n=w.nextNode())){
   let v=n.nodeValue||'',changed=false;
   for(const e of EN_DESC){if(v.includes(e)){v=v.split(e).join('');changed=true}}
   if(changed)n.nodeValue=v;
 }
}
function cleanBody(body){
 if(!body)return;
 const l=lang();
 const title=body.querySelector(':scope > b')||body.querySelector('b');
 const smalls=[...body.querySelectorAll(':scope > small')];
 // Category card markup is title + one description. Remove injected duplicate siblings.
 for(const child of [...body.children]){
   if(child===title||smalls.includes(child))continue;
   const t=norm(child.textContent);
   if(l!=='en'&&(EN_DESC.has(t)||[...EN_DESC].some(e=>t.includes(e))))child.remove();
 }
 if(l!=='en'){
   removeEnglishFromNode(body);
   // Keep only one visible translated description. Prefer the last non-empty/non-English one.
   const alive=[...body.querySelectorAll(':scope > small')];
   const good=alive.filter(s=>{const t=norm(s.textContent);return t&&![...EN_DESC].some(e=>t.includes(e))});
   const keep=good[good.length-1]||null;
   for(const s of alive){
     const t=norm(s.textContent);
     if(s!==keep||!t){s.hidden=true;s.setAttribute('aria-hidden','true')}
     else{s.hidden=false;s.removeAttribute('aria-hidden')}
   }
 }else{
   for(const s of smalls){s.hidden=false;s.removeAttribute('aria-hidden')}
 }
}
let running=false;
function clean(){
 if(running)return;running=true;
 try{
   blockBrowserTranslation();
   document.querySelectorAll('#categories .r5-tile-body').forEach(cleanBody);
   document.documentElement.dataset.svR21='ready';
 }finally{running=false}
}
function schedule(){requestAnimationFrame(()=>requestAnimationFrame(clean))}
function style(){if(document.getElementById('svR21Style'))return;const s=document.createElement('style');s.id='svR21Style';s.textContent=`
#categories .r5-tile-body{min-width:0!important;overflow:hidden!important}
#categories .r5-tile-body>b,#categories .r5-tile-body>small{max-width:100%!important;overflow-wrap:anywhere!important;word-break:normal!important}
#categories .r5-tile-body>small{font-weight:400!important}
html,body{overflow-x:hidden!important}
`;document.head?.appendChild(s)}
blockBrowserTranslation();style();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{clean();schedule()},{once:true});else{clean();schedule()}
const root=document.getElementById('categories')||document.documentElement;
new MutationObserver(schedule).observe(root,{subtree:true,childList:true,characterData:true});
document.addEventListener('change',e=>{if(e.target?.id==='lang'||e.target?.id==='country')schedule()},true);
window.addEventListener('seekvera:localechange',schedule);
[250,700,1500,3000,6000].forEach(ms=>setTimeout(clean,ms));
window.SEEKVERA_R21_CLEANUP={clean,englishDescriptions:[...EN_DESC]};
})();
