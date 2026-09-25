from pathlib import Path
import re

p=Path('r31-ui-polish.js')
s=p.read_text(encoding='utf-8')

# Add persistent conversational intent + language-independent helpers after arabicText/similarReply.
anchor="function similarReply(a,b){const n=x=>String(x||'').toLowerCase().replace(/[^\\p{L}\\p{N}]+/gu,' ').trim();const x=n(a),y=n(b);return !!x&&!!y&&(x===y||(x.length>48&&y.includes(x.slice(0,48)))||(y.length>48&&x.includes(y.slice(0,48))))}"
insert=anchor+"\nfunction lastIntent(){try{return sessionStorage.getItem('seekvera_ai_intent')||''}catch{return''}}\nfunction setIntent(cat){if(!cat||cat==='general')return;try{sessionStorage.setItem('seekvera_ai_intent',cat)}catch{}}\nfunction explicitTravelAction(q){return /book|booking|reserve|reservation|room|stay|night|flight|ticket|trip|travel|حجز|غرفة|ليلة|طيران|تذكرة|رحلة|سفر|réserv|vol|voyage|hotel booking|reservar|vuelo|viaje|reservar|voo|viagem|buchen|flug|reise|rezerv|uçuş|seyahat|брон|рейс|путешеств|预订|航班|旅行|予約|フライト|旅行|예약|항공|여행/iu.test(String(q||''))}\nfunction contextualIntent(q,h=[]){const now=intent(q),prev=lastIntent();if(!prev||prev==='general')return now;const compact=String(q||'').trim().length<=120||String(q||'').trim().split(/\\s+/).length<=12;if(now==='general'&&compact)return prev;if(prev==='jobs'&&now==='travel'&&compact&&!explicitTravelAction(q))return'jobs';return now}\nfunction isKnowledgeQuestion(q){const t=String(q||'').trim();if(/[?؟]$/.test(t))return true;return /^(what|why|how|who|when|where|explain|tell me about|define|compare|ما هو|ما هي|ماذا|لماذا|ليش|كيف|مين|من هو|وين|أين|اشرح|شو يعني|qu['’]?est|pourquoi|comment|qui|où|que es|por qué|como|cómo|quién|dónde|o que|por que|como|was ist|warum|wie|wer|wo|что|почему|как|кто|где|什么是|为什么|怎么|如何|誰|何|なぜ|どう|무엇|왜|어떻게)/iu.test(t)}\nfunction shouldAutoRoute(q,cat){if(!cat||cat==='general')return false;if(isKnowledgeQuestion(q))return false;return String(q||'').trim().length<=180}\nfunction routeUrl(cat,q){const route=ROUTES[cat]||ROUTES.general;return route+'?q='+encodeURIComponent(q)+'&country='+encodeURIComponent(country())}\nfunction controlResult(q){try{const c=window.SEEKVERA_R24_CONTROLLER?.detectControls?.(q)||{};if(c.country||c.language){window.SEEKVERA_R24_CONTROLLER?.applyControls?.(c);return c}}catch{}return null}\nfunction controlReply(c,q){const ar=arabicText(q);if(c?.country&&c?.language)return ar?'تم تغيير الدولة واللغة مباشرة.':'Country and language changed.';if(c?.country)return ar?'تم تغيير الدولة مباشرة.':'Country changed.';if(c?.language)return ar?'تم تغيير اللغة مباشرة.':'Language changed.';return''}\nfunction pendingVoiceOnNextPage(text,language){try{sessionStorage.setItem('seekvera_route_voice',JSON.stringify({text:String(text||''),language:String(language||'auto'),at:Date.now()}))}catch{}}\nfunction autoRoute(cat,q,reply,language,voiceOrigin){if(!shouldAutoRoute(q,cat))return false;setIntent(cat);if(voiceOrigin)pendingVoiceOnNextPage(reply,language);setTimeout(()=>{location.assign(routeUrl(cat,q))},120);return true}\nfunction replayPendingRouteVoice(){let raw='';try{raw=sessionStorage.getItem('seekvera_route_voice')||'';sessionStorage.removeItem('seekvera_route_voice')}catch{}if(!raw)return;try{const x=JSON.parse(raw);if(!x?.text||Date.now()-(x.at||0)>30000)return;setTimeout(()=>{try{window.SEEKVERA_VOICE_AI?.markVoiceReply?.()}catch{}window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:x.text,language:x.language||'auto'}}))},650)}catch{}}"
if 'function contextualIntent(' not in s:
    if anchor not in s: raise SystemExit('R56 helper anchor missing')
    s=s.replace(anchor,insert,1)

# Replace submitAI with context-aware controls, one voice engine, and automatic routing.
start=s.find("async function submitAI(q,{fromVoice=false}={}){")
end=s.find("\nfunction startFastVoice",start)
if start<0 or end<0: raise SystemExit('R56 submitAI boundaries missing')
new_submit="""async function submitAI(q,{fromVoice=false}={}){
 q=String(q||'').trim().slice(0,1800);if(!q||submitting)return;submitting=true;const voiceOrigin=!!fromVoice||!!window.SEEKVERA_VOICE_AI?.isVoiceReplyPending?.();if(voiceOrigin)try{window.SEEKVERA_VOICE_AI?.markVoiceReply?.()}catch{}const input=document.querySelector('#aiChatInput');if(input)input.value='';appendMsg('user',q);const ctl=controlResult(q);if(ctl){const reply=controlReply(ctl,q);appendMsg('bot',reply);window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:reply,language:ctl.language||lang()}}));submitting=false;return}const pending=appendMsg('bot',thinkingText(),'thinking');const h=history(),guessed=contextualIntent(q,h);setIntent(guessed);showRoute({category:guessed,route:ROUTES[guessed]||ROUTES.general},q);
 try{const d=await fetchAI({message:q,country:countryName(),countryCode:country(),language:'auto',uiLanguage:lang(),scope:country()==='WW'?'worldwide':'country',fast:true,history:h,conversationIntent:guessed});try{const srv={country:d?.countryAction?.code||'',language:d?.languageAction?.code||''};if(srv.country||srv.language)window.SEEKVERA_R24_CONTROLLER?.applyControls?.(srv)}catch{}let finalCat=d?.category||guessed;if(guessed==='jobs'&&finalCat==='travel'&&!explicitTravelAction(q))finalCat='jobs';setIntent(finalCat);let reply=String(d.response||'').trim();const previous=[...h].reverse().find(x=>x.role==='assistant')?.content||'';if(similarReply(reply,previous)){reply=arabicText(q)?'تمام. فهمت متابعتك وسأكمل من نفس الطلب بدون تكرار الكلام.':'Got it. I’ll continue from the same request without repeating the previous answer.'}if(pending){pending.textContent=reply;pending.classList.remove('thinking')}const ans=document.querySelector('#aiAnswer');if(ans)ans.textContent=reply;showRoute({category:finalCat,route:ROUTES[finalCat]||d?.route},q);window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:reply,language:d.language||'auto',category:finalCat,route:ROUTES[finalCat]||d?.route}}));if(autoRoute(finalCat,q,reply,d.language||'auto',voiceOrigin))return
 }catch(e){const reply=failText();if(pending){pending.textContent=reply;pending.classList.remove('thinking')}window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:reply,language:'auto'}}));if(guessed!=='general'&&shouldAutoRoute(q,guessed)){setIntent(guessed);setTimeout(()=>location.assign(routeUrl(guessed,q)),180)}}finally{submitting=false}
}"""
s=s[:start]+new_submit+s[end:]

# Make R31 delegate microphone clicks to the central voice-ai engine instead of intercepting with its own TTS/STT path.
old="document.addEventListener('click',e=>{const mic=e.target.closest?.('#aiChatMic');if(!mic)return;if(SpeechRecognition){e.preventDefault();e.stopImmediatePropagation();startFastVoice(mic)}},true);"
new="document.addEventListener('click',e=>{const mic=e.target.closest?.('#aiChatMic');if(!mic)return;if(window.SEEKVERA_VOICE_AI?.start){e.preventDefault();e.stopImmediatePropagation();const input=mic.closest('form')?.querySelector('#aiChatInput,input[type=\\\"text\\\"],input:not([type])');window.SEEKVERA_VOICE_AI.start(input?.id||'aiChatInput',mic)}},true);"
if old in s:s=s.replace(old,new,1)
elif new not in s: raise SystemExit('R56 bindChat mic anchor missing')

# Replay a voice reply after automatic category navigation completes.
oldboot="function boot(){installAtomicCSS();repairCategoryIcons();localizeCurrencies();bindLocale();bindChat();atomicLocale();document.documentElement.dataset.r31=VERSION}"
newboot="function boot(){installAtomicCSS();repairCategoryIcons();localizeCurrencies();bindLocale();bindChat();atomicLocale();replayPendingRouteVoice();document.documentElement.dataset.r31='20260926-r56-global-ai-core'}"
if oldboot in s:s=s.replace(oldboot,newboot,1)
elif "replayPendingRouteVoice();document.documentElement.dataset.r31='20260926-r56-global-ai-core'" not in s: raise SystemExit('R56 boot anchor missing')
p.write_text(s,encoding='utf-8')
print('R56 r31 global AI core patched')

# Strengthen central voice engine: direct public method and longer pending window for mobile async/navigation.
p=Path('voice-ai.js');v=p.read_text(encoding='utf-8')
v=v.replace('voiceReplyDeadline=Date.now()+45000','voiceReplyDeadline=Date.now()+90000')
v=v.replace("markVoiceReply:()=>{voiceConversation=true;voiceReplyDeadline=Date.now()+45000;muted=false;", "markVoiceReply:()=>{voiceConversation=true;voiceReplyDeadline=Date.now()+90000;muted=false;")
# If the exact second replacement was already covered globally, that's fine.
p.write_text(v,encoding='utf-8')
print('R56 voice central engine patched')

# Bump service-worker cache and ensure latest central scripts are fetched network-first.
p=Path('sw.js');sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const CACHE='[^']+';","const CACHE='seekvera-r56-global-ai-core-20260926';",sw,1)
p.write_text(sw,encoding='utf-8')
print('R56 service worker cache bumped')

# Update dynamic HTML injection version for R31 so custom-domain pages do not reuse R55/R31 cache.
p=Path('worker-r31.js');w=p.read_text(encoding='utf-8')
w=re.sub(r"r31-ui-polish\\.js\\?v=[A-Za-z0-9._-]+","r31-ui-polish.js?v=20260926-r56-global-ai-core",w)
# Also replace literal URL version where not regex escaped.
w=re.sub(r"r31-ui-polish\.js\?v=[A-Za-z0-9._-]+","r31-ui-polish.js?v=20260926-r56-global-ai-core",w)
p.write_text(w,encoding='utf-8')
print('R56 worker injection version bumped')
