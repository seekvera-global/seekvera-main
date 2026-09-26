from pathlib import Path
import runpy,re

# Rebuild R65 deterministically from the persisted R64 source.
runpy.run_path('tools/r65_worldwide_chat_language.py', run_name='__main__')
OLD='20260926-r65-worldwide-chat-language'
VER='20260926-r65b-message-language-priority'

# 1) The latest message itself is authoritative. Browser/device/country must never
# pre-empt script detection (Arabic typed on an English phone must stay Arabic).
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
old="const messageLanguageCode=detectMessageLanguageCode(m,b.language==='auto'?(b.browserLanguage||'auto'):b.language),language=langName(messageLanguageCode,m),hinted="
new="const messageLanguageCode=detectMessageLanguageCode(m,b.language),language=langName(messageLanguageCode,m),hinted="
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65B message-language priority anchor missing')
s=s.replace("h.set('x-seekvera-release','r65-worldwide-chat-language')","h.set('x-seekvera-release','r65b-message-language-priority')",1)
p.write_text(s,encoding='utf-8')

# 2) Do not replace a valid, already-localized server reply with a slower browser
# backup merely because the server used a degraded/static multilingual fallback.
p=Path('r24-ai-controller.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
old="if(!data?.blocked&&!data?.reviewRequired&&(res.status===503||data?.degraded===true||data?.model==='seekvera-local-router'||/fallback|static|local-guide/i.test(String(data?.model||'')))){"
new="if(!data?.blocked&&!data?.reviewRequired&&!String(data?.response||'').trim()&&(res.status===503||data?.degraded===true||data?.model==='seekvera-local-router'||/fallback|static|local-guide/i.test(String(data?.model||'')))){"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65B valid-reply fast path anchor missing')
p.write_text(s,encoding='utf-8')

# 3) Remember the language of a typed user message immediately for the NEXT mic
# turn. This makes voice follow the conversation rather than the selected country.
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
anchor="q=String(q||'').trim().slice(0,1800);if(!q||submitting)return;submitting=true;"
insert=anchor+"try{let vc='';if(/[\\u0600-\\u06ff]/u.test(q))vc='ar';else if(/[\\u4e00-\\u9fff]/u.test(q))vc='zh';else if(/[\\u3040-\\u30ff]/u.test(q))vc='ja';else if(/[\\uac00-\\ud7af]/u.test(q))vc='ko';else if(/[\\u0900-\\u097f]/u.test(q))vc='hi';else if(/[\\u0980-\\u09ff]/u.test(q))vc='bn';else if(/[\\u0400-\\u04ff]/u.test(q))vc='ru';else if(/[\\u0590-\\u05ff]/u.test(q))vc='he';else if(/[\\u0370-\\u03ff]/u.test(q))vc='el';else if(/[\\u0e00-\\u0e7f]/u.test(q))vc='th';else if(/[\\u1200-\\u137f]/u.test(q))vc='am';if(vc)localStorage.setItem('seekvera_chat_voice_lang',vc)}catch{}"
if insert not in s:
    if anchor not in s:raise SystemExit('R65B submit language memory anchor missing')
    s=s.replace(anchor,insert,1)
p.write_text(s,encoding='utf-8')

# Release markers/cache busting.
for name in ('voice-ai.js','superapp.js','r60-runtime-guard.js','sw.js'):
    p=Path(name);x=p.read_text(encoding='utf-8').replace(OLD,VER);p.write_text(x,encoding='utf-8')
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    x=p.read_text(encoding='utf-8').replace(OLD,VER)
    for name in ('superapp.js','voice-ai.js','r31-ui-polish.js','r24-ai-controller.js','r60-runtime-guard.js'):
        x=re.sub(re.escape(name)+r'(?:\?v=[^"\'<> ]*)?',name+'?v='+VER,x)
    p.write_text(x,encoding='utf-8')
print('R65B message language priority applied')
