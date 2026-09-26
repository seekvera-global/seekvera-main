from pathlib import Path

# Country vs language ambiguity: "تركيا" contains "تركي" as a substring.
# When the command does not explicitly say country/language, resolve a country
# name first; "تركي" still resolves as language because it is not the country name.
p=Path('r24-ai-controller.js');s=p.read_text(encoding='utf-8')
old="if(!mentionsLang&&!mentionsCountry){if(!language)language=findName(text,buildLanguageNames());if(!language&&!country)country=findName(text,buildCountryNames())}"
new="if(!mentionsLang&&!mentionsCountry){if(!country)country=findName(text,buildCountryNames());if(!country&&!language)language=findName(text,buildLanguageNames())}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R63B control priority anchor missing')
# Keep the optional browser AI backup bounded. It is a backup, never the main path.
s=s.replace("setTimeout(()=>ctl.abort(),6500)","setTimeout(()=>ctl.abort(),3200)",1)
p.write_text(s,encoding='utf-8')

p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
# "job" is English too, so it must not be a German-language discriminator.
s=s.replace("['de',/\\b(hallo|ich|suche|arbeit|job|mochte|bitte|danke|fur|mit)\\b/]","['de',/\\b(hallo|ich|suche|arbeit|mochte|bitte|danke|fur|mit)\\b/]",1)
# Fast failure to the deterministic localized fallback if the public backup is slow.
s=s.replace("AbortSignal.timeout(4500)","AbortSignal.timeout(1800)",1)
# Contextual job fallback in the most common Latin languages instead of a generic intro.
old="function fallbackGuide(language,cat){if(cat==='jobs'){if(language==='Arabic')return'أكيد. سأفتح لك قسم الوظائف مباشرة الآن. قل لي هناك البلد أو المدينة ونوع الشغل الذي تريده حتى أضيّق لك النتائج.';return'Absolutely. I’m taking you directly to Jobs now. Tell me the country/city and job type there and I’ll narrow the results.'}"
new="function fallbackGuide(language,cat){if(cat==='jobs'){if(language==='Arabic')return'أكيد. سأفتح لك قسم الوظائف مباشرة الآن. قل لي المدينة ونوع الشغل الذي تريده وسأضيّق لك النتائج.';if(language==='French')return'Bien sûr. Je vous dirige vers la section Emplois. Dites-moi la ville et le type de poste recherché pour affiner les résultats.';if(language==='Spanish')return'Claro. Te llevo directamente a Empleos. Dime la ciudad y el tipo de trabajo que buscas para afinar los resultados.';if(language==='Portuguese')return'Claro. Vou levá-lo diretamente para Empregos. Diga a cidade e o tipo de trabalho que procura para refinar os resultados.';if(language==='German')return'Natürlich. Ich öffne direkt den Bereich Jobs. Nennen Sie mir Stadt und Art der Arbeit, damit ich die Ergebnisse eingrenzen kann.';if(language==='Italian')return'Certo. Ti porto direttamente nella sezione Lavori. Dimmi la città e il tipo di lavoro che cerchi per restringere i risultati.';if(language==='Turkish')return'Elbette. Sizi doğrudan İşler bölümüne götürüyorum. Sonuçları daraltmak için şehir ve iş türünü söyleyin.';return'Absolutely. I’m taking you directly to Jobs now. Tell me the city and job type you want and I’ll narrow the results.'}"
if old in s:s=s.replace(old,new,1)
elif "if(language==='French')return'Bien sûr." not in s:raise SystemExit('R63B fallbackGuide anchor missing')
old="async function staticPackAIFallback(req,env,b,language,cat,detectedCode){const code=inputLangCode(detectedCode||b?.language);try{"
new="async function staticPackAIFallback(req,env,b,language,cat,detectedCode){const code=inputLangCode(detectedCode||b?.language);if(cat==='jobs'&&['Arabic','English','French','Spanish','Portuguese','German','Italian','Turkish'].includes(language))return{text:fallbackGuide(language,cat),model:'seekvera-local-guide-'+code+'-fallback'};try{"
if old in s:s=s.replace(old,new,1)
elif "model:'seekvera-local-guide-'+code+'-fallback'" not in s:raise SystemExit('R63B contextual fallback anchor missing')
p.write_text(s,encoding='utf-8')

print('R63B country/language precision and contextual fallback patched')
