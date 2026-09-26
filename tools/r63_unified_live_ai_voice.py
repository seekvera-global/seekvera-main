from pathlib import Path
import re

OLD='20260926-r62-any-language-voice-control'
VER='20260926-r63-unified-live-ai-voice'

# -----------------------------------------------------------------------------
# 1) One release on every public page so stale R62 assets are not reused.
# -----------------------------------------------------------------------------
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):
        continue
    s=p.read_text(encoding='utf-8')
    s=s.replace(OLD,VER)
    for name in ('superapp.js','voice-ai.js','r31-ui-polish.js','r24-ai-controller.js','r60-runtime-guard.js'):
        s=re.sub(re.escape(name)+r'(?:\?v=[^"\'<> ]*)?', name+'?v='+VER, s)
    if 'data-release=' in s:
        s=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',s,count=1)
    p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) Use the custom-domain Worker API on the same origin. This removes a needless
#    cross-origin hop from the public app and avoids CORS/network differences.
#    Also clear the old accidental country default once unless the user explicitly
#    chose a country, and remember future explicit choices.
# -----------------------------------------------------------------------------
p=Path('superapp.js');s=p.read_text(encoding='utf-8')
s=s.replace("const WORKER=location.hostname.endsWith('workers.dev')?'':'https://seekvera-main.seekvera-global.workers.dev';","const WORKER='';",1)
old="const migration='seekvera_worldwide_default_20260923_r4';if(!localStorage.getItem(migration)){localStorage.setItem('seekvera_country','WW');localStorage.setItem('seekvera_scope','worldwide');localStorage.setItem(migration,'1')}"
new="const migration='seekvera_worldwide_default_20260926_r63';if(!localStorage.getItem(migration)){if(localStorage.getItem('seekvera_country_explicit')!=='1'){localStorage.setItem('seekvera_country','WW');localStorage.setItem('seekvera_scope','worldwide')}localStorage.setItem(migration,'1')}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R63 worldwide migration anchor missing')
old="el.addEventListener('change',()=>{localStorage.setItem('seekvera_country',el.value);syncCurrency()})"
new="el.addEventListener('change',()=>{localStorage.setItem('seekvera_country',el.value);localStorage.setItem('seekvera_country_explicit','1');syncCurrency()})"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R63 country explicit anchor missing')
s=s.replace("const RELEASE='20260924-az-r8';",f"const RELEASE='{VER}';",1)
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Voice: native Web Speech first when the browser provides it. R62 forced every
#    Android/iPhone through Workers Whisper; when the free AI allocation/capacity is
#    unavailable that makes a perfectly good microphone look broken. Server Whisper
#    remains the fallback when native recognition is unavailable.
# -----------------------------------------------------------------------------
p=Path('voice-ai.js');s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
old="if(/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)&&navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){serverVoice(targetId,activeButton);return}if(!SpeechRecognition){serverVoice(targetId,activeButton);return}"
new="if(!SpeechRecognition){serverVoice(targetId,activeButton);return}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R63 native-first voice anchor missing')
if 'function voiceInputLocale()' not in s:
    marker='function localeForText'
    helper="function voiceInputLocale(){const html=String(document.documentElement.lang||'').toLowerCase().split(/[-_]/)[0],sel=String(document.getElementById('lang')?.value||'').toLowerCase().split(/[-_]/)[0];if(html&&html!=='auto'&&LANGS[html])return LANGS[html];if(sel&&sel!=='auto'&&LANGS[sel])return LANGS[sel];if(lastLocale&&/^[a-z]{2,3}(?:-|$)/i.test(lastLocale))return lastLocale;return locale()}\n"
    if marker not in s:raise SystemExit('R63 voice locale insertion point missing')
    s=s.replace(marker,helper+marker,1)
s=s.replace('r.lang=locale();','r.lang=voiceInputLocale();',1)
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 4) Return the real ASR failure reason instead of hiding every failure behind a
#    generic 503. This lets the client and live audit distinguish quota/capacity.
# -----------------------------------------------------------------------------
p=Path('worker.js');s=p.read_text(encoding='utf-8')
old="}catch(e){console.warn('Speech transcription fallback',e);return j(request,{ok:false,error:'Voice transcription is temporarily unavailable',retryable:true},503)}}"
new="}catch(e){const msg=clean(e?.message||e,500),reason=/3036|daily free allocation/i.test(msg)?'daily_free_ai_limit':/3040|capacity temporarily exceeded/i.test(msg)?'capacity_busy':/5035|requires a Workers Paid plan/i.test(msg)?'paid_model_required':/5016|model agreement/i.test(msg)?'model_agreement_required':'workers_ai_runtime_error';console.warn('Speech transcription fallback',reason,e);return j(request,{ok:false,error:'Voice transcription is temporarily unavailable',retryable:true,reason},503)}}"
if old in s:s=s.replace(old,new,1)
elif "Speech transcription fallback',reason" not in s:raise SystemExit('R63 ASR reason anchor missing')
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 5) Local controls are immediate and independent of the AI provider. Natural
#    commands can move the app to a country even when AI inference is unavailable.
# -----------------------------------------------------------------------------
p=Path('r24-ai-controller.js');s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
s=s.replace("|ملک|পরিবর্তন", "|ملک|وديني|ودّيني|خذني|خدني|انقلني|نقلني|take me|move me|go to|পরিবর্তন",1)
old="if(country&&api.profiles?.[country]){try{api.setCountry(country);changed=true}"
new="if(country&&api.profiles?.[country]){try{localStorage.setItem('seekvera_country_explicit','1')}catch{}try{api.setCountry(country);changed=true}"
if old in s:s=s.replace(old,new,1)
elif "seekvera_country_explicit','1'" not in s:raise SystemExit('R63 controller explicit country anchor missing')
# Local/static 200 responses are degraded AI, so let the already-existing private
# browser backup try once. Keep the timeout bounded so the UI does not hang.
s=s.replace("setTimeout(()=>ctl.abort(),16000)","setTimeout(()=>ctl.abort(),6500)",1)
old="res.status===503||data?.degraded===true||data?.model==='seekvera-local-router'"
new="res.status===503||data?.degraded===true||data?.model==='seekvera-local-router'||/fallback|static|local-guide/i.test(String(data?.model||''))"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R63 browser backup trigger anchor missing')
p.write_text(s,encoding='utf-8')

# The chat-side country setter also records that this was an intentional choice.
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
s=s.replace("try{localStorage.setItem('seekvera_country',code)}catch{}","try{localStorage.setItem('seekvera_country',code);localStorage.setItem('seekvera_country_explicit','1')}catch{}",1)
# Country/language controls must not wait for a model reply. Apply + confirm instantly.
pat=re.compile(r"const spokenLanguage=conversationLang\(q\),ctl=controlResult\(q\);if\(ctl\)\{.*?return\}const pending=appendMsg\('bot',thinkingText\(\),'thinking'\);",re.S)
rep="const spokenLanguage=conversationLang(q),ctl=controlResult(q);if(ctl){const reply=controlReply(ctl,q);appendMsg('bot',reply);try{window.SEEKVERA_CHAT?.save?.()}catch{}window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:reply,language:spokenLanguage}}));submitting=false;return}const pending=appendMsg('bot',thinkingText(),'thinking');"
if pat.search(s):s=pat.sub(rep,s,count=1)
elif rep not in s:raise SystemExit('R63 immediate control branch anchor missing')
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 6) AI resilience. Detect the message language before falling back, including
#    common Latin-script languages. Mark static/local replies as degraded so the
#    browser can try the stronger private fallback. The normal Workers AI fast path
#    remains first and fastest when quota/capacity is available.
# -----------------------------------------------------------------------------
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
if 'function detectMessageLanguageCode(' not in s:
    marker="async function publicAIFallback"
    helper=r'''function detectMessageLanguageCode(text,hint='auto'){const t=String(text||''),h=String(hint||'auto').toLowerCase().split(/[-_ ]/)[0];if(h&&h!=='auto'&&/^[a-z]{2,3}$/.test(h))return h;if(/[\u0600-\u06ff]/u.test(t))return'ar';if(/[\u0590-\u05ff]/u.test(t))return'he';if(/[\u0900-\u097f]/u.test(t))return'hi';if(/[\u0980-\u09ff]/u.test(t))return'bn';if(/[\u4e00-\u9fff]/u.test(t))return'zh';if(/[\u3040-\u30ff]/u.test(t))return'ja';if(/[\uac00-\ud7af]/u.test(t))return'ko';if(/[\u0e00-\u0e7f]/u.test(t))return'th';if(/[\u0370-\u03ff]/u.test(t))return'el';if(/[\u1200-\u137f]/u.test(t))return'am';if(/[\u0400-\u04ff]/u.test(t))return'ru';const n=' '+t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')+' ';const tests=[['fr',/\b(bonjour|salut|je|vous|cherche|travail|emploi|avec|pour|dans|aux|une|des|merci)\b/],['es',/\b(hola|busco|trabajo|empleo|quiero|para|con|una|gracias|pais)\b/],['pt',/\b(ola|procuro|trabalho|emprego|quero|para|com|uma|obrigado)\b/],['de',/\b(hallo|ich|suche|arbeit|job|mochte|bitte|danke|fur|mit)\b/],['it',/\b(ciao|cerco|lavoro|voglio|per|con|grazie|una)\b/],['tr',/\b(merhaba|is|iş|ariyorum|arıyorum|istiyorum|icin|için|tesekkur|teşekkür)\b/],['nl',/\b(hallo|ik|zoek|werk|baan|voor|met|dank)\b/],['id',/\b(hai|saya|mencari|kerja|pekerjaan|untuk|dengan|terima kasih)\b/],['ms',/\b(saya|mencari|kerja|pekerjaan|untuk|dengan|terima kasih)\b/],['sw',/\b(habari|natafuta|kazi|kwa|na|asante)\b/],['fil',/\b(kumusta|ako|trabaho|hanap|para|salamat)\b/]];for(const[c,r]of tests)if(r.test(n))return c;return'en'}
'''
    if marker not in s:raise SystemExit('R63 AI language helper insertion point missing')
    s=s.replace(marker,helper+marker,1)
# Give the private server-side backup enough time to be useful, but cap latency.
s=s.replace("AbortSignal.timeout(2200)","AbortSignal.timeout(4500)",1)
old="const language=langName(b.language,m),hinted=clean(b.conversationIntent,30)"
new="const messageLanguageCode=detectMessageLanguageCode(m,b.language),language=langName(messageLanguageCode,m),hinted=clean(b.conversationIntent,30)"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R63 smartAI language anchor missing')
# Static packs should use the detected message language, not 'auto' -> English.
old="async function staticPackAIFallback(req,env,b,language,cat){const code=inputLangCode(b?.language);"
new="async function staticPackAIFallback(req,env,b,language,cat,detectedCode){const code=inputLangCode(detectedCode||b?.language);"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R63 static fallback language anchor missing')
s=s.replace("staticPackAIFallback(req,env,b,language,cat)","staticPackAIFallback(req,env,b,language,cat,messageLanguageCode)",1)
# Do not disable all fallback just because the AI binding itself is missing.
s=s.replace("if(blocked(m))return null;if(!env.AI)return null;const hist=", "if(blocked(m))return null;const hist=",1)
# staggeredAI assumes env.AI; guard it so public/static fallback still works.
s=s.replace("const got=await staggeredAI(env,messages);let response,model,fastPath;", "const got=env.AI?await staggeredAI(env,messages):null;let response,model,fastPath;",1)
# Expose degraded state only for static/local fallback; R24 can then try one stronger backup.
old="return json(req,{ok:true,response,model,language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath})}"
new="const degraded=/seekvera-(?:static|local-guide)/i.test(String(model||''));return json(req,{ok:true,response,model,language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath,degraded})}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R63 degraded response anchor missing')
# Basic multilingual job intent on direct API requests too.
s=s.replace("job|jobs|career|vacancy|work|employment|hiring|وظيفة", "job|jobs|career|vacancy|work|employment|hiring|travail|emploi|trabajo|empleo|trabalho|lavoro|arbeit|iş|is ilanı|работ|工作|仕事|직업|وظيفة",1)
# Dynamic HTML injection must reference R63.
s=s.replace("h.set('x-seekvera-release','r61-country-chat-server-voice')", "h.set('x-seekvera-release','r63-unified-live-ai-voice')",1)
p.write_text(s,encoding='utf-8')

# Runtime/SW release markers.
for name in ('r60-runtime-guard.js','sw.js'):
    p=Path(name);x=p.read_text(encoding='utf-8').replace(OLD,VER);p.write_text(x,encoding='utf-8')

print('R63 unified live AI + voice recovery patch applied')
