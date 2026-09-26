from pathlib import Path
import re

VER='20260926-r59-one-runtime'

# One permanent runtime in the HTML itself: no more relying on Worker injection to
# upgrade old R54 script tags.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    s=p.read_text(encoding='utf-8')
    s=re.sub(r'superapp\.js(?:\?v=[^"\'<> ]*)?',f'superapp.js?v={VER}',s)
    s=re.sub(r'voice-ai\.js(?:\?v=[^"\'<> ]*)?',f'voice-ai.js?v={VER}',s)
    s=re.sub(r'r31-ui-polish\.js(?:\?v=[^"\'<> ]*)?',f'r31-ui-polish.js?v={VER}',s)
    s=re.sub(r'sw\.js\?v=[^"\'<> )]+',f'sw.js?v={VER}',s)
    if 'r59-runtime-guard.js' not in s:
        s=s.replace('</body>',f'<script src="/r59-runtime-guard.js?v={VER}" defer data-no-i18n="1"></script></body>',1)
    if 'voice-ai.js' not in s:
        s=s.replace('</body>',f'<script src="/voice-ai.js?v={VER}" defer data-no-i18n="1"></script></body>',1)
    if 'r31-ui-polish.js' not in s:
        s=s.replace('</body>',f'<script src="/r31-ui-polish.js?v={VER}" defer data-no-i18n="1"></script></body>',1)
    s=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',s,count=1)
    p.write_text(s,encoding='utf-8')

# Release guard forces the newest SW script to activate, clears visual switching
# leftovers on history restore, but intentionally never reloads the page.
Path('r59-runtime-guard.js').write_text(r'''(()=>{'use strict';
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
''',encoding='utf-8')

# Non-intercepting SW: keep PWA registration/installability, but never sit between
# the browser and page navigation. On activation purge every old app cache once.
Path('sw.js').write_text(r'''const RELEASE='20260926-r59-one-runtime';
self.addEventListener('install',e=>{e.waitUntil(self.skipWaiting())});
self.addEventListener('activate',e=>{e.waitUntil((async()=>{for(const k of await caches.keys())await caches.delete(k);await self.clients.claim()})())});
self.addEventListener('message',e=>{if(e.data==='SKIP_WAITING')self.skipWaiting()});
''',encoding='utf-8')

# Voice-origin route: navigate fast, then speak the saved AI answer on the target
# page. This avoids navigation killing Android speech synthesis.
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8')
old="function autoRoute(cat,q,reply,language,voiceOrigin){if(!shouldAutoRoute(q,cat))return false;setIntent(cat);const go=()=>location.assign(routeUrl(cat,q));if(!voiceOrigin){setTimeout(go,100);return true}let moved=false;const once=()=>{if(moved)return;moved=true;setTimeout(go,1350)};window.addEventListener('seekvera:tts-start',once,{once:true});setTimeout(()=>{if(!moved){moved=true;go()}},2600);return true}"
new="function autoRoute(cat,q,reply,language,voiceOrigin){if(!shouldAutoRoute(q,cat))return false;setIntent(cat);if(voiceOrigin)pendingVoiceOnNextPage(reply,language);setTimeout(()=>location.assign(routeUrl(cat,q)),90);return true}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R59 autoRoute anchor missing')
s=s.replace("setTimeout(()=>{try{window.SEEKVERA_VOICE_AI?.markVoiceReply?.()}catch{}window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:x.text,language:x.language||'auto'}}))},650)","setTimeout(()=>{try{window.SEEKVERA_VOICE_AI?.markVoiceReply?.()}catch{}window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:x.text,language:x.language||'auto'}}))},320)",1)
s=s.replace("document.documentElement.dataset.r31='20260926-r58-global-assistant'",f"document.documentElement.dataset.r31='{VER}'",1)
p.write_text(s,encoding='utf-8')

# Stronger Android audio unlock + deterministic retry if an utterance is queued but
# never begins. Browser TTS remains universal; no paid provider is required.
p=Path('voice-ai.js');s=p.read_text(encoding='utf-8')
old="function unlockTTS(){if(!hasTTS())return;try{speechSynthesis.getVoices?.();speechSynthesis.resume();const u=new SpeechSynthesisUtterance(' ');u.volume=0;u.rate=1;speechSynthesis.speak(u);setTimeout(()=>{try{speechSynthesis.getVoices?.();speechSynthesis.resume()}catch(_){}},60)}catch(_){}}"
new="function unlockTTS(){try{const AC=window.AudioContext||window.webkitAudioContext;if(AC){const c=new AC(),g=c.createGain(),o=c.createOscillator();g.gain.value=.00001;o.connect(g);g.connect(c.destination);o.start();o.stop(c.currentTime+.02);setTimeout(()=>c.close().catch(()=>{}),80)}}catch(_){}if(!hasTTS())return;try{speechSynthesis.cancel();speechSynthesis.getVoices?.();speechSynthesis.resume();const u=new SpeechSynthesisUtterance(' ');u.volume=.01;u.rate=2;speechSynthesis.speak(u);setTimeout(()=>{try{speechSynthesis.cancel();speechSynthesis.getVoices?.();speechSynthesis.resume()}catch(_){}},90)}catch(_){}}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R59 unlockTTS anchor missing')
old2="if(!speechSynthesis.speaking&&attempt<TTS_RETRY_DELAYS.length-1)play(index,attempt+1)"
new2="if(!speechSynthesis.speaking&&attempt<TTS_RETRY_DELAYS.length-1){try{speechSynthesis.cancel();speechSynthesis.resume()}catch(_){}play(index,attempt+1)}"
if old2 in s:s=s.replace(old2,new2,1)
elif new2 not in s:raise SystemExit('R59 TTS retry anchor missing')
p.write_text(s,encoding='utf-8')

# Worker injects the same release marker even if a stale external HTML copy reaches
# it. This is a safety net, not the primary runtime anymore.
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
s=re.sub(r"voice-ai\\\.js\(\?:\\\?\[\^\\\"'<> \]\*\)\?/g,'voice-ai\.js\?v=[^']+'",lambda m:m.group(0),s) if False else s
s=s.replace("text=text.replace(/voice-ai\\.js(?:\\?[^\\\"'<> ]*)?/g,'voice-ai.js?v=20260926-r58-global-assistant');","text=text.replace(/voice-ai\\.js(?:\\?[^\\\"'<> ]*)?/g,'voice-ai.js?v=20260926-r59-one-runtime');text=text.replace(/superapp\\.js(?:\\?[^\\\"'<> ]*)?/g,'superapp.js?v=20260926-r59-one-runtime');text=text.replace(/r31-ui-polish\\.js(?:\\?[^\\\"'<> ]*)?/g,'r31-ui-polish.js?v=20260926-r59-one-runtime');",1)
s=s.replace("if(!text.includes('r31-ui-polish.js'))text=text.replace(/<\\/body>/i,'<script src=\"/r31-ui-polish.js?v=20260926-r58-global-assistant\" defer></script></body>');","if(!text.includes('r59-runtime-guard.js'))text=text.replace(/<\\/body>/i,'<script src=\"/r59-runtime-guard.js?v=20260926-r59-one-runtime\" defer></script></body>');if(!text.includes('voice-ai.js'))text=text.replace(/<\\/body>/i,'<script src=\"/voice-ai.js?v=20260926-r59-one-runtime\" defer></script></body>');if(!text.includes('r31-ui-polish.js'))text=text.replace(/<\\/body>/i,'<script src=\"/r31-ui-polish.js?v=20260926-r59-one-runtime\" defer></script></body>');",1)
s=s.replace("h.set('x-seekvera-release','r35-global-final')","h.set('x-seekvera-release','r59-one-runtime')",1)
p.write_text(s,encoding='utf-8')
print('R59 one runtime patched')
