from pathlib import Path
import re

WORLD = ['en','ar','fr','zh','es','hi','pt','de','ja','ko','id','tr','ru','ur','bn','vi','it','sw','th','fa','pl','nl','ms','fil','ha','yo','ig','am','he','el','uk','ro','cs','sk','hu','sv','no','da','fi','bg','hr','sr','sl','lt','lv','et','ca','eu','gl','is','sq','mk','ka','hy','az','kk','uz','ky','tg','tk','ne','si','ta','te','ml','mr','gu','pa','km','lo','my','mn','zu','af','be','bs','dz','ti','fo','kl','rw','sm','to','so','ps','dv','mt','mg','ga','cy','mi','fy','lb','rm','ku','xh','st','tn']

# -----------------------------------------------------------------------------
# Worker: dedicated low-cost translation model + global edge translation cache.
# -----------------------------------------------------------------------------
p = Path('worker.js')
s = p.read_text(encoding='utf-8')
model_anchor = "const PRIMARY='@cf/google/gemma-4-26b-a4b-it',FALLBACK='@cf/zai-org/glm-4.7-flash',LIGHT='@cf/qwen/qwen3-30b-a3b-fp8',FASTCHAT='@cf/meta/llama-3.1-8b-instruct-fast',VISION='@cf/google/gemma-4-26b-a4b-it',VISION_FALLBACK='@cf/qwen/qwen3.8-27b',ASR='@cf/openai/whisper-large-v3-turbo';"
if "const TRANSLATE='@cf/meta/llama-3.2-1b-instruct';" not in s:
    if model_anchor not in s:
        raise SystemExit('worker model anchor missing')
    s = s.replace(model_anchor, model_anchor + "\nconst TRANSLATE='@cf/meta/llama-3.2-1b-instruct';", 1)

route_pattern = re.compile(
    r"if\(u\.pathname==='/api/ui-translate'\)\{try\{.*?\}\s*catch\(e\)\{return j\(request,\{ok:false,error:'UI translation temporarily unavailable',retryable:true\},503\)\}\}",
    re.S,
)
m = route_pattern.search(s)
if not m:
    raise SystemExit('current ui-translate route not found')

route = r"""if(u.pathname==='/api/ui-translate'){try{
 const b=await request.json(),language=clean(b.language,80),strings=Array.isArray(b.strings)?b.strings.slice(0,12).map(x=>clean(x,700)):[];
 if(!language||!strings.length||strings.some(x=>!x))return j(request,{ok:false,error:'Language and strings are required'},400);
 const raw=language+'\u0000'+JSON.stringify(strings),dig=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)),hex=[...new Uint8Array(dig)].map(x=>x.toString(16).padStart(2,'0')).join('');
 const cache=await caches.open('seekvera-ui-translate-r12'),ck=new Request(new URL('/__sv_ui_translation/'+hex,request.url).toString(),{method:'GET'}),hit=await cache.match(ck);
 if(hit){try{const cached=await hit.json();if(cached?.ok&&Array.isArray(cached.translations))return j(request,{...cached,cached:true})}catch{}}
 if(!env.AI)return j(request,{ok:false,error:'Translation service unavailable',retryable:true,reason:'ai_binding_unavailable'},503);
 const sys='You are SEEKVERA UI translator. LANGUAGE LOCK: translate every supplied interface string fully into '+language+'. Return ONLY one valid JSON array of exactly '+strings.length+' strings, same order. No markdown, no keys, no explanation. Preserve SEEKVERA, URLs, currency codes, model names, emojis, punctuation placeholders and numbers. Translate labels, buttons, headings, descriptions and accessibility text naturally; never concatenate all items into one string.';
 let text='',model=TRANSLATE;
 try{text=out(await env.AI.run(TRANSLATE,{messages:[{role:'system',content:sys},{role:'user',content:JSON.stringify(strings)}],temperature:0,max_tokens:1200}))}
 catch(e){const em=clean(e?.message||e,500);if(/3036|daily free allocation|daily.*neuron/i.test(em))return j(request,{ok:false,error:'UI translation temporarily unavailable',retryable:true,reason:'daily_free_ai_limit'},503);const rr=await ai(env,[{role:'system',content:sys},{role:'user',content:JSON.stringify(strings)}],1200,0);text=rr.response;model=rr.model}
 const a=text.indexOf('['),z=text.lastIndexOf(']');if(a<0||z<=a)return j(request,{ok:false,error:'Translation format error',retryable:true},502);
 const arr=JSON.parse(text.slice(a,z+1));if(!Array.isArray(arr)||arr.length!==strings.length||arr.some(x=>typeof x!=='string'||!x.trim()))return j(request,{ok:false,error:'Translation count mismatch',retryable:true},502);
 const payload={ok:true,language,translations:arr.map(x=>String(x).trim()),model};
 try{await cache.put(ck,new Response(JSON.stringify(payload),{headers:{'content-type':'application/json; charset=utf-8','cache-control':'public, max-age=2592000'}}))}catch{}
 return j(request,payload)
 }catch(e){const em=clean(e?.message||e,500);return j(request,{ok:false,error:'UI translation temporarily unavailable',retryable:true,reason:/3036|daily free allocation|daily.*neuron/i.test(em)?'daily_free_ai_limit':'translation_error'},503)}}"""
s = s[:m.start()] + route + s[m.end():]
p.write_text(s, encoding='utf-8')

# -----------------------------------------------------------------------------
# i18n: 98-language runtime, persistent device cache, optional native desktop
# Translator API before using the Cloudflare translation endpoint.
# -----------------------------------------------------------------------------
p = Path('i18n-ui.js')
s = p.read_text(encoding='utf-8')
world_js = "const SUPPORTED=[" + ','.join(repr(x) for x in WORLD) + '];'
s, n = re.subn(r"const SUPPORTED=\[[^\]]+\];", world_js, s, count=1)
if n != 1:
    raise SystemExit('SUPPORTED list anchor missing')

old = "const textSource=new WeakMap(),attrSource=new WeakMap(),memory=new Map();\nlet applying=false,pending=false,timer=0,seq=0;"
new = "const textSource=new WeakMap(),attrSource=new WeakMap(),memory=new Map(),nativeTranslators=new Map();\nlet applying=false,pending=false,timer=0,seq=0;"
if old not in s:
    raise SystemExit('R9 state anchor missing')
s = s.replace(old, new, 1)

old = "function cacheKey(l,s){return l+'\\u0000'+s}\nfunction cached(l,s){return memory.get(cacheKey(l,s))||QUICK[l]?.[s]||''}\nfunction put(l,s,v){if(v&&v.trim())memory.set(cacheKey(l,s),v.trim())}"
new = """function cacheKey(l,s){return l+'\\u0000'+s}
function diskKey(l,s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return'sv_i18n_r12_'+l+'_'+(h>>>0).toString(36)}
function cached(l,s){const mem=memory.get(cacheKey(l,s))||QUICK[l]?.[s]||'';if(mem)return mem;try{return localStorage.getItem(diskKey(l,s))||''}catch{return''}}
function put(l,s,v){v=String(v||'').trim();if(!v)return;memory.set(cacheKey(l,s),v);try{localStorage.setItem(diskKey(l,s),v)}catch{}}
async function nativeTranslator(l){if(!('Translator'in self)||l==='en')return null;if(nativeTranslators.has(l))return nativeTranslators.get(l);try{const a=await Translator.availability({sourceLanguage:'en',targetLanguage:l});if(a!=='available')return null;const t=await Translator.create({sourceLanguage:'en',targetLanguage:l});nativeTranslators.set(l,t);return t}catch{return null}}
async function nativeBatch(l,arr){const out=new Map(),t=await nativeTranslator(l);if(!t)return out;for(const s of arr){try{const v=String(await t.translate(s)||'').trim();if(v&&v!==s){put(l,s,v);out.set(s,v)}}catch{}}return out}"""
if old not in s:
    raise SystemExit('R9 cache functions anchor missing')
s = s.replace(old, new, 1)

old = "async function batchTranslate(l,arr){if(!arr.length)return new Map();const out=new Map();for(let i=0;i<arr.length;i+=12){const batch=arr.slice(i,i+12);try{const r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:langName(l),strings:batch})});const d=await r.json().catch(()=>null);if(r.ok&&Array.isArray(d?.translations)&&d.translations.length===batch.length){batch.forEach((s,j)=>{const v=String(d.translations[j]||'').trim();if(v){put(l,s,v);out.set(s,v)}})}}catch{}}\n return out}"
new = """async function batchTranslate(l,arr){if(!arr.length)return new Map();const out=await nativeBatch(l,arr),remaining=arr.filter(s=>!out.has(s)&&!cached(l,s));for(let i=0;i<remaining.length;i+=12){const batch=remaining.slice(i,i+12);try{const r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:langName(l),strings:batch})});const d=await r.json().catch(()=>null);if(r.ok&&Array.isArray(d?.translations)&&d.translations.length===batch.length){batch.forEach((s,j)=>{const v=String(d.translations[j]||'').trim();if(v){put(l,s,v);out.set(s,v)}})}}catch{}}
 return out}"""
if old not in s:
    raise SystemExit('R9 batchTranslate anchor missing')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

# -----------------------------------------------------------------------------
# Navigation: static AI translation cache persists; country-control remains local
# and recognizes the local word for country/region across the worldwide set.
# -----------------------------------------------------------------------------
p = Path('navigation.js')
s = p.read_text(encoding='utf-8')
s = s.replace('/* SEEKVERA universal navigation + worldwide locale/voice hardening R10 */', '/* SEEKVERA universal navigation + worldwide locale/voice hardening R12 */', 1)
s = s.replace(
    "const cached=sessionStorage.getItem(key);if(cached){box.textContent=cached;box.dataset.svLang=l;return;}",
    "let cached='';try{cached=localStorage.getItem(key)||sessionStorage.getItem(key)||''}catch{}if(cached){box.textContent=cached;box.dataset.svLang=l;return;}",
    1,
)
s = s.replace(
    "if(r.ok&&t&&mine===translateSeq){sessionStorage.setItem(key,t);box.textContent=t;box.dataset.svLang=l;}",
    "if(r.ok&&t&&mine===translateSeq){try{localStorage.setItem(key,t)}catch{}box.textContent=t;box.dataset.svLang=l;}",
    1,
)

anchor = "function isCountryCommand(text){\n  const s=normalizeText(text);"
if anchor not in s:
    raise SystemExit('country command anchor missing')
terms = """country|region|دولة|الدولة|بلد|البلد|منطقة|pays|région|国家|地区|país|región|देश|क्षेत्र|região|land|国|地域|국가|지역|negara|wilayah|ülke|bölge|страна|регион|ملک|علاقہ|দেশ|অঞ্চল|quốc gia|khu vực|paese|regione|nchi|eneo|ประเทศ|ภูมิภาค|کشور|منطقه|kraj|regio|bansa|rehiyon|ƙasa|yanki|orilẹ-ede|agbegbe|obodo|mpaghara|ሀገር|ክልል|מדינה|אזור|χώρα|περιοχή|країна|регіон|țară|regiune|země|krajina|régión|ország|régió|maa|alue|държава|država|regija|šalis|regionas|valsts|reģions|riik|piirkond|regió|herrialde|eskualde|rexión|svæði|vend|rajon|земја|ქვეყანა|რეგიონი|երկիր|տարածաշրջան|ölkə|ел|аймақ|mamlakat|hudud|өлкө|аймак|кишвар|минтақа|ýurt|sebit|රට|කලාපය|நாடு|பகுதி|దేశం|ప్రాంతం|രാജ്യം|പ്രദേശം|प्रदेश|દેશ|ਪ੍ਰਦੇਸ਼|ਦੇਸ਼|ਖੇਤਰ|ប្រទេស|តំបន់|ປະເທດ|ພາກພື້ນ|နိုင်ငံ|ဒေသ|улс|бүс|izwe|isifunda|streek|краіна|рэгіён|ሃገር|øki|nuna|igihugu|akarere|atunuu|itulagi|fonua|dal|gobol|هېواد|سیمه|ޤައުމު|ސަރަހައްދު|pajji|reġjun|firenena|faritra|tír|réigiún|gwlad|rhanbarth|whenua|rohe|lân|regioun|pajais|regiun|welat|herêm|ilizwe|ummandla|naha|sebaka|naga|kgaolo"""
helper = "const COUNTRY_TERMS=" + repr(terms) + ".split('|').map(normalizeText).filter(Boolean);\nfunction hasCountryTerm(text){const s=normalizeText(text),pad=' '+s+' ';return COUNTRY_TERMS.some(t=>/^[a-z0-9\\- ]+$/i.test(t)?pad.includes(' '+t+' '):s.includes(t))}\n"
s = s.replace(anchor, helper + anchor, 1)
old = "    || /(?:ملک|ملک کو|ملک بدل).{0,30}(?:بدل|منتخب|چن)/u.test(String(text||''));"
new = "    || /(?:ملک|ملک کو|ملک بدل).{0,30}(?:بدل|منتخب|چن)/u.test(String(text||''))\n    || hasCountryTerm(text);"
if old not in s:
    raise SystemExit('country command tail missing')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

print('R12 patch applied')
