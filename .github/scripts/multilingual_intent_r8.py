from pathlib import Path

p=Path('worker.js')
s=p.read_text(encoding='utf-8')

anchor="const route=c=>({connectivity:'connectivity.html',travel:'travel.html',property:'property.html',cars:'cars-auto.html',jobs:'jobs.html',business:'import-export.html',health:'health.html',restaurants:'restaurants-food.html',shopping:'shopping.html',media:'media.html',general:'marketplace.html'})[c]||'marketplace.html';"
helper="""const INTENT_ALLOWED=new Set(['connectivity','travel','property','cars','jobs','business','health','restaurants','shopping','media','general']);
async function classifyIntent(env,text){
 const quick=category(text);if(quick!=='general'||!env.AI)return quick;
 const prompt='Classify the user request written in ANY language into exactly ONE SEEKVERA category token. Allowed tokens only: connectivity, travel, property, cars, jobs, business, health, restaurants, shopping, media, general. Meanings: connectivity=internet Wi-Fi SIM eSIM telecom; travel=hotels flights tourism airport visa trips; property=homes apartments land rent real estate; cars=vehicles auto parts; jobs=employment careers vacancies hiring work; business=suppliers manufacturers import export procurement; health=hospitals clinics doctors pharmacies; restaurants=food restaurants cafes; shopping=products buying retail; media=news movies music TV radio; general=only when none fits. Consider the whole conversation context. Return ONLY the single lowercase token, no punctuation or explanation.';
 try{const r=await env.AI.run(FASTCHAT,{messages:[{role:'system',content:prompt},{role:'user',content:clean(text,5000)}],temperature:0,max_tokens:16});const raw=out(r).toLowerCase().trim();const m=raw.match(/^(connectivity|travel|property|cars|jobs|business|health|restaurants|shopping|media|general)$/);return m&&INTENT_ALLOWED.has(m[1])?m[1]:quick}catch(e){console.warn('Multilingual intent classifier fallback',e);return quick}
}
"""
if 'async function classifyIntent(' not in s:
    if anchor not in s:
        raise SystemExit('route anchor not found')
    s=s.replace(anchor,anchor+'\n'+helper,1)

old='const detected=await detectedLanguage(env,m,b.language),c=category(contextText),p='
new='const detected=await detectedLanguage(env,m,b.language),c=await classifyIntent(env,contextText),p='
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('AI category call anchor not found')

p.write_text(s,encoding='utf-8')
print('Worldwide multilingual intent routing patch applied.')
