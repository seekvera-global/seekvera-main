/* SEEKVERA R23 — stability guard. No DOM mutation polling; one owner per UI concern. */
(()=>{'use strict';
if(window.__SEEKVERA_R23_STABILITY)return;window.__SEEKVERA_R23_STABILITY=true;
// Disable the legacy broad R9 mutation observer before i18n-ui.js loads.
window.__seekveraLocaleGuardR9=true;
const VERSION='20260925-r23-stable';
let timer=0,raf=0;
function installStyle(){
  if(document.getElementById('svR23Stability'))return;
  const s=document.createElement('style');s.id='svR23Stability';s.textContent=`
html,body{max-width:100%;overflow-x:hidden!important;-webkit-text-size-adjust:100%;text-size-adjust:100%}
html{scrollbar-gutter:stable}
body{overflow-anchor:none}
.r5-shell,.r5-main,.r5-market,.r5-center,#categories,.r5-grid,#aiChat,.sv-unified-chat{min-width:0!important;max-width:100%!important}
#categories .r5-tile{min-width:0!important;width:100%!important;overflow:hidden!important;contain:layout paint!important}
#categories .r5-tile-body{min-width:0!important;overflow:hidden!important}
#categories .r5-tile-body>b,#categories .r5-tile-body>small{max-width:100%!important;overflow-wrap:anywhere!important;word-break:normal!important}
#aiChat,.sv-unified-chat{min-width:0!important;max-width:100%!important;overflow-x:hidden!important;contain:layout!important;overflow-anchor:none!important}
#aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{overflow-anchor:none!important;scroll-behavior:auto!important}
html.sv-r15-applying *,html.sv-r23-applying *{animation:none!important;transition:none!important}
@media(max-width:780px){#categories .r5-tile,#aiChat,.sv-unified-chat{transform:none!important}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;scroll-behavior:auto!important;transition-duration:.01ms!important}}
`;
  document.head.appendChild(s);
}
function apply(){
  installStyle();
  document.documentElement.dataset.svR20='ready';
  document.documentElement.dataset.svR23='stable';
  document.documentElement.classList.add('sv-r23-applying');
  cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>requestAnimationFrame(()=>document.documentElement.classList.remove('sv-r23-applying')));
  try{window.SEEKVERA_R22_CATEGORY_LOCK?.schedule?.(24)}catch{}
}
function schedule(ms=60){clearTimeout(timer);timer=setTimeout(apply,ms)}
function bind(){
  installStyle();schedule(0);schedule(220);
  window.addEventListener('pageshow',()=>schedule(20));
  window.addEventListener('load',()=>schedule(20),{once:true});
  window.addEventListener('seekvera:languagechange',()=>schedule(40));
  window.addEventListener('seekvera:countrychange',()=>schedule(40));
  window.addEventListener('orientationchange',()=>schedule(120));
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
window.SEEKVERA_R20_FINAL={version:VERSION,apply,schedule,descriptions:[],extraLanguages:[]};
})();
