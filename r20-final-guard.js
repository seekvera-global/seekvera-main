/* SEEKVERA R20 final multilingual UI + mobile stability guard */
(()=>{'use strict';
if(window.__SEEKVERA_R20_FINAL_GUARD)return;window.__SEEKVERA_R20_FINAL_GUARD=true;
const VERSION='20260925-r20';
const EN_DESC=new Set([
'Buy, sell and compare worldwide','Trips, transport and stays','Search flight routes','Search stays worldwide','Places and experiences','Homes, land and rentals','Vehicles, parts and auto','Local and global careers','Products and deals','Food, cafes and dining','Everyday skilled help','Machines and equipment','Boats and marine listings','Factories and suppliers','Freight, cargo and delivery','POS, accounting and SaaS','Apps and digital tools','Domains, hosting and websites','Power and energy solutions','Schools, courses and skills','Clinics, labs and pharmacies','Licensed provider discovery','Movies, music and family','Trusted media and official sources','Play inside SEEKVERA','Internet, SIM and eSIM','Public Wi‑Fi discovery','Sourcing and business missions','Nearby daily needs','Share and install SEEKVERA','Business plans and promotion'
]);
const SKIP_EN=new Set(['SEEKVERA','AI','QR','Wi‑Fi','SIM','eSIM','POS','SaaS']);
const sourceText=new WeakMap();
let timer=0;
function lang(){let v=document.querySelector('.sv-controls select#lang,select#lang.sv-select')?.value||localStorage.getItem('seekvera_lang')||document.documentElement.lang||navigator.language||'en';if(v==='auto')v=navigator.language||'en';return String(v).toLowerCase().split(/[-_]/)[0]||'en'}
function remember(root=document){const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){const p=n.parentElement;if(!p||p.closest('script,style,noscript,code,pre,svg,#aiMessages,#aiResult,.ai-msg,.sv-ai-answer,.sv-ai-actions,#liveListings'))continue;const s=(n.nodeValue||'').trim();if(s&&!sourceText.has(n))sourceText.set(n,s)}}
function titleData(){return window.SEEKVERA_R14_CATEGORIES?.data||null}
function fixCategories(){
 const l=lang(),data=titleData(),tiles=[...document.querySelectorAll('#categories .r5-tile')];
 if(l!=='en'&&data?.[l]){for(let i=0;i<tiles.length&&i<data[l].length;i++){const b=tiles[i].querySelector('.r5-tile-body>b');if(b&&data[l][i])b.textContent=data[l][i]}}
 for(const tile of tiles){
  const small=tile.querySelector('.r5-tile-body>small');if(!small)continue;
  const t=(small.textContent||'').trim();
  const unresolved=l!=='en'&&(!t||t==='…'||EN_DESC.has(t));
  small.hidden=unresolved;small.classList.toggle('sv-r20-untranslated',unresolved);
  if(unresolved)small.setAttribute('aria-hidden','true');else small.removeAttribute('aria-hidden');
 }
}
function fixStaticLeaks(){
 const l=lang();if(l==='en')return;
 document.querySelectorAll('.r5-section-head,.r5-ai-note,.r5-foot,.r5-kicker,.r5-scope,.r5-right-box').forEach(root=>{
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){
   const original=sourceText.get(n),now=(n.nodeValue||'').trim();if(!original||!now||now!==original||SKIP_EN.has(now))continue;
   if(!/[A-Za-z]{3}/.test(now))continue;
   if(EN_DESC.has(now)){n.nodeValue='';continue}
  }
 });
}
function injectStyle(){if(document.getElementById('svR20FinalStyle'))return;const s=document.createElement('style');s.id='svR20FinalStyle';s.textContent=`
html,body{overflow-x:hidden!important}
#categories .r5-grid{align-items:stretch!important}
#categories .r5-tile{min-width:0!important;width:100%!important;height:100%!important;overflow:hidden!important;contain:layout paint!important}
#categories .r5-tile-body{min-width:0!important;overflow:hidden!important;padding:7px 8px!important}
#categories .r5-tile-body>b,#categories .r5-tile-body>small{max-width:100%!important;overflow-wrap:anywhere!important;word-break:normal!important;hyphens:auto!important}
#categories .r5-tile-body>b{font-size:clamp(10.5px,3.1vw,14px)!important;line-height:1.18!important;display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;overflow:hidden!important;min-height:2.36em!important}
#categories .r5-tile-body>small{font-size:clamp(9px,2.45vw,11px)!important;line-height:1.22!important;display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;overflow:hidden!important;min-height:2.44em!important}
#categories .r5-tile-body>small[hidden],#categories .sv-r20-untranslated{display:none!important;min-height:0!important}
#aiChat,.sv-unified-chat{overflow:hidden!important;overscroll-behavior:contain!important;overflow-anchor:none!important}
#aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{height:auto!important;min-height:86px!important;max-height:170px!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;overflow-anchor:none!important;scroll-behavior:auto!important}
#aiChat .ai-msg,.sv-unified-chat .ai-msg{overflow-wrap:anywhere!important;word-break:break-word!important;max-width:94%!important}
@media(max-width:780px){
 #aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{height:auto!important;min-height:82px!important;max-height:128px!important}
 #aiChatSpeaker,.sv-global-speaker{width:46px!important;min-width:46px!important;max-width:46px!important;height:46px!important;min-height:46px!important}
 #categories .r5-tile-body{min-height:48px!important}
}
@media(max-width:390px){#aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{max-height:118px!important}}
`;document.head.appendChild(s)}
function apply(){injectStyle();fixCategories();fixStaticLeaks();document.documentElement.dataset.svR20='ready'}
function schedule(ms=60){clearTimeout(timer);timer=setTimeout(apply,ms)}
function bind(){remember(document);injectStyle();schedule(0);schedule(250);schedule(900);document.addEventListener('change',e=>{if(e.target?.id==='lang'||e.target?.id==='country'){schedule(30);schedule(350);schedule(1000)}},true);window.addEventListener('seekvera:languagechange',()=>schedule(40));window.addEventListener('seekvera:countrychange',()=>schedule(40));window.addEventListener('pageshow',()=>schedule(50));new MutationObserver(ms=>{let dirty=false;for(const m of ms){if(m.type==='characterData'||m.addedNodes?.length){dirty=true;for(const n of m.addedNodes||[])if(n.nodeType===1)remember(n)}}if(dirty)schedule(90)}).observe(document.documentElement,{subtree:true,childList:true,characterData:true})}
if(document.readyState==='loading'){remember(document);document.addEventListener('DOMContentLoaded',bind,{once:true})}else bind();
window.SEEKVERA_R20_FINAL={version:VERSION,apply,schedule,descriptions:[...EN_DESC]};
})();
