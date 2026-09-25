/* SEEKVERA R22 — deterministic category ownership; no mixed-language card DOM */
(()=>{'use strict';
if(window.__SEEKVERA_R22_CATEGORY_LOCK)return;window.__SEEKVERA_R22_CATEGORY_LOCK=true;
const EN_TITLES=['Marketplace','Travel','Flights','Hotels','Tourism','Property','Cars & Auto','Jobs','Shopping','Restaurants & Food','Local Services','Equipment & Machinery','Boats & Marine','Import & Export','Shipping & Logistics','Business Software','Software','Websites & Hosting','Solar & Energy','Education','Health','Money & Insurance','Entertainment','News & Media','Games','Connectivity','Free Wi‑Fi','AI Deal Agent','Everyday','Scan / QR','Promote / Business'];
const EN_DESC=['Buy, sell and compare worldwide','Trips, transport and stays','Search flight routes','Search stays worldwide','Places and experiences','Homes, land and rentals','Vehicles, parts and auto','Local and global careers','Products and deals','Food, cafes and dining','Everyday skilled help','Machines and equipment','Boats and marine listings','Factories and suppliers','Freight, cargo and delivery','POS, accounting and SaaS','Apps and digital tools','Domains, hosting and websites','Power and energy solutions','Schools, courses and skills','Clinics, labs and pharmacies','Licensed provider discovery','Movies, music and family','Trusted media and official sources','Play inside SEEKVERA','Internet, SIM and eSIM','Public Wi‑Fi discovery','Sourcing and business missions','Nearby daily needs','Share and install SEEKVERA','Business plans and promotion'];
function language(){let v=document.getElementById('lang')?.value||document.documentElement.lang||navigator.language||'en';if(v==='auto')v=navigator.language||'en';return String(v).toLowerCase().split('-')[0]||'en'}
function titles(l){const d=window.SEEKVERA_R14_CATEGORIES?.data?.[l];return Array.isArray(d)&&d.length>=31?d:EN_TITLES}
let running=false,pending=false;
function lock(){
  if(running){pending=true;return}running=true;pending=false;
  try{
    const l=language(), list=titles(l), tiles=[...document.querySelectorAll('#categories .r5-tile')];
    document.documentElement.setAttribute('translate','no');document.documentElement.classList.add('notranslate');
    document.body?.setAttribute('translate','no');document.body?.classList.add('notranslate');
    tiles.slice(0,31).forEach((tile,i)=>{
      const body=tile.querySelector('.r5-tile-body');if(!body)return;
      body.setAttribute('data-no-translate','1');body.setAttribute('translate','no');
      const title=String(list[i]||EN_TITLES[i]||'').trim();
      const wantDesc=l==='en'?EN_DESC[i]:'';
      const bs=[...body.children].filter(x=>x.tagName==='B');
      const ss=[...body.children].filter(x=>x.tagName==='SMALL');
      const ok=(l==='en'&&body.children.length===2&&bs.length===1&&ss.length===1&&bs[0].textContent.trim()===title&&ss[0].textContent.trim()===wantDesc)||(l!=='en'&&body.children.length===1&&bs.length===1&&bs[0].textContent.trim()===title);
      if(ok)return;
      const b=document.createElement('b');b.textContent=title;b.setAttribute('data-no-translate','1');
      if(l==='en'){const s=document.createElement('small');s.textContent=wantDesc;s.setAttribute('data-no-translate','1');body.replaceChildren(b,s)}
      else body.replaceChildren(b);
    });
    document.documentElement.dataset.svR22='ready';
  }finally{running=false;if(pending)queueMicrotask(lock)}
}
function schedule(){clearTimeout(schedule.t);schedule.t=setTimeout(lock,20)}
function setup(){
  if(!document.querySelector('meta[name="google"][content="notranslate"]')){const m=document.createElement('meta');m.name='google';m.content='notranslate';document.head?.appendChild(m)}
  const s=document.createElement('style');s.id='svR22Style';s.textContent='#categories .r5-tile-body{min-width:0!important;overflow:hidden!important}#categories .r5-tile-body>b{display:block!important;max-width:100%!important;overflow-wrap:anywhere!important;word-break:normal!important;line-height:1.12!important}html,body{overflow-x:hidden!important}';document.head?.appendChild(s);
  lock();
  const root=document.getElementById('categories')||document.documentElement;new MutationObserver(schedule).observe(root,{subtree:true,childList:true,characterData:true});
  document.addEventListener('change',e=>{if(e.target?.id==='lang'||e.target?.id==='country')schedule()},true);
  window.addEventListener('seekvera:localechange',schedule);
  [100,300,700,1500,3000].forEach(ms=>setTimeout(lock,ms));
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
window.SEEKVERA_R22_CATEGORY_LOCK={lock,EN_TITLES,EN_DESC};
})();
