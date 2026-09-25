from pathlib import Path

p=Path('r31-ui-polish.js')
s=p.read_text(encoding='utf-8')

# Add deterministic client intent routing to the real capture-phase chat controller.
anchor="function countryName(){const e=document.querySelector('#country');return e?.options?.[e.selectedIndex]?.textContent||'Worldwide'}"
helper=anchor+"\nfunction intent(q){const t=String(q||'').toLowerCase();const tests=[['jobs',/job|jobs|career|vacancy|work|employment|hiring|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام/u],['travel',/travel|flight|hotel|tourism|airport|visa|سفر|طيران|فندق|سياح/u],['property',/property|house|apartment|land|rent|real estate|عقار|بيت|ارض|أرض|ايجار|إيجار/u],['cars',/car|vehicle|auto|spare part|سيارة|مركبة|قطع غيار/u],['business',/supplier|manufacturer|factory|wholesale|import|export|rfq|quotation|مورد|مصنع|استيراد|تصدير|عرض سعر/u],['health',/hospital|clinic|doctor|pharmacy|health|مستشفى|عيادة|طبيب|صيدلية/u],['restaurants',/restaurant|food|cafe|coffee|مطعم|اكل|أكل|قهوة/u],['connectivity',/wifi|wi-?fi|internet|esim|sim card|mobile data|واي فاي|انترنت|إنترنت|شريحة/u],['shopping',/buy|shopping|product|shop|price|شراء|تسوق|منتج|سعر/u],['media',/news|movie|music|radio|tv|أخبار|فيلم|موسيقى/u]];for(const[c,re]of tests)if(re.test(t))return c;return'general'}\nfunction arabicText(q=''){return /[\\u0600-\\u06ff]/u.test(String(q||''))||lang()==='ar'}\nfunction similarReply(a,b){const n=x=>String(x||'').toLowerCase().replace(/[^\\p{L}\\p{N}]+/gu,' ').trim();const x=n(a),y=n(b);return !!x&&!!y&&(x===y||(x.length>48&&y.includes(x.slice(0,48)))||(y.length>48&&x.includes(y.slice(0,48))))}"
if 'function intent(q)' not in s:
    if anchor not in s: raise SystemExit('R31 countryName anchor missing')
    s=s.replace(anchor,helper,1)

# Make route CTA category-specific and usable immediately, including colloquial Arabic.
old="function showRoute(d,q){const box=document.querySelector('#aiActions');if(!box)return;box.innerHTML='';const route=d?.route||ROUTES[d?.category]||'';if(!route)return;const a=document.createElement('a');a.href=route+'?q='+encodeURIComponent(q);a.textContent=lang()==='ar'?'افتح القسم المناسب ←':'Open the right section →';box.appendChild(a)}"
new="function showRoute(d,q){const box=document.querySelector('#aiActions');if(!box)return;box.innerHTML='';const cat=d?.category||intent(q),route=d?.route||ROUTES[cat]||ROUTES.general;if(!route)return;const ar=arabicText(q),labels={jobs:ar?'افتح الوظائف الآن ←':'Open Jobs now →',travel:ar?'افتح السفر والفنادق الآن ←':'Open Travel & Hotels now →',property:ar?'افتح العقارات الآن ←':'Open Property now →',cars:ar?'افتح السيارات الآن ←':'Open Cars now →',business:ar?'افتح الشركات والموردين الآن ←':'Open Business & Suppliers now →',health:ar?'افتح الصحة الآن ←':'Open Health now →',restaurants:ar?'افتح المطاعم الآن ←':'Open Restaurants now →',connectivity:ar?'افتح الإنترنت والاتصال الآن ←':'Open Connectivity now →',shopping:ar?'افتح التسوق الآن ←':'Open Shopping now →'};const a=document.createElement('a');a.href=route+'?q='+encodeURIComponent(q)+'&country='+encodeURIComponent(country());a.textContent=labels[cat]||(ar?'افتح القسم المناسب الآن ←':'Open the right section now →');a.dataset.svDirectRoute=cat;box.appendChild(a)}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R31 showRoute anchor missing')

# Reduce the real controller timeout. The server already owns its own resilient fallbacks.
s=s.replace("setTimeout(()=>c.abort(),6500)","setTimeout(()=>c.abort(),4200)",1)

old="async function submitAI(q,{fromVoice=false}={}){\n q=String(q||'').trim().slice(0,1800);if(!q||submitting)return;submitting=true;voiceTurn=!!fromVoice;const input=document.querySelector('#aiChatInput');if(input)input.value='';appendMsg('user',q);const pending=appendMsg('bot',thinkingText(),'thinking');const h=history();\n try{const d=await fetchAI({message:q,country:countryName(),countryCode:country(),language:lang(),scope:country()==='WW'?'worldwide':'country',fast:true,history:h});if(pending){pending.textContent=d.response;pending.classList.remove('thinking')}const ans=document.querySelector('#aiAnswer');if(ans)ans.textContent=d.response;showRoute(d,q);window.dispatchEvent(new CustomEvent('seekvera:ai-response-r31',{detail:{text:d.response,language:d.language||lang()}}));if(fromVoice)speak(d.response)}catch(e){if(pending){pending.textContent=failText();pending.classList.remove('thinking')}voiceTurn=false}finally{submitting=false}\n}"
new="async function submitAI(q,{fromVoice=false}={}){\n q=String(q||'').trim().slice(0,1800);if(!q||submitting)return;submitting=true;const voiceOrigin=!!fromVoice||!!window.SEEKVERA_VOICE_AI?.isVoiceReplyPending?.();voiceTurn=voiceOrigin;if(voiceOrigin)try{window.SEEKVERA_VOICE_AI?.markVoiceReply?.()}catch{}const input=document.querySelector('#aiChatInput');if(input)input.value='';appendMsg('user',q);const pending=appendMsg('bot',thinkingText(),'thinking');const h=history(),guessed=intent(q);showRoute({category:guessed,route:ROUTES[guessed]||ROUTES.general},q);\n try{const d=await fetchAI({message:q,country:countryName(),countryCode:country(),language:'auto',uiLanguage:lang(),scope:country()==='WW'?'worldwide':'country',fast:true,history:h});let reply=String(d.response||'').trim();const previous=[...h].reverse().find(x=>x.role==='assistant')?.content||'';if(similarReply(reply,previous)){reply=guessed==='jobs'?(arabicText(q)?'أكيد. فتحت لك طريق الوظائف مباشرة تحت الرد. قل لي البلد أو المدينة ونوع الشغل، وبكمّل معك على النتائج بدل ما أعيد نفس الكلام.':'Absolutely. The Jobs link is directly below. Tell me the country/city and job type and I’ll move to the results instead of repeating myself.'):(arabicText(q)?'تمام، خلينا نكمل للخطوة التالية. استخدم زر القسم المباشر تحت الرد وأعطني فقط التفصيل الناقص.':'Let’s move to the next step. Use the direct section button below and give me only the missing detail.')}if(pending){pending.textContent=reply;pending.classList.remove('thinking')}const ans=document.querySelector('#aiAnswer');if(ans)ans.textContent=reply;showRoute({...d,category:d.category||guessed,route:d.route||ROUTES[d.category||guessed]},q);const detail={text:reply,language:d.language||'auto',route:d.route||ROUTES[d.category||guessed],category:d.category||guessed};window.dispatchEvent(new CustomEvent('seekvera:ai-response-r31',{detail}));window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail}))}catch(e){const msg=guessed==='jobs'?(arabicText(q)?'أنا معك. زر الوظائف موجود مباشرة تحت الرد؛ قل لي البلد أو المدينة ونوع الشغل لأضيّق لك النتائج.':'I’m with you. The Jobs button is directly below; tell me the country/city and job type and I’ll narrow the results.'):failText();if(pending){pending.textContent=msg;pending.classList.remove('thinking')}showRoute({category:guessed,route:ROUTES[guessed]||ROUTES.general},q);window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:msg,language:'auto',route:ROUTES[guessed]||ROUTES.general,category:guessed}}));voiceTurn=false}finally{submitting=false}\n}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R31 submitAI anchor missing')

p.write_text(s,encoding='utf-8')
print('R55 real R31 chat/voice controller patched')

# Make the injected R31 controller URL fresh on every production page.
p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8')
s=s.replace('r31-ui-polish.js?v=20260925-r31b','r31-ui-polish.js?v=20260925-r55-chat-voice',1)
p.write_text(s,encoding='utf-8')

# Force network-first for the actual chat controller and rotate the SW cache.
p=Path('sw.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const CACHE='seekvera-r35-global-final-20260925';","const CACHE='seekvera-r55-chat-voice-20260925';",1)
s=s.replace('(?:r24-ai-controller|i18n-ui|voice-ai|global-ui|superapp|navigation|locale-r15|locale-r14|locale-r14-categories|r20-final-guard|r20-extra-categories|r22-category-lock)', '(?:r31-ui-polish|r24-ai-controller|i18n-ui|voice-ai|global-ui|superapp|navigation|locale-r15|locale-r14|locale-r14-categories|r20-final-guard|r20-extra-categories|r22-category-lock)',1)
p.write_text(s,encoding='utf-8')
print('R55 worker injection + service worker cache patched')
