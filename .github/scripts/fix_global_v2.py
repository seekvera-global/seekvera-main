from pathlib import Path
import re


def must_replace(text, old, new, label):
    if old not in text:
        raise SystemExit(f'{label}: expected source not found')
    return text.replace(old, new, 1)


# Server AI: reply in the language actually used by the person, independent of country.
p = Path('worker.js')
s = p.read_text(encoding='utf-8')
s = must_replace(
    s,
    "Reply in the user language. Understand cross-border intent.",
    "Automatically detect the language of the user's latest message and reply in that same language and script, independent of country or location. If the user explicitly asks for a different reply language, use that requested language. Never default to English merely because the country, interface or browser is English. Understand multilingual and cross-border intent.",
    'worker same-language prompt',
)
s = must_replace(
    s,
    " Voice mode: answer as short natural spoken sentences in the requested language. Do not use markdown, bullet symbols, tables, raw URLs or hard-to-pronounce abbreviations.",
    " Voice mode: answer as short natural spoken sentences in the same language the user spoke, unless the user explicitly asks for another language. Do not use markdown, bullet symbols, tables, raw URLs or hard-to-pronounce abbreviations.",
    'worker voice prompt',
)
p.write_text(s, encoding='utf-8')


# Voice runtime: all pages, better female/natural voice preference, visible conversation mirroring.
p = Path('voice-ai.js')
s = p.read_text(encoding='utf-8')
s = must_replace(
    s,
    "const RTL=/^(ar|fa|ur)(-|$)/i;\nlet recognition=null,listenTimer=null,lastAnswer='',lastLang='',muted=localStorage.getItem('seekvera_voice_muted')==='1';",
    "const RTL=/^(ar|fa|ur)(-|$)/i;\nconst FEMALE_HINTS=/aria|jenny|zira|samantha|victoria|karen|moira|tessa|ava|allison|susan|hazel|fiona|serena|veena|heera|lekha|monica|amelie|audrey|julie|celine|hortense|laila|layla|salma|hoda|farah|mariam|maryam|amira|zahra|female|woman/i;\nconst MALE_HINTS=/david|mark|george|daniel|fred|ralph|bruce|hammad|hamed|majed|maged|male|man/i;\nconst QUALITY_HINTS=/neural|natural|enhanced|premium|online|google|microsoft|siri/i;\nlet recognition=null,listenTimer=null,lastAnswer='',lastLang='',muted=localStorage.getItem('seekvera_voice_muted')==='1';",
    'voice constants',
)
s = must_replace(
    s,
    "function pickVoice(locale){\n  const voices=speechSynthesis.getVoices?.()||[]; if(!voices.length)return null;\n  const exact=voices.find(v=>v.lang?.toLowerCase()===locale.toLowerCase()); if(exact)return exact;\n  const base=locale.split('-')[0].toLowerCase(); return voices.find(v=>v.lang?.toLowerCase().startsWith(base))||null;\n}",
    "function pickVoice(locale){\n  const voices=window.speechSynthesis?.getVoices?.()||[]; if(!voices.length)return null;\n  const wanted=String(locale||'en-US').toLowerCase(),base=wanted.split('-')[0];\n  let candidates=voices.filter(v=>String(v.lang||'').toLowerCase().startsWith(base)); if(!candidates.length)candidates=voices;\n  const score=v=>{const name=(v.name||'')+' '+(v.voiceURI||''),vl=String(v.lang||'').toLowerCase();let n=0;if(vl===wanted)n+=120;else if(vl.startsWith(base))n+=75;if(QUALITY_HINTS.test(name))n+=38;if(FEMALE_HINTS.test(name))n+=45;if(MALE_HINTS.test(name))n-=55;if(v.default)n+=8;if(v.localService===false)n+=8;return n};\n  return [...candidates].sort((a,b)=>score(b)-score(a))[0]||null;\n}",
    'voice picker',
)
s = must_replace(
    s,
    "const next=()=>{if(muted||i>=chunks.length)return;const u=new SpeechSynthesisUtterance(chunks[i++]);u.lang=lastLang;const v=pickVoice(lastLang);if(v)u.voice=v;u.rate=/^(ar|fa|ur)(-|$)/i.test(lastLang)?.90:.94;u.pitch=1;u.onend=next;u.onerror=()=>{};speechSynthesis.speak(u)};",
    "const next=()=>{if(muted||i>=chunks.length)return;const u=new SpeechSynthesisUtterance(chunks[i++]);u.lang=lastLang;const v=pickVoice(lastLang);if(v)u.voice=v;const rtl=/^(ar|fa|ur)(-|$)/i.test(lastLang);u.rate=rtl?.98:1.02;u.pitch=rtl?1.06:1.09;u.volume=1;u.onend=next;u.onerror=()=>{};speechSynthesis.speak(u)};",
    'voice playback',
)
s = s.replace("  if(location.pathname.endsWith('/app.html'))return;\n", '', 1)
s = must_replace(
    s,
    "    try{\n      const msgs=document.getElementById('aiMessages');\n      if(msgs){\n        const u=document.createElement('div');u.className='ai-msg user';u.textContent=clean;msgs.appendChild(u);\n        const b=document.createElement('div');b.className='ai-msg bot';b.textContent=answer;msgs.appendChild(b);msgs.scrollTop=msgs.scrollHeight;\n      }\n    }catch(_){ }",
    "    try{\n      const msgs=document.getElementById('aiMessages');\n      if(msgs){const u=document.createElement('div');u.className='ai-msg user';u.textContent=clean;msgs.appendChild(u);const b=document.createElement('div');b.className='ai-msg bot';b.textContent=answer;msgs.appendChild(b);msgs.scrollTop=msgs.scrollHeight;}\n      const globalMsgs=document.getElementById('svGlobalMessages');\n      if(globalMsgs){const u=document.createElement('div');u.className='sv-global-msg user';u.textContent=clean;globalMsgs.appendChild(u);const b=document.createElement('div');b.className='sv-global-msg bot';b.textContent=answer;globalMsgs.appendChild(b);globalMsgs.scrollTop=globalMsgs.scrollHeight;}\n    }catch(_){ }",
    'voice chat mirroring',
)
anchor = "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',build,{once:true});else build();"
if "seekvera:voice" not in s:
    s = must_replace(s, anchor, "window.addEventListener('seekvera:voice',()=>{if(document.getElementById('svVoiceFab'))startListening()});\n" + anchor, 'voice event')
p.write_text(s, encoding='utf-8')


# Homepage language picker: Auto for new users; explicit selections remain.
p = Path('superapp.js')
s = p.read_text(encoding='utf-8')
s = must_replace(s, "const LANGS=[['en','English']", "const LANGS=[['auto','Auto · Same as my language'],['en','English']", 'language list')
s = must_replace(
    s,
    "const saved=localStorage.getItem('seekvera_lang');if(saved&&LANGS.some(x=>x[0]===saved))el.value=saved;",
    "const saved=localStorage.getItem('seekvera_lang');if(saved&&LANGS.some(x=>x[0]===saved))el.value=saved;else el.value='auto';",
    'language default',
)
s = must_replace(
    s,
    "document.documentElement.lang=el.value;document.documentElement.dir=/^(ar|fa|ur)$/.test(el.value)?'rtl':'ltr';",
    "document.documentElement.lang=el.value==='auto'?((navigator.language||'en').split('-')[0]):el.value;document.documentElement.dir=/^(ar|fa|ur)$/.test(el.value)?'rtl':'ltr';",
    'language document mode',
)
p.write_text(s, encoding='utf-8')


# All public pages/departments use identical premium chat/voice assets and a fresh cache key.
css = '<link rel="stylesheet" href="global-ui.css?v=20260922-premium-voice2">'
voice = '<script src="voice-ai.js?v=20260922-premium-voice2" defer></script>'
gui = '<script src="global-ui.js?v=20260922-premium-voice2" defer></script>'
pages = []
for p in sorted(Path('.').glob('*.html')):
    if p.name.lower().startswith('google'):
        continue
    text = p.read_text(encoding='utf-8')
    text = re.sub(r'<link rel="stylesheet" href="global-ui\.css\?v=[^"]+">', css, text)
    if 'global-ui.css' not in text:
        text = text.replace('</head>', css + '\n</head>', 1)
    text = re.sub(r'<script src="voice-ai\.js(?:\?v=[^"]+)?" defer></script>', voice, text)
    if 'voice-ai.js' not in text:
        text = text.replace('</body>', voice + '\n</body>', 1)
    text = re.sub(r'<script src="global-ui\.js\?v=[^"]+" defer></script>', gui, text)
    if 'global-ui.js' not in text:
        text = text.replace('</body>', gui + '\n</body>', 1)
    p.write_text(text, encoding='utf-8')
    pages.append(p.name)

bad = []
for name in pages:
    t = Path(name).read_text(encoding='utf-8')
    for needle in (
        'global-ui.css?v=20260922-premium-voice2',
        'voice-ai.js?v=20260922-premium-voice2',
        'global-ui.js?v=20260922-premium-voice2',
    ):
        if needle not in t:
            bad.append(f'{name}: missing {needle}')
if bad:
    raise SystemExit('\n'.join(bad))

print(f'Public pages/departments covered: {len(pages)}')
print('Global multilingual chat + voice patch complete.')
