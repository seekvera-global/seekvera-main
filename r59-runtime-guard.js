(()=>{'use strict';
const RELEASE='20260926-r59-one-runtime';
document.documentElement.dataset.seekveraRelease=RELEASE;
function cleanVisualState(){document.documentElement.classList.remove('sv-r31-switching');try{document.body?.classList.remove('sv-r31-switching')}catch{}}
window.addEventListener('pageshow',cleanVisualState);document.addEventListener('visibilitychange',()=>{if(!document.hidden)cleanVisualState()});
if('serviceWorker' in navigator){
  const install=()=>navigator.serviceWorker.register('/sw.js?v='+RELEASE,{updateViaCache:'none'}).then(async r=>{try{await r.update()}catch{}if(r.waiting)try{r.waiting.postMessage('SKIP_WAITING')}catch{}}).catch(()=>{});
  if(document.readyState==='complete')install();else window.addEventListener('load',install,{once:true});
}
window.SEEKVERA_RELEASE=RELEASE;
})();
