from pathlib import Path
p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8')
old="const got=await staggeredAI(env,messages);const response=got?.text||await localizedFallback(env,language,cat),model=got?.model||'seekvera-r32-localized-fallback';return json(req,{ok:true,response,model,language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath:got?'r31-staggered-fast':'r31-latency-fallback'})"
new="const got=await staggeredAI(env,messages);if(!got)return null;const response=got.text,model=got.model;return json(req,{ok:true,response,model,language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath:'r32-staggered-fast'})"
if old not in s:
    raise SystemExit('R32 smartAI failover anchor not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('R32 AI failover patched: smart route falls through to resilient base AI when fast models are unavailable')
