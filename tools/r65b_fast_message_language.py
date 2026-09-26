from pathlib import Path
import re, runpy

# Start from the audited R65 repair on top of the persisted R64 baseline.
runpy.run_path('tools/r65_worldwide_chat_language.py', run_name='__main__')
OLD='20260926-r65-worldwide-chat-language'
VER='20260926-r65b-worldwide-chat-language'

# Do not delay a valid server reply by invoking a second browser AI provider.
p=Path('r24-ai-controller.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
old="res.status===503||data?.degraded===true||data?.model==='seekvera-local-router'||/fallback|static|local-guide/i.test(String(data?.model||''))"
new="res.status===503||data?.model==='seekvera-local-router'||!String(data?.response||'').trim()"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R65B browser backup trigger anchor missing')
p.write_text(s,encoding='utf-8')

# Give the server's bounded fallback path enough time to return.
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
s=s.replace("setTimeout(()=>c.abort(),4200)","setTimeout(()=>c.abort(),7500)",1)
p.write_text(s,encoding='utf-8')

# Latest-message language beats browser/country/UI. Browser language is only the final tiebreaker.
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
start=s.find("function detectMessageLanguageCode(text,hint='auto'){")
end=s.find("\nasync function publicAIFallback",start)
if start<0 or end<0:raise SystemExit('R65B detector bounds missing')
new_detector=r'''function detectMessageLanguageCode(text,hint='auto'){const t=String(text||''),h=String(hint||'auto').toLowerCase().split(/[-_ ]/)[0];if(/[\u0600-\u06ff]/u.test(t))return'ar';if(/[\u0590-\u05ff]/u.test(t))return'he';if(/[\u0900-\u097f]/u.test(t))return'hi';if(/[\u0980-\u09ff]/u.test(t))return'bn';if(/[\u4e00-\u9fff]/u.test(t))return'zh';if(/[\u3040-\u30ff]/u.test(t))return'ja';if(/[\uac00-\ud7af]/u.test(t))return'ko';if(/[\u0e00-\u0e7f]/u.test(t))return'th';if(/[\u0370-\u03ff]/u.test(t))return'el';if(/[\u1200-\u137f]/u.test(t))return'am';if(/[\u0400-\u04ff]/u.test(t))return'ru';if(/[\u0b80-\u0bff]/u.test(t))return'ta';if(/[\u0c00-\u0c7f]/u.test(t))return'te';if(/[\u0d00-\u0d7f]/u.test(t))return'ml';if(/[\u0a80-\u0aff]/u.test(t))return'gu';if(/[\u0a00-\u0a7f]/u.test(t))return'pa';if(/[\u1780-\u17ff]/u.test(t))return'km';if(/[\u0e80-\u0eff]/u.test(t))return'lo';if(/[\u1000-\u109f]/u.test(t))return'my';if(/[\u0d80-\u0dff]/u.test(t))return'si';if(/[\u0f00-\u0fff]/u.test(t))return'dz';const n=' '+t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')+' ';if(/\b(i am|i'm|im |looking for|i need|i want|please help|find me|help me|can you|could you|what|why|how|where|when|hello|thanks|thank you)\b/.test(n))return'en';const tests=[['fr',/\b(bonjour|salut|je|vous|cherche|travail|emploi|avec|pour|dans|aux|une|des|merci|comment|besoin|aider)\b/],['es',/\b(hola|busco|trabajo|empleo|quiero|para|con|una|gracias|pais|como|puedes|ayuda)\b/],['pt',/\b(ola|procuro|trabalho|emprego|quero|para|com|uma|obrigado|ajuda|voce)\b/],['de',/\b(hallo|ich|suche|arbeit|mochte|bitte|danke|fur|mit|wie|hilfe)\b/],['it',/\b(ciao|cerco|lavoro|voglio|per|con|grazie|una|aiuto|come)\b/],['tr',/\b(merhaba|is|iş|ariyorum|arıyorum|istiyorum|icin|için|tesekkur|teşekkür|yardim|yardım|nasıl)\b/],['nl',/\b(hallo|ik|zoek|werk|baan|voor|met|dank|hoe|help)\b/],['id',/\b(hai|saya|mencari|kerja|pekerjaan|untuk|dengan|terima kasih|bantu)\b/],['ms',/\b(saya|mencari|kerja|pekerjaan|untuk|dengan|terima kasih|bantu)\b/],['sw',/\b(habari|natafuta|kazi|kwa|asante|msaada|naweza)\b/],['fil',/\b(kumusta|ako|trabaho|hanap|para|salamat|tulong)\b/],['ro',/\b(buna|salut|caut|munca|vreau|multumesc|ajutor)\b/],['pl',/\b(czesc|szukam|pracy|chce|prosze|dziekuje|pomoc)\b/],['sv',/\b(hej|jag|soker|jobb|vill|tack|hjalp)\b/],['no',/\b(hei|jeg|soker|jobb|vil|takk|hjelp)\b/],['da',/\b(hej|jeg|soger|job|vil|tak|hjaelp)\b/],['fi',/\b(hei|mina|etsin|tyota|haluan|kiitos|apua)\b/]];for(const[c,r]of tests)if(r.test(n))return c;if(h&&h!=='auto'&&/^[a-z]{2,3}$/.test(h))return h;return'en'}'''
s=s[:start]+new_detector+s[end:]
p.write_text(s,encoding='utf-8')

# Carry the release marker through all served assets/pages.
for name in ('voice-ai.js','superapp.js','r60-runtime-guard.js','sw.js'):
    p=Path(name);x=p.read_text(encoding='utf-8').replace(OLD,VER);p.write_text(x,encoding='utf-8')
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    x=p.read_text(encoding='utf-8').replace(OLD,VER)
    for name in ('superapp.js','voice-ai.js','r31-ui-polish.js','r24-ai-controller.js','r60-runtime-guard.js'):
        x=re.sub(re.escape(name)+r'(?:\?v=[^"\'<> ]*)?',name+'?v='+VER,x)
    p.write_text(x,encoding='utf-8')
print('R65B fast message-language fix applied')
