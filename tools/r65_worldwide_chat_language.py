from pathlib import Path
import re

OLD='20260926-r64-final-ai-voice'
VER='20260926-r65-worldwide-chat-language'

# Keep one cache-busted release across public pages.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):
        continue
    s=p.read_text(encoding='utf-8').replace(OLD,VER)
    for name in ('superapp.js','voice-ai.js','r31-ui-polish.js','r24-ai-controller.js','r60-runtime-guard.js'):
        s=re.sub(re.escape(name)+r'(?:\?v=[^"\'<> ]*)?',name+'?v='+VER,s)
    p.write_text(s,encoding='utf-8')

# 1) Worldwide is a real app-control target, not an AI search intent.
p=Path('r24-ai-controller.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
old="const COUNTRY_ALIASES={US:"
new="const COUNTRY_ALIASES={WW:['worldwide','global','all countries','all markets','whole world','everywhere','world wide','العالم','عالمي','العالمي','حول العالم','كل العالم','كل الدول','جميع الدول','دولي','الدولي','mondial','monde entier','mundo','todo el mundo','weltweit','globalt','विश्वभर','दुनिया भर','全球','全世界','世界中','전세계','dünya çapında','весь мир','по всему миру'],US:"
if old in s:s=s.replace(old,new,1)
elif "WW:['worldwide'" not in s:raise SystemExit('R65 worldwide aliases anchor missing')
old="if(country&&!api.profiles?.[country])country='';"
new="if(country&&country!=='WW'&&!api.profiles?.[country])country='';"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65 WW validation anchor missing')
s=s.replace("if(country&&api.profiles?.[country]){try{localStorage.setItem('seekvera_country_explicit','1')}","if(country&&(country==='WW'||api.profiles?.[country])){try{localStorage.setItem('seekvera_country_explicit','1')}",1)
s=s.replace("if(country&&api.profiles?.[country]){\n    const e=document.querySelector('#lang');","if(country&&(country==='WW'||api.profiles?.[country])){\n    const e=document.querySelector('#lang');",1)
p.write_text(s,encoding='utf-8')

# 2) Controls never inherit the previous Jobs/Travel intent.
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
old="function controlResult(q){try{const c=window.SEEKVERA_R24_CONTROLLER?.detectControls?.(q)||{};if(c.country||c.language){forceControl(c);return c}}catch{}return null}"
new="function controlResult(q){try{const c=window.SEEKVERA_R24_CONTROLLER?.detectControls?.(q)||{};if(c.country||c.language){try{sessionStorage.removeItem('seekvera_ai_intent')}catch{}forceControl(c);return c}}catch{}return null}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65 control reset anchor missing')
pat=re.compile(r"function controlReply\(c,q\)\{.*?return''\}")
rep="function controlReply(c,q){if(c?.country&&c?.language)return'✓ '+String(c.country).toUpperCase()+' · '+String(c.language).toUpperCase();if(c?.country)return c.country==='WW'?'✓ 🌐 Worldwide':'✓ '+String(c.country).toUpperCase();if(c?.language)return'✓ '+String(c.language).toUpperCase();return''}"
if pat.search(s):s=pat.sub(rep,s,count=1)
elif rep not in s:raise SystemExit('R65 control reply anchor missing')
old="language:'auto',uiLanguage:lang(),scope:country()==='WW'?'worldwide':'country'"
new="language:'auto',uiLanguage:lang(),browserLanguage:String(navigator.language||''),scope:country()==='WW'?'worldwide':'country'"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65 browser language request anchor missing')
p.write_text(s,encoding='utf-8')

# 3) Text chat language comes from the latest MESSAGE, never country.
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
old="You are SEEKVERA AI inside a worldwide marketplace app. Reply ONLY in ${language}. Market: ${market}. User message: ${message}. Category: ${cat}."
new="You are SEEKVERA AI inside a worldwide marketplace app. Detect the language of the USER MESSAGE yourself and reply ONLY in that same language and script, unless the user explicitly asks for another reply language. The selected market must NEVER decide the reply language. Language hint ${language} may be wrong. Market: ${market}. User message: ${message}. Category: ${cat}."
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65 public fallback language anchor missing')
old="You are SEEKVERA AI inside a worldwide marketplace app. Reply ONLY in ${language}. Market: ${market}.${controlNote} Be natural, practical and concise"
new="You are SEEKVERA AI inside a worldwide marketplace app. Detect the language of the LATEST USER MESSAGE yourself and reply ONLY in that same language and script, unless the user explicitly requests another reply language. Never choose the reply language from country, market, interface language or browser language. Local language hint: ${language}. Market: ${market}.${controlNote} Be natural, practical and concise"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65 Workers AI language lock anchor missing')
old="const messageLanguageCode=detectMessageLanguageCode(m,b.language),language=langName(messageLanguageCode,m),hinted="
new="const messageLanguageCode=detectMessageLanguageCode(m,b.language==='auto'?(b.browserLanguage||'auto'):b.language),language=langName(messageLanguageCode,m),hinted="
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65 language tiebreaker anchor missing')
s=s.replace("h.set('x-seekvera-release','r64-final-ai-voice')","h.set('x-seekvera-release','r65-worldwide-chat-language')",1)
p.write_text(s,encoding='utf-8')

# 4) Voice chat is independent of country.
p=Path('voice-ai.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
old="function voiceInputLocale(){const html=String(document.documentElement.lang||'').toLowerCase().split(/[-_]/)[0],sel=String(document.getElementById('lang')?.value||'').toLowerCase().split(/[-_]/)[0];if(html&&html!=='auto'&&LANGS[html])return LANGS[html];if(sel&&sel!=='auto'&&LANGS[sel])return LANGS[sel];if(lastLocale&&/^[a-z]{2,3}(?:-|$)/i.test(lastLocale))return lastLocale;return locale()}"
new="function voiceInputLocale(){let explicit=false;try{explicit=localStorage.getItem('seekvera_language_explicit')==='1'}catch{}const sel=String(document.getElementById('lang')?.value||'').toLowerCase().split(/[-_]/)[0];if(explicit&&sel&&sel!=='auto'&&LANGS[sel])return LANGS[sel];try{const saved=String(localStorage.getItem('seekvera_chat_voice_lang')||'');const c=codeOf(saved);if(c&&LANGS[c])return LANGS[c]}catch{}const nav=String((navigator.languages&&navigator.languages[0])||navigator.language||'');if(nav)return nav;if(lastLocale&&/^[a-z]{2,3}(?:-|$)/i.test(lastLocale))return lastLocale;return 'en-US'}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65 voice locale anchor missing')
anchor="function localeForText(t,requested){"
helper="function rememberChatVoiceLanguage(v,text=''){let c=codeOf(v);if(!c){const x=String(text||'');if(/[\\u0600-\\u06ff]/.test(x))c='ar';else if(/[\\u4e00-\\u9fff]/.test(x))c='zh';else if(/[\\u3040-\\u30ff]/.test(x))c='ja';else if(/[\\uac00-\\ud7af]/.test(x))c='ko';else if(/[\\u0900-\\u097f]/.test(x))c='hi';else if(/[\\u0980-\\u09ff]/.test(x))c='bn';else if(/[\\u0400-\\u04ff]/.test(x))c='ru';else if(/[\\u0590-\\u05ff]/.test(x))c='he';else if(/[\\u0370-\\u03ff]/.test(x))c='el';else if(/[\\u0e00-\\u0e7f]/.test(x))c='th';else if(/[\\u1200-\\u137f]/.test(x))c='am'}if(c&&LANGS[c])try{localStorage.setItem('seekvera_chat_voice_lang',c)}catch{}}\n"
if 'function rememberChatVoiceLanguage(' not in s:
    if anchor not in s:raise SystemExit('R65 voice memory insertion missing')
    s=s.replace(anchor,helper+anchor,1)
old="window.addEventListener('seekvera:ai-response',e=>{const voiceMode=localStorage.getItem('seekvera_voice_mode')==='1',auto=voiceConversation||Date.now()<voiceReplyDeadline||voiceMode;if(auto)voiceReplyDeadline=0;speak(e.detail?.text,e.detail?.language,auto)});"
new="window.addEventListener('seekvera:ai-response',e=>{const d=e.detail||{},voiceMode=localStorage.getItem('seekvera_voice_mode')==='1',auto=voiceConversation||Date.now()<voiceReplyDeadline||voiceMode;if(auto)voiceReplyDeadline=0;if(d.text){rememberChatVoiceLanguage(d.language,d.text);speak(d.text,d.language,auto)}});"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65 ai-response voice memory anchor missing')
s=s.replace('r.maxAlternatives=1;','r.maxAlternatives=3;',1)
p.write_text(s,encoding='utf-8')

for name in ('superapp.js','r60-runtime-guard.js','sw.js'):
    p=Path(name);x=p.read_text(encoding='utf-8').replace(OLD,VER);p.write_text(x,encoding='utf-8')

print('R65 worldwide control + country-independent chat language applied')
