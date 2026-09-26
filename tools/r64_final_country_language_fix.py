from pathlib import Path
import re

VER='20260926-r64-final-ai-voice'

# Start from the unified live AI/voice repair so R64 is reproducible.
import runpy
runpy.run_path('tools/r63_unified_live_ai_voice.py', run_name='__main__')

# 1) App-control ambiguity: country names win over language substrings.
p=Path('r24-ai-controller.js')
s=p.read_text(encoding='utf-8')
s=s.replace('20260926-r63-unified-live-ai-voice',VER)
old="if(!mentionsLang&&!mentionsCountry){if(!language)language=findName(text,buildLanguageNames());if(!language&&!country)country=findName(text,buildCountryNames())}"
new="if(!mentionsLang&&!mentionsCountry){if(!country)country=findName(text,buildCountryNames());if(!country&&!language)language=findName(text,buildLanguageNames())}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R64 control precedence anchor missing')
s=s.replace("setTimeout(()=>ctl.abort(),6500)","setTimeout(()=>ctl.abort(),3200)",1)
p.write_text(s,encoding='utf-8')

# 2) Browser-side intent must understand common job words in the user's language.
p=Path('r31-ui-polish.js')
s=p.read_text(encoding='utf-8').replace('20260926-r63-unified-live-ai-voice',VER)
old="job|jobs|career|vacancy|work|employment|hiring|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام"
extra="job|jobs|career|vacancy|work|employment|hiring|travail|emploi|emplois|trabajo|empleo|trabalho|emprego|lavoro|arbeit|stellen|stelle|iş|is ilanı|iş ilanı|работ|ваканси|工作|职位|仕事|求人|직업|채용|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام"
if old in s:s=s.replace(old,extra,1)
elif 'travail|emploi|emplois' not in s:raise SystemExit('R64 browser multilingual jobs anchor missing')
p.write_text(s,encoding='utf-8')

# 3) AI language detection and multilingual intent/fallback.
p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8').replace('20260926-r63-unified-live-ai-voice',VER)
old="const n=' '+t.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')+' ';const tests="
new="const n=' '+t.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')+' ';if(/\\b(i am|i'm|im |looking for|i need|i want|please help|find me|help me|can you|could you)\\b/.test(n))return'en';const tests="
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R64 English detection anchor missing')
s=s.replace("['de',/\\b(hallo|ich|suche|arbeit|job|mochte|bitte|danke|fur|mit)\\b/]","['de',/\\b(hallo|ich|suche|arbeit|mochte|bitte|danke|fur|mit)\\b/]",1)

pat=re.compile(r"\['jobs',/([^/]+)/u\]")
m=pat.search(s)
if not m:raise SystemExit('R64 jobs category regex missing')
expr=m.group(1)
for x in ['travail','emploi','emplois','trabajo','empleo','trabalho','emprego','lavoro','arbeit','stellen','stelle','iş','is ilanı','iş ilanı','работ','ваканси','工作','职位','仕事','求人','직업','채용','وظيفة','وظائف','عمل','شغل']:
    if x not in expr:expr+='|'+x
s=s[:m.start(1)]+expr+s[m.end(1):]

# Fast bounded public fallback; never leave the chat spinning for several seconds.
s=s.replace("AbortSignal.timeout(4500)","AbortSignal.timeout(1800)",1)

# Useful same-language fallback if Workers AI is out of quota/capacity.
start=s.find('function fallbackGuide(language,cat){')
end=s.find('\nasync function localizedFallback',start)
if start<0 or end<0:raise SystemExit('R64 fallbackGuide boundary missing')
fallback=r'''function fallbackGuide(language,cat){if(cat==='jobs'){if(language==='Arabic')return'أكيد. سأفتح لك قسم الوظائف مباشرة الآن. قل لي المدينة ونوع الشغل الذي تريده وسأضيّق لك النتائج.';if(language==='French')return'Bien sûr. Je vous dirige vers la section Emplois. Dites-moi la ville et le type de poste recherché pour affiner les résultats.';if(language==='Spanish')return'Claro. Te llevo directamente a Empleos. Dime la ciudad y el tipo de trabajo que buscas para afinar los resultados.';if(language==='Portuguese')return'Claro. Vou levá-lo diretamente para Empregos. Diga a cidade e o tipo de trabalho que procura para refinar os resultados.';if(language==='German')return'Natürlich. Ich öffne direkt den Bereich Jobs. Nennen Sie mir Stadt und Art der Arbeit, damit ich die Ergebnisse eingrenzen kann.';if(language==='Italian')return'Certo. Ti porto direttamente nella sezione Lavori. Dimmi la città e il tipo di lavoro che cerchi per restringere i risultati.';if(language==='Turkish')return'Elbette. Sizi doğrudan İşler bölümüne götürüyorum. Sonuçları daraltmak için şehir ve iş türünü söyleyin.';return'Absolutely. I’m taking you directly to Jobs now. Tell me the city and job type you want and I’ll narrow the results.'}const routeName={travel:'travel',property:'property',cars:'cars',shopping:'shopping',business:'business sourcing',health:'health',restaurants:'restaurants',connectivity:'connectivity',media:'media',general:'marketplace'}[cat]||'marketplace';if(language==='Arabic')return`تمام. سأنتقل بك مباشرة إلى القسم المناسب الآن. إذا بقي تفصيل ضروري واحد فقط، سأطلبه منك هناك.`;return`Done. I’m taking you directly to the right section now. If one essential detail is still missing, I’ll ask for it there.`}'''
s=s[:start]+fallback+s[end:]
old="async function staticPackAIFallback(req,env,b,language,cat,detectedCode){const code=inputLangCode(detectedCode||b?.language);try{"
new="async function staticPackAIFallback(req,env,b,language,cat,detectedCode){const code=inputLangCode(detectedCode||b?.language);if(cat==='jobs'&&['Arabic','English','French','Spanish','Portuguese','German','Italian','Turkish'].includes(language))return{text:fallbackGuide(language,cat),model:'seekvera-local-guide-'+code+'-fallback'};try{"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R64 contextual fallback anchor missing')

# 4) Force every core runtime reference to the same release, including the guard itself.
# Also make runtime JS no-store through the Worker so old mobile caches cannot win.
inject_old="text=text.replace(/voice-ai\\.js(?:\\?[^\\\"'<> ]*)?/g,'voice-ai.js?v=20260926-r64-final-ai-voice');text=text.replace(/superapp\\.js(?:\\?[^\\\"'<> ]*)?/g,'superapp.js?v=20260926-r64-final-ai-voice');text=text.replace(/r31-ui-polish\\.js(?:\\?[^\\\"'<> ]*)?/g,'r31-ui-polish.js?v=20260926-r64-final-ai-voice');"
inject_new=inject_old+"text=text.replace(/r60-runtime-guard\\.js(?:\\?[^\\\"'<> ]*)?/g,'r60-runtime-guard.js?v=20260926-r64-final-ai-voice');text=text.replace(/r24-ai-controller\\.js(?:\\?[^\\\"'<> ]*)?/g,'r24-ai-controller.js?v=20260926-r64-final-ai-voice');text=text.replace(/navigation\\.js(?:\\?[^\\\"'<> ]*)?/g,'navigation.js?v=20260926-r64-final-ai-voice');"
if inject_old in s and 'text.replace(/r60-runtime-guard' not in s:s=s.replace(inject_old,inject_new,1)

old="const r=await r30.fetch(request,env,ctx);return u.pathname.startsWith('/api/')?r:inject(r)}};"
new="const r=await r30.fetch(request,env,ctx);if(/^\\/(?:voice-ai|r24-ai-controller|r31-ui-polish|r60-runtime-guard|superapp|navigation)\\.js$/.test(u.pathname)){const h=new Headers(r.headers);h.delete('content-length');h.set('cache-control','no-store, max-age=0');h.set('x-seekvera-release','r64-final-ai-voice');return new Response(r.body,{status:r.status,statusText:r.statusText,headers:h})}return u.pathname.startsWith('/api/')?r:inject(r)}};"
if old in s:s=s.replace(old,new,1)
elif "cache-control','no-store, max-age=0'" not in s:raise SystemExit('R64 runtime no-store anchor missing')
s=s.replace("h.set('x-seekvera-release','r63-unified-live-ai-voice')","h.set('x-seekvera-release','r64-final-ai-voice')",1)
p.write_text(s,encoding='utf-8')

# 5) Final release marker/cache bust across every runtime and page.
for name in ('superapp.js','voice-ai.js','r60-runtime-guard.js','sw.js'):
    p=Path(name);x=p.read_text(encoding='utf-8').replace('20260926-r63-unified-live-ai-voice',VER);p.write_text(x,encoding='utf-8')

for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    x=p.read_text(encoding='utf-8').replace('20260926-r63-unified-live-ai-voice',VER)
    if 'data-release=' in x:x=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',x,count=1)
    for name in ('superapp.js','voice-ai.js','r31-ui-polish.js','r24-ai-controller.js','r60-runtime-guard.js','navigation.js'):
        x=re.sub(re.escape(name)+r'(?:\?v=[^"\'<> ]*)?',name+'?v='+VER,x)
    p.write_text(x,encoding='utf-8')

print('R64 unified production parity patch applied')
