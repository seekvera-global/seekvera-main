from pathlib import Path
import re

VER='20260927-r99-current-locale-voice'
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')

old="""function hintedVoiceCodes(){
  const out=[];const add=x=>{const c=codeOf(x);if(c&&LANGS[c]&&!out.includes(c))out.push(c)};
  try{add(localStorage.getItem('seekvera_chat_voice_lang'));add(selectedLang());add(document.documentElement.lang);add(navigator.language)}catch(_){}
  return out.slice(0,3)
}
"""
new="""function hintedVoiceCodes(){
  const out=[];const add=x=>{const c=codeOf(x);if(c&&LANGS[c]&&!out.includes(c))out.push(c)};
  try{add(selectedLang());add(document.documentElement.lang);add(localStorage.getItem('seekvera_chat_voice_lang'));add(navigator.language)}catch(_){}
  return out.slice(0,4)
}
"""
if new not in s:
    if old not in s: raise SystemExit('hintedVoiceCodes anchor missing')
    s=s.replace(old,new,1)

# The user explicitly reported that the microphone cut them off. Allow a natural pause before auto-send.
s=s.replace('const VOICE_SILENCE_MS=1800,VOICE_MAX_MS=45000,VOICE_RMS_THRESHOLD=.012;','const VOICE_SILENCE_MS=3200,VOICE_MAX_MS=60000,VOICE_RMS_THRESHOLD=.012;',1)
# Native recognition hard cap should follow the same longer conversation ceiling.
s=s.replace('Math.min(VOICE_MAX_MS,30000)','Math.min(VOICE_MAX_MS,50000)',1)
s=re.sub(r"window\.__seekveraVoiceMode='[^']+';", "window.__seekveraVoiceMode='current-locale-quality-r99';", s, count=1)
p.write_text(s,encoding='utf-8')

for hp in Path('.').glob('*.html'):
    h=hp.read_text(encoding='utf-8')
    h=re.sub(r'voice-ai\.js\?v=[^"\\s]+','voice-ai.js?v='+VER,h)
    if hp.name=='index.html': h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
    hp.write_text(h,encoding='utf-8')
psw=Path('sw.js'); sw=psw.read_text(encoding='utf-8'); sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1); psw.write_text(sw,encoding='utf-8')
print('R99_APPLIED')
