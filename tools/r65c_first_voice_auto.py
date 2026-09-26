from pathlib import Path
import re

OLD='20260926-r65b-worldwide-chat-language'
VER='20260926-r65c-first-voice-auto'

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8').replace(OLD,VER)

# First-turn speech has no text to language-detect. Try server ASR with language:auto;
# if the zero-cost server recognizer is temporarily unavailable, fall back to native.
old="async function serverVoice(targetId,button){"
new="async function serverVoice(targetId,button,fallbackNative=false){"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65C serverVoice signature missing')

old="}catch(e){voiceConversation=false;if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"
new="}catch(e){voiceConversation=false;if(fallbackNative&&SpeechRecognition){if(i)i.placeholder='Switching to phone voice recognition…';setTimeout(()=>start(targetId,button,true),80)}else if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65C server fallback anchor missing')

old="function start(targetId,button){"
new="function start(targetId,button,forceNative=false){"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65C start signature missing')

anchor="  const i=document.getElementById(targetId||'aiChatInput');"
extra=anchor+"\n  let explicitVoice=false,rememberedVoice=false;try{explicitVoice=localStorage.getItem('seekvera_language_explicit')==='1';rememberedVoice=!!localStorage.getItem('seekvera_chat_voice_lang')}catch{}\n  if(!forceNative&&!explicitVoice&&!rememberedVoice&&navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){serverVoice(targetId,activeButton,true);return}"
if extra not in s:
    if anchor not in s:raise SystemExit('R65C start decision anchor missing')
    # replace only in native start; serverVoice has same const line before it. Use rfind after start signature.
    pos=s.find(new)
    at=s.find(anchor,pos)
    if at<0:raise SystemExit('R65C native input anchor missing')
    s=s[:at]+extra+s[at+len(anchor):]

p.write_text(s,encoding='utf-8')

# Carry one release marker through app assets and HTML.
for name in ('r24-ai-controller.js','r31-ui-polish.js','worker-r31.js','superapp.js','r60-runtime-guard.js','sw.js'):
    p=Path(name);x=p.read_text(encoding='utf-8').replace(OLD,VER);p.write_text(x,encoding='utf-8')
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    x=p.read_text(encoding='utf-8').replace(OLD,VER)
    for name in ('superapp.js','voice-ai.js','r31-ui-polish.js','r24-ai-controller.js','r60-runtime-guard.js'):
        x=re.sub(re.escape(name)+r'(?:\?v=[^"\'<> ]*)?',name+'?v='+VER,x)
    p.write_text(x,encoding='utf-8')
print('R65C automatic first voice language applied')
