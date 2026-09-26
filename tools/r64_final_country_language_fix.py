from pathlib import Path
import re

VER='20260926-r64-final-ai-voice'

# Apply the full R63 repair first so this patch is reproducible from main.
import runpy
runpy.run_path('tools/r63_unified_live_ai_voice.py', run_name='__main__')

# 1) App-control ambiguity: when the user says "take me / put me + Turkey",
# country names must win over language names. "حطلي تركي" still resolves to Turkish.
p=Path('r24-ai-controller.js')
s=p.read_text(encoding='utf-8')
s=s.replace('20260926-r63-unified-live-ai-voice',VER)
old="if(!mentionsLang&&!mentionsCountry){if(!language)language=findName(text,buildLanguageNames());if(!language&&!country)country=findName(text,buildCountryNames())}"
new="if(!mentionsLang&&!mentionsCountry){if(!country)country=findName(text,buildCountryNames());if(!country&&!language)language=findName(text,buildLanguageNames())}"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('R64 control precedence anchor missing')
p.write_text(s,encoding='utf-8')

# 2) AI language detection: explicit English phrases before Latin-language heuristics;
# never use the generic English word "job" as a German-language signal.
p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8')
s=s.replace('20260926-r63-unified-live-ai-voice',VER)
old="const n=' '+t.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')+' ';const tests="
new="const n=' '+t.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')+' ';if(/\\b(i am|i'm|im |looking for|i need|i want|please help|find me|help me|can you|could you)\\b/.test(n))return'en';const tests="
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('R64 English detection anchor missing')
s=s.replace("['de',/\\b(hallo|ich|suche|arbeit|job|mochte|bitte|danke|fur|mit)\\b/]","['de',/\\b(hallo|ich|suche|arbeit|mochte|bitte|danke|fur|mit)\\b/]",1)

# Strengthen multilingual job intent in the actual category matcher regardless of older text shape.
pat=re.compile(r"\['jobs',/([^/]+)/u\]")
m=pat.search(s)
if not m:
    raise SystemExit('R64 jobs category regex missing')
expr=m.group(1)
extras=['travail','emploi','trabajo','empleo','trabalho','lavoro','arbeit','iş','is ilanı','работ','工作','仕事','직업','وظيفة','وظائف','عمل','شغل']
for x in extras:
    if x not in expr:
        expr += '|'+x
s=s[:m.start(1)]+expr+s[m.end(1):]

# Static/local degraded fallback should remain useful for a clear jobs request.
old="if(r.ok){const d=await r.json(),text=clean(d?.translations?.[STATIC_AI_SOURCE],1800);if(text&&text!==STATIC_AI_SOURCE)return{text,model:'seekvera-static-'+code+'-fallback'}}"
new="if(r.ok){const d=await r.json(),text=clean(d?.translations?.[STATIC_AI_SOURCE],1800);if(cat==='jobs'&&(language==='Arabic'||language==='English'))return{text:fallbackGuide(language,cat),model:'seekvera-local-guide-'+code+'-fallback'};if(text&&text!==STATIC_AI_SOURCE)return{text,model:'seekvera-static-'+code+'-fallback'}}"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('R64 useful fallback anchor missing')

# Final release header/cache-busting references.
s=s.replace("h.set('x-seekvera-release','r63-unified-live-ai-voice')","h.set('x-seekvera-release','r64-final-ai-voice')",1)
p.write_text(s,encoding='utf-8')

for name in ('superapp.js','voice-ai.js','r31-ui-polish.js','r60-runtime-guard.js','sw.js'):
    p=Path(name)
    x=p.read_text(encoding='utf-8').replace('20260926-r63-unified-live-ai-voice',VER)
    p.write_text(x,encoding='utf-8')

# Update every HTML reference to the same final asset version.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):
        continue
    x=p.read_text(encoding='utf-8').replace('20260926-r63-unified-live-ai-voice',VER)
    for name in ('superapp.js','voice-ai.js','r31-ui-polish.js','r24-ai-controller.js','r60-runtime-guard.js'):
        x=re.sub(re.escape(name)+r'(?:\?v=[^"\'<> ]*)?',name+'?v='+VER,x)
    p.write_text(x,encoding='utf-8')

print('R64 final country/language AI voice patch applied')
