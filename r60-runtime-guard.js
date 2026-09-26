(()=>{'use strict';
const RELEASE='20260926-r60-chat-voice-persist';
const CHAT_KEY='seekvera_ai_chat_v1';
const CHAT_MAX=80;
document.documentElement.dataset.seekveraRelease=RELEASE;
function cleanVisualState(){document.documentElement.classList.remove('sv-r31-switching');try{document.body?.classList.remove('sv-r31-switching')}catch{}}
function box(){return document.querySelector('#aiMessages')}
function safeRead(){try{const x=JSON.parse(localStorage.getItem(CHAT_KEY)||'[]');return Array.isArray(x)?x:[]}catch{return[]}}
function saveChat(){const b=box();if(!b)return;const rows=[...b.querySelectorAll('.ai-msg')].filter(n=>!n.classList.contains('thinking')).map(n=>({role:n.classList.contains('user')?'user':'assistant',text:String(n.textContent||'').trim()})).filter(x=>x.text).slice(-CHAT_MAX);if(!rows.length)return;try{localStorage.setItem(CHAT_KEY,JSON.stringify(rows))}catch{}}
function restoreChat(){const b=box(),rows=safeRead();if(!b||!rows.length)return false;b.innerHTML='';for(const x of rows){const m=document.createElement('div');m.className='ai-msg '+(x.role==='user'?'user':'bot');m.dataset.persisted='1';m.textContent=String(x.text||'').slice(0,4000);b.appendChild(m)}b.scrollTop=b.scrollHeight;return true}
let saveTimer=0;
function scheduleSave(){clearTimeout(saveTimer);saveTimer=setTimeout(saveChat,80)}
function watchChat(){const b=box();if(!b)return;restoreChat();new MutationObserver(scheduleSave).observe(b,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['class']});window.addEventListener('seekvera:ai-response',saveChat);window.addEventListener('pagehide',saveChat)}
function enableVoiceMode(){try{localStorage.setItem('seekvera_voice_mode','1');localStorage.setItem('seekvera_voice_muted','0')}catch{}try{speechSynthesis.resume()}catch{}}
document.addEventListener('pointerdown',e=>{if(e.target.closest?.('#aiChatMic,.sv-global-compose .mic'))enableVoiceMode()},{capture:true});
window.addEventListener('pageshow',()=>{cleanVisualState();setTimeout(()=>{if(box()&&safeRead().length)restoreChat()},0)});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)cleanVisualState()});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',watchChat,{once:true});else watchChat();
if('serviceWorker' in navigator){const install=()=>navigator.serviceWorker.register('/sw.js?v='+RELEASE,{updateViaCache:'none'}).then(async r=>{try{await r.update()}catch{}if(r.waiting)try{r.waiting.postMessage('SKIP_WAITING')}catch{}}).catch(()=>{});if(document.readyState==='complete')install();else window.addEventListener('load',install,{once:true})}
window.SEEKVERA_RELEASE=RELEASE;
window.SEEKVERA_CHAT={save:saveChat,restore:restoreChat,clear:()=>{try{localStorage.removeItem(CHAT_KEY)}catch{}const b=box();if(b)b.innerHTML=''}};
})();
