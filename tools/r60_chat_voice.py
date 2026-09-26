from pathlib import Path
import re

VER='20260926-r60-chat-voice-persist'

# -----------------------------------------------------------------------------
# 1) One release across every HTML entry point.
# -----------------------------------------------------------------------------
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    s=p.read_text(encoding='utf-8')
    s=re.sub(r'superapp\.js(?:\?v=[^"\'<> ]*)?',f'superapp.js?v={VER}',s)
    s=re.sub(r'voice-ai\.js(?:\?v=[^"\'<> ]*)?',f'voice-ai.js?v={VER}',s)
    s=re.sub(r'r31-ui-polish\.js(?:\?v=[^"\'<> ]*)?',f'r31-ui-polish.js?v={VER}',s)
    s=re.sub(r'sw\.js\?v=[^"\'<> )]+',f'sw.js?v={VER}',s)
    s=s.replace('r59-runtime-guard.js','r60-runtime-guard.js')
    s=re.sub(r'r60-runtime-guard\.js(?:\?v=[^"\'<> ]*)?',f'r60-runtime-guard.js?v={VER}',s)
    if 'r60-runtime-guard.js' not in s:
        s=s.replace('</body>',f'<script src="/r60-runtime-guard.js?v={VER}" defer data-no-i18n="1"></script></body>',1)
    if 'voice-ai.js' not in s:
        s=s.replace('</body>',f'<script src="/voice-ai.js?v={VER}" defer data-no-i18n="1"></script></body>',1)
    if 'r31-ui-polish.js' not in s:
        s=s.replace('</body>',f'<script src="/r31-ui-polish.js?v={VER}" defer data-no-i18n="1"></script></body>',1)
    if 'data-release=' in s:
        s=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',s,count=1)
    p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) Persistent chat + release guard.
#    The chat is device-local (localStorage), survives reload/back/category routing,
#    and is shared by the same SEEKVERA runtime regardless of country/language.
# -----------------------------------------------------------------------------
Path('r60-runtime-guard.js').write_text(r'''(()=>{'use strict';
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
function watchChat(){const b=box();if(!b)return;restoreChat();new MutationObserver(scheduleSave).observe(b,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['class']});window.addEventListener('seekvera:ai-response',()=>setTimeout(saveChat,40));window.addEventListener('pagehide',saveChat)}
function enableVoiceMode(){try{localStorage.setItem('seekvera_voice_mode','1');localStorage.setItem('seekvera_voice_muted','0')}catch{}try{speechSynthesis.resume()}catch{}}
document.addEventListener('pointerdown',e=>{if(e.target.closest?.('#aiChatMic,.sv-global-compose .mic'))enableVoiceMode()},{capture:true});
window.addEventListener('pageshow',()=>{cleanVisualState();setTimeout(()=>{if(box()&&safeRead().length)restoreChat()},0)});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)cleanVisualState()});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',watchChat,{once:true});else watchChat();
if('serviceWorker' in navigator){const install=()=>navigator.serviceWorker.register('/sw.js?v='+RELEASE,{updateViaCache:'none'}).then(async r=>{try{await r.update()}catch{}if(r.waiting)try{r.waiting.postMessage('SKIP_WAITING')}catch{}}).catch(()=>{});if(document.readyState==='complete')install();else window.addEventListener('load',install,{once:true})}
window.SEEKVERA_RELEASE=RELEASE;
window.SEEKVERA_CHAT={save:saveChat,restore:restoreChat,clear:()=>{try{localStorage.removeItem(CHAT_KEY)}catch{}const b=box();if(b)b.innerHTML=''}};
})();
''',encoding='utf-8')

# Non-intercepting SW remains intentional: no blank/back delays caused by SW fetch.
Path('sw.js').write_text(r'''const RELEASE='20260926-r60-chat-voice-persist';
self.addEventListener('install',e=>{e.waitUntil(self.skipWaiting())});
self.addEventListener('activate',e=>{e.waitUntil((async()=>{for(const k of await caches.keys())await caches.delete(k);await self.clients.claim()})())});
self.addEventListener('message',e=>{if(e.data==='SKIP_WAITING')self.skipWaiting()});
''',encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Global voice mode: once the user talks, every AI answer is spoken in the
#    answer language until they explicitly mute it. All 98 configured languages use
#    the exact same engine and locale resolver.
# -----------------------------------------------------------------------------
p=Path('voice-ai.js');s=p.read_text(encoding='utf-8')
old="function enableVoiceConversation(){voiceConversation=true;voiceReplyDeadline=Date.now()+90000;muted=false;localStorage.setItem('seekvera_voice_muted','0');updateSpeakerButtons();unlockTTS()}"
new="function enableVoiceConversation(){voiceConversation=true;voiceReplyDeadline=Date.now()+90000;muted=false;localStorage.setItem('seekvera_voice_muted','0');localStorage.setItem('seekvera_voice_mode','1');updateSpeakerButtons();unlockTTS()}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R60 enableVoiceConversation anchor missing')

# Android should also use the best matching installed/network voice when available.
old="const android=/Android/i.test(navigator.userAgent);const v=android?null:pickVoice(lastLocale);if(v)u.voice=v;"
new="const v=pickVoice(lastLocale);if(v)u.voice=v;"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R60 Android voice selection anchor missing')

old="window.addEventListener('seekvera:ai-response',e=>{const auto=voiceConversation||Date.now()<voiceReplyDeadline;if(auto)voiceReplyDeadline=0;speak(e.detail?.text,e.detail?.language,auto)});"
new="window.addEventListener('seekvera:ai-response',e=>{const voiceMode=localStorage.getItem('seekvera_voice_mode')==='1',auto=voiceConversation||Date.now()<voiceReplyDeadline||voiceMode;if(auto)voiceReplyDeadline=0;speak(e.detail?.text,e.detail?.language,auto)});"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R60 ai-response voice anchor missing')

old="window.SEEKVERA_VOICE_AI={speak,start,markVoiceReply:()=>{voiceConversation=true;voiceReplyDeadline=Date.now()+90000;muted=false;localStorage.setItem('seekvera_voice_muted','0');updateSpeakerButtons();unlockTTS()},isVoiceReplyPending:()=>voiceConversation||Date.now()<voiceReplyDeadline};"
new="window.SEEKVERA_VOICE_AI={speak,start,markVoiceReply:()=>{voiceConversation=true;voiceReplyDeadline=Date.now()+90000;muted=false;localStorage.setItem('seekvera_voice_muted','0');localStorage.setItem('seekvera_voice_mode','1');updateSpeakerButtons();unlockTTS()},isVoiceReplyPending:()=>voiceConversation||Date.now()<voiceReplyDeadline||localStorage.getItem('seekvera_voice_mode')==='1',supportedLanguages:Object.keys(LANGS),resolveLocale:(text,requested)=>localeForText(text,requested)};"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R60 public voice API anchor missing')
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 4) Voice navigation: do not destroy speech immediately. If TTS starts, wait for
#    its end (max 9s). If it cannot start, route quickly and retry pending speech on
#    the destination page.
# -----------------------------------------------------------------------------
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8')
old="function autoRoute(cat,q,reply,language,voiceOrigin){if(!shouldAutoRoute(q,cat))return false;setIntent(cat);if(voiceOrigin)pendingVoiceOnNextPage(reply,language);setTimeout(()=>location.assign(routeUrl(cat,q)),90);return true}"
new="function autoRoute(cat,q,reply,language,voiceOrigin){if(!shouldAutoRoute(q,cat))return false;setIntent(cat);const go=()=>location.assign(routeUrl(cat,q));if(!voiceOrigin){setTimeout(go,90);return true}pendingVoiceOnNextPage(reply,language);let moved=false,started=false;const move=()=>{if(moved)return;moved=true;go()};window.addEventListener('seekvera:tts-start',()=>{started=true},{once:true});window.addEventListener('seekvera:tts-end',()=>{try{sessionStorage.removeItem('seekvera_route_voice')}catch{}move()},{once:true});setTimeout(()=>{if(!started)move()},1800);setTimeout(move,9000);return true}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R60 autoRoute anchor missing')
s=s.replace("document.documentElement.dataset.r31='20260926-r59-one-runtime'",f"document.documentElement.dataset.r31='{VER}'",1)
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 5) Worker safety-net injection uses exactly the same R60 runtime.
# -----------------------------------------------------------------------------
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
s=s.replace('20260926-r59-one-runtime',VER)
s=s.replace('r59-runtime-guard.js','r60-runtime-guard.js')
s=s.replace("h.set('x-seekvera-release','r59-one-runtime')","h.set('x-seekvera-release','r60-chat-voice-persist')")
p.write_text(s,encoding='utf-8')
print('R60 persistent chat + global voice patched')
