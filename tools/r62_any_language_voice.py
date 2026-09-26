from pathlib import Path
import re

OLD='20260926-r61-country-chat-server-voice'
VER='20260926-r62-any-language-voice-control'

# 1) One cache-busted runtime on all public pages.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):
        continue
    s=p.read_text(encoding='utf-8')
    s=s.replace(OLD,VER)
    for name in ('navigation.js','r24-ai-controller.js','voice-ai.js','r31-ui-polish.js','r60-runtime-guard.js'):
        s=re.sub(re.escape(name)+r'(?:\?v=[^"\'<> ]*)?', name+'?v='+VER, s)
    s=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',s,count=1)
    p.write_text(s,encoding='utf-8')

# 2) Voice input must not be locked to the selected UI language.
#    On phones/tablets prefer the existing server Whisper path because it can auto-detect
#    the spoken language. Desktop keeps native recognition for speed, with server fallback.
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
old="if(!SpeechRecognition){serverVoice(targetId,activeButton);return}"
new="if(/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)&&navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){serverVoice(targetId,activeButton);return}if(!SpeechRecognition){serverVoice(targetId,activeButton);return}"
if new not in s:
    if old not in s: raise SystemExit('voice mobile/server-first anchor missing')
    s=s.replace(old,new,1)
old="body:JSON.stringify({audio,language:selectedLang()||'auto'})"
new="body:JSON.stringify({audio,language:'auto'})"
if new not in s:
    if old not in s: raise SystemExit('voice transcription language anchor missing')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# 3) Every written/spoken message asks the backend to detect the user's actual language.
#    Do not infer Latin-script conversation language from the UI country/language.
p=Path('r31-ui-polish.js')
s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
s=re.sub(r"function conversationLang\(q=''\)\{.*?\}\nfunction similarReply", "function conversationLang(q=''){return'auto'}\nfunction similarReply", s, count=1, flags=re.S)
if "function conversationLang(q=''){return'auto'}" not in s:
    raise SystemExit('conversation language patch missing')
# When a control command succeeds, use the server-detected language for speech output.
s=s.replace("detail:{text:reply,language:spokenLanguage}}))", "detail:{text:reply,language:d?.language||spokenLanguage}}))", 1)
p.write_text(s,encoding='utf-8')

# 4) Release markers and controller version.
for name in ('r24-ai-controller.js','r60-runtime-guard.js','sw.js','worker-r31.js'):
    p=Path(name)
    s=p.read_text(encoding='utf-8')
    s=s.replace(OLD,VER)
    p.write_text(s,encoding='utf-8')

print('R62 any-language voice/control patch applied')
