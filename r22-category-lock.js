/* SEEKVERA R23 category lock — deterministic, event-driven, zero mutation polling. */
(()=>{'use strict';
if(window.__SEEKVERA_R22_CATEGORY_LOCK)return;window.__SEEKVERA_R22_CATEGORY_LOCK=true;
const VERSION='20260925-r23-category';
const EN_TITLES=['Marketplace','Travel','Flights','Hotels','Tourism','Property','Cars & Auto','Jobs','Shopping','Restaurants & Food','Local Services','Equipment & Machinery','Boats & Marine','Import & Export','Shipping & Logistics','Business Software','Software','Websites & Hosting','Solar & Energy','Education','Health','Money & Insurance','Entertainment','News & Media','Games','Connectivity','Free Wi‑Fi','AI Deal Agent','Everyday','Scan / QR','Promote / Business'];
const EN_DESC=['Buy, sell and compare worldwide','Trips, transport and stays','Search flight routes','Search stays worldwide','Places and experiences','Homes, land and rentals','Vehicles, parts and auto','Local and global careers','Products and deals','Food, cafes and dining','Everyday skilled help','Machines and equipment','Boats and marine listings','Factories and suppliers','Freight, cargo and delivery','POS, accounting and SaaS','Apps and digital tools','Domains, hosting and websites','Power and energy solutions','Schools, courses and skills','Clinics, labs and pharmacies','Licensed provider discovery','Movies, music and family','Trusted media and official sources','Play inside SEEKVERA','Internet, SIM and eSIM','Public Wi‑Fi discovery','Sourcing and business missions','Nearby daily needs','Share and install SEEKVERA','Business plans and promotion'];
let timer=0,running=false,pending=false;
function language(){let v=document.querySelector('.sv-controls select#lang,select#lang.sv-select,#lang')?.value||localStorage.getItem('seekvera_lang')||document.documentElement.lang||navigator.language||'en';if(v==='auto')v=navigator.language||'en';return String(v).toLowerCase().split(/[-_]/)[0]||'en'}
function titles(l){const d=window.SEEKVERA_R14_CATEGORIES?.data?.[l];return Array.isArray(d)&&d.length>=31?d:EN_TITLES}
function stableBody(body,title,desc,l){
  body.setAttribute('data-no-translate','1');body.setAttribute('data-no-i18n','1');body.setAttribute('translate','no');
  const children=[...body.children],bs=children.filter(x=>x.tagName==='B'),ss=children.filter(x=>x.tagName==='SMALL');
  if(l==='en'){
    const exact=children.length===2&&bs.length===1&&ss.length===1&&bs[0].textContent.trim()===title&&ss[0].textContent.trim()===desc;
    if(exact)return;
    const b=bs[0]||document.createElement('b'),s=ss[0]||document.createElement('small');b.textContent=title;s.textContent=desc;b.setAttribute('data-no-translate','1');s.setAttribute('data-no-translate','1');body.replaceChildren(b,s);return;
  }
  const exact=children.length===1&&bs.length===1&&bs[0].textContent.trim()===title;
  if(exact)return;
  const b=bs[0]||document.createElement('b');b.textContent=title;b.setAttribute('data-no-translate','1');b.setAttribute('data-no-i18n','1');body.replaceChildren(b);
}
function lock(){
  if(running){pending=true;return}running=true;pending=false;
  try{
    const l=language(),list=titles(l),tiles=[...document.querySelectorAll('#categories .r5-tile')].slice(0,31);
    document.documentElement.setAttribute('translate','no');document.documentElement.classList.add('notranslate');
    tiles.forEach((tile,i)=>{const body=tile.querySelector('.r5-tile-body');if(body)stableBody(body,String(list[i]||EN_TITLES[i]||'').trim(),EN_DESC[i]||'',l)});
    document.documentElement.dataset.svR22='ready';document.documentElement.dataset.svR23Category='stable';
  }finally{running=false;if(pending)schedule(30)}
}
function schedule(ms=48){clearTimeout(timer);timer=setTimeout(lock,ms)}
function hookCategoryEngine(){
  const c=window.SEEKVERA_R14_CATEGORIES;if(!c||c.__r23Hooked)return false;
  const original=typeof c.apply==='function'?c.apply.bind(c):null;if(!original)return false;
  c.apply=(...args)=>{const result=original(...args);schedule(20);return result};c.__r23Hooked=true;return true;
}
function bind(){
  hookCategoryEngine();schedule(0);schedule(180);schedule(650);
  document.addEventListener('change',e=>{if(['lang','country','currency'].includes(e.target?.id))schedule(45)},true);
  window.addEventListener('pageshow',()=>schedule(30));window.addEventListener('seekvera:languagechange',()=>schedule(30));window.addEventListener('seekvera:countrychange',()=>schedule(30));
  let tries=0;const t=setInterval(()=>{tries++;if(hookCategoryEngine()||tries>20)clearInterval(t)},100);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
window.SEEKVERA_R22_CATEGORY_LOCK={version:VERSION,lock,schedule};
})();
