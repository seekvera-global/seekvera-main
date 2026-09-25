from pathlib import Path

p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8')
marker='seekvera-r52-ai-quota-fallback'
if marker not in s:
    anchor='async function smartAI(req,env,b){'
    if anchor not in s:
        raise SystemExit('R52 smartAI anchor missing')
    helpers=r'''const R52_AI_FALLBACK='seekvera-r52-ai-quota-fallback';
const STATIC_AI_SOURCE='I’m the SEEKVERA AI assistant. Tell me what you need and I’ll help you find the right section, compare options or search worldwide.';
function inputLangCode(v){let x=String(v||'en').trim().toLowerCase().replace('_','-').split('-')[0];return /^[a-z]{2,3}$/.test(x)?x:'en'}
async function publicAIFallback(language,market,message,cat){try{const prompt=`You are SEEKVERA AI inside a worldwide marketplace app. Reply ONLY in ${language}. Market: ${market}. User message: ${message}. Category: ${cat}. Be natural, practical and concise, under 120 words. Help the user find the right section or next step. Never invent live prices, inventory, availability, booking, job or company replies. Never request passwords, OTP, PIN or CVV. Return only the answer.`,signal=(typeof AbortSignal!=='undefined'&&AbortSignal.timeout)?AbortSignal.timeout(7500):undefined,r=await fetch('https://text.pollinations.ai/'+encodeURIComponent(prompt)+'?model=openai&private=true',{headers:{accept:'text/plain','user-agent':'SEEKVERA-R52/1.0'},...(signal?{signal}:{})});if(r.ok){const text=clean(await r.text(),1800);if(text&&text.length>1)return{text,model:'pollinations-private-zero-cost'}}}catch{}return null}
async function staticPackAIFallback(req,env,b,language,cat){const code=inputLangCode(b?.language);try{if(env?.ASSETS){const u=new URL('/i18n-r32/'+encodeURIComponent(code)+'.json',req.url),r=await env.ASSETS.fetch(new Request(u.toString(),{method:'GET'}));if(r.ok){const d=await r.json(),text=clean(d?.translations?.[STATIC_AI_SOURCE],1800);if(text&&text!==STATIC_AI_SOURCE)return{text,model:'seekvera-static-'+code+'-fallback'}}}}catch{}return{text:fallbackGuide(language,cat),model:'seekvera-local-guide-fallback'}}
'''
    s=s.replace(anchor,helpers+anchor,1)

old="const got=await staggeredAI(env,messages);if(!got)return null;const response=got.text,model=got.model;return json(req,{ok:true,response,model,language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath:'r32-staggered-fast'})"
new="const got=await staggeredAI(env,messages);let response,model,fastPath;if(got){response=got.text;model=got.model;fastPath='r32-staggered-fast'}else{const pub=await publicAIFallback(language,market,m,cat),fb=pub||await staticPackAIFallback(req,env,b,language,cat);response=fb.text;model=fb.model;fastPath=pub?'r52-public-zero-cost-fallback':'r52-static-localized-fallback'}return json(req,{ok:true,response,model,language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath})"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('R52 patched smartAI anchor missing')

# Surface the fallback mode in health without exposing secrets.
health="r31Runtime:'atomic-locale-localized-currency-fast-voice-smart-ai-r31c'"
health_new="r31Runtime:'atomic-locale-localized-currency-fast-voice-smart-ai-r31c',aiQuotaFallback:R52_AI_FALLBACK"
if health in s:
    s=s.replace(health,health_new,1)
elif health_new not in s:
    raise SystemExit('R52 health anchor missing')

p.write_text(s,encoding='utf-8')
print('R52 AI quota fallback patched: Workers AI -> private zero-cost backup -> static localized pack')
