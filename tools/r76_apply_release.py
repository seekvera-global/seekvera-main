from pathlib import Path
import re, json

VER='20260926-r76-complete-global-final'

# 1) One Worker entry point: the R76 structured multilingual assistant.
p=Path('wrangler.jsonc');s=p.read_text(encoding='utf-8')
s=re.sub(r'"main"\s*:\s*"\./worker-[^"]+\.js"','"main": "./worker-r76.js"',s,count=1)
p.write_text(s,encoding='utf-8')

# 2) Force fresh static language packs and one visible release marker.
p=Path('i18n-ui.js');s=p.read_text(encoding='utf-8')
s=re.sub(r"const VERSION='[^']+'","const VERSION='"+VER+"'",s,count=1)
s=s.replace('20260925-r32-static-v5',VER)
s=s.replace('20260925-r35-static-v3',VER)
s=s.replace('20260925-r35-static-v4',VER)
p.write_text(s,encoding='utf-8')

# 3) Voice: server Whisper language:auto first for EVERY microphone turn when MediaRecorder is available.
# Native phone/browser speech recognition is only the fallback. This removes the UI-language lock.
p=Path('voice-ai.js');s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'","const RELEASE='"+VER+"'",s,count=1)
# Normalize serverVoice signature so it can fall back to native.
s=s.replace('async function serverVoice(targetId,button){','async function serverVoice(targetId,button,fallbackNative=false){',1)
# Add native fallback to the common transcription error branch when an older build lacks it.
old="}catch(e){voiceConversation=false;if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"
new="}catch(e){voiceConversation=false;if(fallbackNative&&SpeechRecognition){if(i)i.placeholder='Switching to phone voice recognition…';setTimeout(()=>start(targetId,button,true),80)}else if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"
if old in s:s=s.replace(old,new,1)
# Normalize start signature.
s=s.replace('function start(targetId,button){','function start(targetId,button,forceNative=false){',1)
# Replace previous conditional first-turn server-ASR decision with unconditional server-first decision.
s=re.sub(r"\n\s*let explicitVoice=false,rememberedVoice=false;try\{explicitVoice=.*?serverVoice\(targetId,activeButton,true\);return\}","\n  if(!forceNative&&navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){serverVoice(targetId,activeButton,true);return}",s,count=1,flags=re.S)
# If that older decision did not exist, inject after the input lookup inside start().
if "if(!forceNative&&navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){serverVoice(targetId,activeButton,true);return}" not in s:
    pos=s.find('function start(targetId,button,forceNative=false){')
    anchor="const i=document.getElementById(targetId||'aiChatInput');"
    at=s.find(anchor,pos)
    if pos<0 or at<0: raise SystemExit('R76 voice start anchor missing')
    at+=len(anchor)
    s=s[:at]+"\n  if(!forceNative&&navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){serverVoice(targetId,activeButton,true);return}"+s[at:]
# Keep TTS/reply mode active after microphone input.
if "localStorage.setItem('seekvera_voice_mode','1')" not in s:
    s=s.replace("function enableVoiceConversation(){voiceConversation=true;","function enableVoiceConversation(){try{localStorage.setItem('seekvera_voice_mode','1')}catch{}voiceConversation=true;",1)
p.write_text(s,encoding='utf-8')

# 4) R31 owns chat submission/routing/persistence. R24 remains only as a fetch/action helper.
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8')
s=re.sub(r"const VERSION='[^']+'","const VERSION='"+VER+"'",s,count=1)
s=s.replace("setTimeout(()=>c.abort(),7500)","setTimeout(()=>c.abort(),11000)",1)
p.write_text(s,encoding='utf-8')

p=Path('r24-ai-controller.js');s=p.read_text(encoding='utf-8')
s=re.sub(r"const VERSION='[^']+'","const VERSION='"+VER+"'",s,count=1)
# Let the R76 server answer stand; browser backup is only for an actual failed/empty response.
s=s.replace("res.status===503||data?.model==='seekvera-local-router'||!String(data?.response||'').trim()||/fallback|static|local-guide/i.test(String(data?.model||''))","res.status===503||!String(data?.response||'').trim()",1)
p.write_text(s,encoding='utf-8')

# 5) Stamp related assets and remove the two overlapping late AI controllers (R66 + R74) from pages.
for name in ('superapp.js','r60-runtime-guard.js','navigation.js'):
    p=Path(name)
    if not p.exists(): continue
    x=p.read_text(encoding='utf-8')
    x=re.sub(r"const RELEASE='[^']+'","const RELEASE='"+VER+"'",x,count=1)
    p.write_text(x,encoding='utf-8')

p=Path('sw.js');p.write_text("const RELEASE='"+VER+"';\nself.addEventListener('install',e=>{e.waitUntil(self.skipWaiting())});\nself.addEventListener('activate',e=>{e.waitUntil((async()=>{for(const k of await caches.keys())await caches.delete(k);await self.clients.claim()})())});\nself.addEventListener('message',e=>{if(e.data==='SKIP_WAITING')self.skipWaiting()});\n",encoding='utf-8')

assets=('superapp.js','voice-ai.js','i18n-ui.js','navigation.js','r24-ai-controller.js','r60-runtime-guard.js','r31-ui-polish.js')
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    x=p.read_text(encoding='utf-8')
    x=re.sub(r'<script[^>]+src=["\']/r66-final-controller\.js[^>]*></script>','',x,flags=re.I)
    x=re.sub(r'<script[^>]+src=["\']/r74-ai-failover\.js[^>]*></script>','',x,flags=re.I)
    x=re.sub(r'<script[^>]+src=["\']r66-final-controller\.js[^>]*></script>','',x,flags=re.I)
    x=re.sub(r'<script[^>]+src=["\']r74-ai-failover\.js[^>]*></script>','',x,flags=re.I)
    for a in assets:
        x=re.sub(re.escape(a)+r'(?:\?v=[^"\'<> ]*)?',a+'?v='+VER,x)
    x=re.sub(r'sw\.js\?v=[^"\'<> )]+','sw.js?v='+VER,x)
    if 'data-release=' in x:x=re.sub(r'data-release="[^"]+"','data-release="'+VER+'"',x,count=1)
    p.write_text(x,encoding='utf-8')

# 6) Basic invariants before deploy.
assert 'worker-r76.js' in Path('wrangler.jsonc').read_text(encoding='utf-8')
assert 'serverVoice(targetId,activeButton,true)' in Path('voice-ai.js').read_text(encoding='utf-8')
assert VER in Path('i18n-ui.js').read_text(encoding='utf-8')
idx=Path('index.html').read_text(encoding='utf-8')
assert 'r66-final-controller.js' not in idx and 'r74-ai-failover.js' not in idx
print('R76 release patch applied',VER)
