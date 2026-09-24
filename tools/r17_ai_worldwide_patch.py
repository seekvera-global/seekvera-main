from pathlib import Path
import re

VER='20260924-r17'

# 1) Voice: never force the selected UI language onto the user's speech.
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
old="const VOICE_SILENCE_MS=3200,VOICE_MAX_MS=90000,VOICE_RMS_THRESHOLD=.018;"
new="const VOICE_SILENCE_MS=1250,VOICE_MAX_MS=30000,VOICE_RMS_THRESHOLD=.016;"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('voice timing anchor missing')
old="body:JSON.stringify({audio,language:selectedLang()||'auto'})"
new="body:JSON.stringify({audio,language:'auto'})"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('voice auto-language anchor missing')
old="if(!SpeechRecognition||/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)){serverVoice(targetId,activeButton);return}"
new="if(navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){serverVoice(targetId,activeButton);return}if(!SpeechRecognition){voiceConversation=false;if(i)i.placeholder='Voice recognition is unavailable here — please type your message.';return}"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('voice universal server-ASR anchor missing')
p.write_text(s,encoding='utf-8')

# 2) Chat: detect the language of every new message independently of UI/country.
p=Path('global-ui.js')
s=p.read_text(encoding='utf-8')
old="body:JSON.stringify({message:q,country:country(),language:aiLanguageName(),scope:'worldwide',fast:true,history})"
new="body:JSON.stringify({message:q,country:country(),language:'auto',scope:'worldwide',fast:true,history})"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('global chat language anchor missing')
# Smooth error recovery: one direct-worker retry if same-origin routing is temporarily unavailable.
anchor="function country(){const e=$('#country');return e?.value==='WW'?'Worldwide':(e?.options?.[e.selectedIndex]?.textContent||'Worldwide')}"
helper=anchor+"\nasync function aiChatRequest(payload){const primary=api('/api/ai'),direct='https://seekvera-main.seekvera-global.workers.dev/api/ai',urls=[...new Set([primary,direct])];let last='AI unavailable';for(const url of urls){const c=new AbortController(),timer=setTimeout(()=>c.abort(),18000);try{const r=await fetch(url,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload),signal:c.signal});const d=await r.json().catch(()=>null);clearTimeout(timer);const answer=plain(d?.response);if(r.ok&&answer)return{r,d,answer};last=plain(d?.error)||('HTTP '+r.status);if(![429,500,502,503,504].includes(r.status))break}catch(e){clearTimeout(timer);last=plain(e?.message)||'AI network error'}}throw Error(last)}"
if 'async function aiChatRequest(payload)' not in s:
    if anchor not in s: raise SystemExit('global ai retry insertion anchor missing')
    s=s.replace(anchor,helper,1)
old="const r=await fetch(api('/api/ai'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:q,country:country(),language:'auto',scope:'worldwide',fast:true,history})});const d=await r.json().catch(()=>null),answer=plain(d?.response);if(!r.ok||!answer)throw Error(plain(d?.error)||'AI unavailable');"
new="const {r,d,answer}=await aiChatRequest({message:q,country:country(),language:'auto',scope:'worldwide',fast:true,history});"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('global ai retry call anchor missing')
p.write_text(s,encoding='utf-8')

# 3) Navigation/local app control: accept natural country forms before AI/network.
p=Path('navigation.js')
s=p.read_text(encoding='utf-8')
# Lebanese adjective variants from the reported Hindi/English case; country names for all 248 remain dynamic.
alias_anchor="function countryNames(code){\n  const out=new Set([code]);"
alias_new="const COUNTRY_COMMAND_ALIASES={LB:['lebanese','libanese','libanais','libanaise','لبناني','لبنانية','لبنانيه','लेबनानी']};\nfunction countryNames(code){\n  const out=new Set([code,...(COUNTRY_COMMAND_ALIASES[code]||[])]);"
if 'COUNTRY_COMMAND_ALIASES' not in s:
    if alias_anchor not in s: raise SystemExit('country alias insertion anchor missing')
    s=s.replace(alias_anchor,alias_new,1)
old="const names=countryNames(code),hasTarget=names.some(n=>n.length>=2&&(s===n||(' '+s+' ').includes(' '+n+' ')));\n    const latin=/\\b(?:set|switch|change|choose|select|go|move|use|open|control|app|market|country|region|take|put)\\b/.test(s);\n    const native=/(?:حط|حطلي|اختار|اختر|غير|غيرلي|حول|حوللي|انتقل|اذهب|استخدم|غيّر|حوّل|बदल|चुन|जाओ|देश|ملک|بدل|منتخب|смени|сменить|выбери|установи|cambia|elige|selecciona|change|choisis|wechsle|wähle|mudar|trocar|seç|degistir|imposta|scegli)/u.test(raw);\n    const short=s.split(/\\s+/).filter(Boolean).length<=3;"
new="const names=countryNames(code);\n    const latin=/\\b(?:set|switch|change|choose|select|go|move|use|open|control|app|market|country|region|take|put)\\b/.test(s);\n    const native=/(?:حط|حطلي|اختار|اختر|غير|غيرلي|حول|حوللي|انتقل|اذهب|استخدم|غيّر|حوّل|बदल|चुन|जाओ|देश|ऐप|परिवर्तन|ملک|بدل|منتخب|смени|сменить|выбери|установи|cambia|elige|selecciona|change|choisis|wechsle|wähle|mudar|trocar|seç|degistir|imposta|scegli)/u.test(raw);\n    const short=s.split(/\\s+/).filter(Boolean).length<=3;\n    const hasTarget=names.some(n=>n.length>=2&&(s===n||(' '+s+' ').includes(' '+n+' ')||((latin||native)&&s.includes(n))));"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('country natural-form anchor missing')
# Let inner chat scroll hand movement back to the page instead of trapping it; prevent scroll anchoring jitter.
s=s.replace("contain:layout style!important","contain:layout!important")
s=s.replace("scroll-behavior:auto!important;overscroll-behavior:contain!important","scroll-behavior:smooth!important;overscroll-behavior:auto!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important;overflow-anchor:none!important")
p.write_text(s,encoding='utf-8')

# 4) Worker: message language wins over selected UI language, and prefer the current fast multilingual model.
p=Path('worker.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'", "const RELEASE='20260924-ai-r17'", s, count=1)
old="if(h&&!/^auto$/i.test(h))return h;const script=scriptLanguage(text);"
new="const script=scriptLanguage(text);"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('worker language-hint anchor missing')
old="quality?[FALLBACK,PRIMARY,LIGHT,FASTCHAT]:[FASTCHAT,FALLBACK,LIGHT,PRIMARY]"
new="quality?[FALLBACK,PRIMARY,LIGHT,FASTCHAT]:[FALLBACK,PRIMARY,LIGHT,FASTCHAT]"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('worker model order anchor missing')
s=s.replace("aiResilience:'fast-chat-language-lock-v4'","aiResilience:'r17-message-language-auto-glm-first'",1)
s=s.replace("voiceRuntime:'native-plus-server-asr-v1'","voiceRuntime:'server-asr-auto-language-r17'",1)
p.write_text(s,encoding='utf-8')

# 5) Force every page to fetch the corrected runtimes; do not change page structure.
changed=0
for hp in Path('.').glob('*.html'):
    if hp.name.lower().startswith('google'): continue
    t=hp.read_text(encoding='utf-8')
    before=t
    t=re.sub(r'voice-ai\\.js\\?v=[^"\\']+',f'voice-ai.js?v={VER}',t)
    t=re.sub(r'global-ui\\.js\\?v=[^"\\']+',f'global-ui.js?v={VER}',t)
    t=re.sub(r'navigation\\.js\\?v=[^"\\']+',f'navigation.js?v={VER}',t)
    t=re.sub(r"sw\\.js\\?v=[^'\"]+",f'sw.js?v={VER}',t)
    if t!=before:
        hp.write_text(t,encoding='utf-8'); changed+=1
if changed<1: raise SystemExit('no HTML runtime references updated')

# Service-worker cache refresh so existing phones do not stay on R16.
p=Path('sw.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const CACHE='[^']+';", "const CACHE='seekvera-r17-worldwide-ai-20260924';", s, count=1)
p.write_text(s,encoding='utf-8')

# Guardrails.
assert "language:'auto',scope:'worldwide'" in Path('global-ui.js').read_text(encoding='utf-8')
assert "language:'auto'" in Path('voice-ai.js').read_text(encoding='utf-8')
assert 'VOICE_SILENCE_MS=1250' in Path('voice-ai.js').read_text(encoding='utf-8')
assert 'COUNTRY_COMMAND_ALIASES' in Path('navigation.js').read_text(encoding='utf-8')
assert 'लेबनानी' in Path('navigation.js').read_text(encoding='utf-8')
assert "const script=scriptLanguage(text);" in Path('worker.js').read_text(encoding='utf-8')
print('R17 source patch complete; HTML pages updated:',changed)
