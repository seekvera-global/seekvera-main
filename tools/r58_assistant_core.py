from pathlib import Path
import re

VER='20260926-r58-global-assistant'

# -----------------------------------------------------------------------------
# 1) Client router: all SEEKVERA departments + translated category recognition.
# -----------------------------------------------------------------------------
p=Path('r31-ui-polish.js')
s=p.read_text(encoding='utf-8')

old="const ROUTES={travel:'travel.html',property:'property.html',cars:'cars-auto.html',jobs:'jobs.html',shopping:'shopping.html',business:'import-export.html',health:'health.html',restaurants:'restaurants-food.html',connectivity:'connectivity.html',media:'media.html',general:'marketplace.html'};"
new="const ROUTES={general:'marketplace.html',travel:'travel.html',tourism:'tourism.html',property:'property.html',cars:'cars-auto.html',jobs:'jobs.html',shopping:'shopping.html',restaurants:'restaurants-food.html',services:'local-services.html',equipment:'marketplace.html?q=equipment',boats:'marketplace.html?q=boats',business:'import-export.html',shipping:'shipping-logistics.html',businessSoftware:'business-software.html',software:'software.html',hosting:'web-hosting.html',solar:'solar.html',education:'education.html',health:'health.html',money:'money-insurance.html',entertainment:'entertainment.html',media:'media.html',games:'games.html',connectivity:'connectivity.html',wifi:'wifi.html',dealAgent:'deal-agent.html',everyday:'everyday.html',scan:'scan.html',promote:'seller-plans.html'};"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('R58 ROUTES anchor missing')

pat=re.compile(r"function intent\(q\)\{.*?return'general'\}",re.S)
replacement=r'''const DEPT_KEYS=['general','travel','travel','travel','tourism','property','cars','jobs','shopping','restaurants','services','equipment','boats','business','shipping','businessSoftware','software','hosting','solar','education','health','money','entertainment','media','games','connectivity','wifi','dealAgent','everyday','scan','promote'];
const INTENT_STOP=new Set(['and','the','with','for','from','this','that','your','you','all','new','best','open','search','find','near','world','global','about','into','plus','free','local','business','service','services','marketplace','market','online','worldwide','من','الى','إلى','على','في','عن','مع','كل','هذا','هذه','الآن','الان','عبر','حول']);
function normIntentText(v){return String(v||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[ًٌٍَُِّْـ]/g,'').replace(/[^\p{L}\p{N}]+/gu,' ').trim()}
function translatedIntent(q){const nq=normIntentText(q);if(!nq)return'general';const data=window.SEEKVERA_R14_CATEGORIES?.data||{};let best='general',bestScore=0;for(const arr of Object.values(data)){if(!Array.isArray(arr))continue;for(let i=0;i<Math.min(arr.length,DEPT_KEYS.length);i++){const key=DEPT_KEYS[i];if(!key||key==='general')continue;const title=normIntentText(arr[i]);if(!title)continue;if(nq.includes(title)&&title.length>bestScore){best=key;bestScore=title.length+100;continue}const toks=title.split(/\s+/).map(x=>x.replace(/^و/u,'')).filter(x=>x.length>=4&&!INTENT_STOP.has(x));for(const tok of toks){if(nq.includes(tok)&&tok.length>bestScore){best=key;bestScore=tok.length}}}}return best}
function intent(q){const t=String(q||'').toLowerCase();const tests=[
['jobs',/job|jobs|career|vacancy|work|employment|hiring|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام/u],
['solar',/solar|inverter|photovoltaic|pv panel|solar panel|renewable energy|طاقة شمسية|الطاقة الشمسية|شمسي|شمسية|انفرتر|إنفرتر|الواح شمسية|ألواح شمسية/u],
['education',/education|school|university|course|training|college|تعليم|مدرسة|جامعة|دورة|تدريب/u],
['money',/insurance|bank|loan|finance|money|تأمين|بنك|قرض|تمويل/u],
['shipping',/shipping|logistics|freight|cargo|delivery|شحن|لوجست|نقل بضائع|توصيل/u],
['services',/local service|repair|plumber|electrician|cleaning|خدمات محلية|صيانة|سباك|كهربائي|تنظيف/u],
['equipment',/equipment|machinery|machine|generator|معدات|ماكينات|آلات|مولد/u],
['boats',/boat|marine|yacht|ship for sale|قارب|قوارب|يخت|بحري/u],
['software',/software|app development|application development|برمجيات|تطبيقات|برنامج/u],
['hosting',/hosting|domain|website|web site|استضافة|دومين|موقع إلكتروني|موقع الكتروني/u],
['games',/game|games|gaming|لعبة|العاب|ألعاب/u],
['tourism',/tourism|tourist|attraction|sightseeing|سياحة|سياحي|معالم/u],
['dealAgent',/deal agent|source offers|request offers|procurement agent|وكيل الصفقات|جيب عروض|اجلب عروض/u],
['travel',/travel|flight|hotel|tourism|airport|visa|سفر|طيران|فندق|سياح/u],
['property',/property|house|apartment|land|rent|real estate|عقار|بيت|ارض|أرض|ايجار|إيجار/u],
['cars',/car|vehicle|auto|spare part|سيارة|مركبة|قطع غيار/u],
['business',/supplier|manufacturer|factory|wholesale|import|export|rfq|quotation|مورد|مصنع|استيراد|تصدير|عرض سعر/u],
['health',/hospital|clinic|doctor|pharmacy|health|مستشفى|عيادة|طبيب|صيدلية|صحة/u],
['restaurants',/restaurant|food|cafe|coffee|مطعم|اكل|أكل|قهوة/u],
['connectivity',/wifi|wi-?fi|internet|esim|sim card|mobile data|واي فاي|انترنت|إنترنت|شريحة/u],
['shopping',/buy|shopping|product|shop|price|cheapest|شراء|تسوق|منتج|سعر|ارخص|أرخص/u],
['entertainment',/entertainment|cinema|concert|ترفيه|سينما|حفلة/u],
['media',/news|movie|music|radio|tv|أخبار|فيلم|موسيقى/u]
];for(const[c,re]of tests)if(re.test(t))return c;return translatedIntent(q)}'''
if pat.search(s):
    s=pat.sub(replacement,s,count=1)
elif 'function translatedIntent(q)' not in s:
    raise SystemExit('R58 intent function not found')

# Route URLs can already contain their own query string.
old="function routeUrl(cat,q){const route=ROUTES[cat]||ROUTES.general;return route+'?q='+encodeURIComponent(q)+'&country='+encodeURIComponent(country())}"
new="function routeUrl(cat,q){const route=ROUTES[cat]||ROUTES.general,sep=route.includes('?')?'&':'?';return route+sep+'q='+encodeURIComponent(q)+'&country='+encodeURIComponent(country())}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R58 routeUrl anchor missing')

# Hide manual route buttons when the request is clear enough to auto-route.
old="function showRoute(d,q){const box=document.querySelector('#aiActions');if(!box)return;box.innerHTML='';const cat=d?.category||intent(q),route=d?.route||ROUTES[cat]||ROUTES.general;if(!route)return;"
new="function showRoute(d,q){const box=document.querySelector('#aiActions');if(!box)return;box.innerHTML='';const cat=d?.category||intent(q),route=d?.route||ROUTES[cat]||ROUTES.general;if(!route)return;if(cat!=='general'&&shouldAutoRoute(q,cat))return;"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R58 showRoute anchor missing')

# Prefer the deterministic translated router over a weak backend generic classification.
old="let finalCat=d?.category||guessed;if(guessed==='jobs'&&finalCat==='travel'&&!explicitTravelAction(q))finalCat='jobs';"
new="let finalCat=(guessed&&guessed!=='general')?guessed:(d?.category||guessed);if(guessed==='jobs'&&finalCat==='travel'&&!explicitTravelAction(q))finalCat='jobs';"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R58 finalCat anchor missing')

# Remove the exact repetitive generic replacement seen by the user. If the model repeats,
# keep one concise acknowledgement and immediately continue to the routed result.
old="if(similarReply(reply,previous)){reply=arabicText(q)?'تمام. فهمت متابعتك وسأكمل من نفس الطلب بدون تكرار الكلام.':'Got it. I’ll continue from the same request without repeating the previous answer.'}"
new="if(similarReply(reply,previous)){const title=(()=>{const data=window.SEEKVERA_R14_CATEGORIES?.data?.[lang()];const i=DEPT_KEYS.indexOf(finalCat);return Array.isArray(data)&&i>=0?String(data[i]||'').trim():''})();reply=title?(arabicText(q)?('تمام — '+title+'. عم أكمل طلبك مباشرة هناك.'):(title+'. I’m continuing your request there now.')):(arabicText(q)?'تمام، عم أكمل طلبك مباشرة من دون إعادة نفس الكلام.':'Got it. I’m continuing your request directly without repeating myself.')}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R58 similar reply anchor missing')

# For voice-originated requests, allow audible TTS to begin before navigation instead of
# killing speech 120 ms later. Non-voice remains immediate.
old="function autoRoute(cat,q,reply,language,voiceOrigin){if(!shouldAutoRoute(q,cat))return false;setIntent(cat);if(voiceOrigin)pendingVoiceOnNextPage(reply,language);setTimeout(()=>{location.assign(routeUrl(cat,q))},120);return true}"
new="function autoRoute(cat,q,reply,language,voiceOrigin){if(!shouldAutoRoute(q,cat))return false;setIntent(cat);const go=()=>location.assign(routeUrl(cat,q));if(!voiceOrigin){setTimeout(go,100);return true}let moved=false;const once=()=>{if(moved)return;moved=true;setTimeout(go,1350)};window.addEventListener('seekvera:tts-start',once,{once:true});setTimeout(()=>{if(!moved){moved=true;go()}},2600);return true}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R58 autoRoute anchor missing')

s=s.replace("document.documentElement.dataset.r31='20260926-r56-global-ai-core'",f"document.documentElement.dataset.r31='{VER}'",1)
s=s.replace("window.SEEKVERA_R31={version:VERSION,refresh:atomicLocale,currencyLabel,repairCategoryIcons,cancelVoice:cancelRecognition,submitAI,startFastVoice,hasFastVoice:!!SpeechRecognition};","window.SEEKVERA_R31={version:VERSION,refresh:atomicLocale,currencyLabel,repairCategoryIcons,cancelVoice:cancelRecognition,submitAI,startFastVoice,intent,translatedIntent,routeUrl,hasFastVoice:!!SpeechRecognition};",1)
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) Worker router: honor the client intent for all departments and never fall back
#    to the old 'press a button' guidance.
# -----------------------------------------------------------------------------
p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8')
old="const ROUTE={travel:'travel.html',property:'property.html',cars:'cars-auto.html',jobs:'jobs.html',shopping:'shopping.html',business:'import-export.html',health:'health.html',restaurants:'restaurants-food.html',connectivity:'connectivity.html',media:'media.html',general:'marketplace.html'};"
new="const ROUTE={general:'marketplace.html',travel:'travel.html',tourism:'tourism.html',property:'property.html',cars:'cars-auto.html',jobs:'jobs.html',shopping:'shopping.html',restaurants:'restaurants-food.html',services:'local-services.html',equipment:'marketplace.html?q=equipment',boats:'marketplace.html?q=boats',business:'import-export.html',shipping:'shipping-logistics.html',businessSoftware:'business-software.html',software:'software.html',hosting:'web-hosting.html',solar:'solar.html',education:'education.html',health:'health.html',money:'money-insurance.html',entertainment:'entertainment.html',media:'media.html',games:'games.html',connectivity:'connectivity.html',wifi:'wifi.html',dealAgent:'deal-agent.html',everyday:'everyday.html',scan:'scan.html',promote:'seller-plans.html'};"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R58 worker ROUTE anchor missing')

# Extend deterministic server classification for the highest-value departments.
old="['jobs',/job|career|vacancy|work|employment|hiring|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام/u],['business'"
new="['jobs',/job|career|vacancy|work|employment|hiring|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام/u],['solar',/solar|inverter|photovoltaic|solar panel|renewable energy|طاقة شمسية|الطاقة الشمسية|شمسي|شمسية|انفرتر|إنفرتر/u],['education',/education|school|university|course|training|تعليم|مدرسة|جامعة|دورة|تدريب/u],['money',/insurance|bank|loan|finance|money|تأمين|بنك|قرض|تمويل/u],['shipping',/shipping|logistics|freight|cargo|delivery|شحن|لوجست|توصيل/u],['services',/local service|repair|plumber|electrician|cleaning|خدمات محلية|صيانة|سباك|كهربائي|تنظيف/u],['equipment',/equipment|machinery|machine|generator|معدات|ماكينات|آلات|مولد/u],['boats',/boat|marine|yacht|قارب|قوارب|يخت|بحري/u],['software',/software|app development|برمجيات|تطبيقات|برنامج/u],['hosting',/hosting|domain|website|استضافة|دومين|موقع/u],['games',/game|games|gaming|لعبة|العاب|ألعاب/u],['tourism',/tourism|tourist|attraction|sightseeing|سياحة|سياحي|معالم/u],['business'"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R58 worker category anchor missing')

# Old fallback explicitly told the user about a button. Remove that behavior everywhere.
s=s.replace("return`Done. The direct section button is right below the reply. Give me only the one missing detail and I’ll move to the next step instead of repeating the same guidance.`","return`I’m taking you directly to the best matching SEEKVERA section now. I’ll keep the same request context there so you do not need to repeat yourself.`")
s=s.replace("return`تمام. زر القسم المناسب موجود مباشرة تحت الرد. أعطني أهم تفصيل ناقص فقط حتى أنتقل للخطوة التالية بدل تكرار الكلام.`","return`تمام. عم بنقلك مباشرة للقسم الأنسب وبكمل نفس طلبك هناك، من دون ما تعيد الكلام.`")

# Bump injected asset version so mobile browsers cannot keep R57/R56 JS.
s=re.sub(r'r31-ui-polish\.js\?v=[^\"\']+',f'r31-ui-polish.js?v={VER}',s)
s=re.sub(r'voice-ai\.js\?v=[^\"\']+',f'voice-ai.js?v={VER}',s)
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Voice: Android uses system-selected voice first, emits start/end signals, and
#    retries without an explicitly selected voice if speech never starts.
# -----------------------------------------------------------------------------
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const v=pickVoice(lastLocale);if(v)u.voice=v;u.rate=1.01;u.pitch=1.05;u.volume=1;let started=false,finished=false;u.onstart=()=>{started=true};u.onend=()=>{finished=true;if(token===speakToken)play(index+1,0)};","const android=/Android/i.test(navigator.userAgent);const v=android?null:pickVoice(lastLocale);if(v)u.voice=v;u.rate=1.0;u.pitch=1.02;u.volume=1;let started=false,finished=false;u.onstart=()=>{started=true;window.dispatchEvent(new CustomEvent('seekvera:tts-start',{detail:{language:lastLocale}}))};u.onend=()=>{finished=true;if(token===speakToken)play(index+1,0)};",1)
s=s.replace("if(index>=chunks.length){if(token===speakToken)voiceConversation=false;return}","if(index>=chunks.length){if(token===speakToken){voiceConversation=false;window.dispatchEvent(new CustomEvent('seekvera:tts-end',{detail:{language:lastLocale}}))}return}",1)
# Final retry on Android/default system voice instead of silently advancing.
old="else if(token===speakToken)play(index+1,0)};speechSynthesis.resume();speechSynthesis.speak(u);"
new="else if(token===speakToken){try{speechSynthesis.cancel();speechSynthesis.resume();const z=new SpeechSynthesisUtterance(chunks[index]);z.lang=lastLocale;z.rate=1;z.pitch=1;z.volume=1;z.onstart=()=>window.dispatchEvent(new CustomEvent('seekvera:tts-start',{detail:{language:lastLocale}}));z.onend=()=>play(index+1,0);z.onerror=()=>play(index+1,0);speechSynthesis.speak(z)}catch(_){play(index+1,0)}}};speechSynthesis.resume();speechSynthesis.speak(u);"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R58 TTS retry anchor missing')
p.write_text(s,encoding='utf-8')

# Service-worker cache bump.
p=Path('sw.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const CACHE='[^']+'",f"const CACHE='{VER}'",s,count=1)
p.write_text(s,encoding='utf-8')
print('R58 global assistant core patched')
