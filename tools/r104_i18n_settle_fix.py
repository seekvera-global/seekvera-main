from pathlib import Path
import re

p=Path('i18n-ui.js')
s=p.read_text(encoding='utf-8')
VER='20260927-r104-fast-atomic-i18n'

# Fresh language packs after the translation-system repair; do not reuse old cached pack URLs forever.
s=s.replace("'/i18n-r32/'+encodeURIComponent(l)+'.json?v=20260927-r78-voice-locale-final'", "'/i18n-r32/'+encodeURIComponent(l)+'.json?v='+VERSION", 1)

# If Cloudflare AI translation is quota-blocked, stop retrying it on every missing string in this page session.
old="async function cloudTranslate(l,batch){for(let attempt=0;attempt<3;attempt++)try{const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),12000);const r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:langName(l),strings:batch}),signal:ctl.signal,cache:'no-store'});clearTimeout(to);const d=await r.json().catch(()=>null);if(r.ok&&Array.isArray(d?.translations)&&d.translations.length===batch.length){const vals=d.translations.map((v,i)=>valid(v,batch[i])?String(v).trim():'');if(vals.some(Boolean))return vals}}catch{};return null}"
new="let CLOUD_TRANSLATE_BLOCKED=false;async function cloudTranslate(l,batch){if(CLOUD_TRANSLATE_BLOCKED)return null;try{const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),5000);const r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:langName(l),strings:batch}),signal:ctl.signal,cache:'no-store'});clearTimeout(to);if(r.status===429||r.status===503){CLOUD_TRANSLATE_BLOCKED=true;return null}const d=await r.json().catch(()=>null);if(r.ok&&Array.isArray(d?.translations)&&d.translations.length===batch.length){const vals=d.translations.map((v,i)=>valid(v,batch[i])?String(v).trim():'');if(vals.some(Boolean))return vals}}catch{}return null}"
if new not in s:
    if old not in s: raise SystemExit('cloudTranslate anchor missing')
    s=s.replace(old,new,1)

old="let seq=0,timer=0,applying=false;"
new="let seq=0,timer=0,applying=false;const BG_TRANSLATING=new Set();"
if new not in s:
    if old not in s: raise SystemExit('apply state anchor missing')
    s=s.replace(old,new,1)

old_apply="""async function apply(){const my=++seq,l=lang();if(l!=='en'){await loadPack(l);if(my!==seq)return}applying=true;document.documentElement.lang=l;document.documentElement.dir=RTL.has(l)?'rtl':'ltr';capture(document);const texts=[],attrs=[],need=[];
 for(const [n,src] of entriesText()){if(!n.isConnected)continue;texts.push([n,src]);if(l!=='en'&&!get(l,src))need.push(src);setText(n,src,l)}
 for(const [el,m] of entriesAttr()){if(!el.isConnected)continue;for(const [a,src] of Object.entries(m)){attrs.push([el,a,src]);if(l!=='en'&&!get(l,src))need.push(src);setAttr(el,a,src,l)}}
 const ai=document.querySelector('#aiMessages .ai-msg.bot:first-child');if(ai&&ai.textContent?.trim()===INITIAL_AI){if(l==='en')ai.textContent=INITIAL_AI;else{const q=get(l,INITIAL_AI);ai.textContent=q||'…';if(!q)need.push(INITIAL_AI)}}
 applying=false;if(l!=='en'&&need.length)await translate(l,need);if(my!==seq)return;applying=true;for(const [n,src] of texts)if(n.isConnected)setText(n,src,l);for(const [el,a,src] of attrs)if(el.isConnected)setAttr(el,a,src,l);const ai2=document.querySelector('#aiMessages .ai-msg.bot:first-child');if(ai2){const q=l==='en'?INITIAL_AI:get(l,INITIAL_AI);if(q&&(/SEEKVERA AI assistant/.test(ai2.textContent||'')||(ai2.textContent||'').trim()==='…'))ai2.textContent=q}document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;applying=false}"""
new_apply="""async function apply(){const my=++seq,l=lang();if(l!=='en'){await loadPack(l);if(my!==seq)return}applying=true;document.documentElement.lang=l;document.documentElement.dir=RTL.has(l)?'rtl':'ltr';capture(document);const need=[];
 for(const [n,src] of entriesText()){if(!n.isConnected)continue;if(l!=='en'&&!get(l,src))need.push(src);setText(n,src,l)}
 for(const [el,m] of entriesAttr()){if(!el.isConnected)continue;for(const [a,src] of Object.entries(m)){if(l!=='en'&&!get(l,src))need.push(src);setAttr(el,a,src,l)}}
 const ai=document.querySelector('#aiMessages .ai-msg.bot:first-child');if(ai&&ai.textContent?.trim()===INITIAL_AI){if(l==='en')ai.textContent=INITIAL_AI;else{const q=get(l,INITIAL_AI);if(q)ai.textContent=q;else need.push(INITIAL_AI)}}
 document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;applying=false;
 if(l!=='en'&&need.length&&!BG_TRANSLATING.has(l)){BG_TRANSLATING.add(l);translate(l,need).catch(()=>{}).finally(()=>{BG_TRANSLATING.delete(l);if(lang()===l)schedule(0)})}}"""
if new_apply not in s:
    if old_apply not in s: raise SystemExit('apply function anchor missing')
    s=s.replace(old_apply,new_apply,1)

s=re.sub(r"const VERSION='[^']+';",f"const VERSION='{VER}';",s,count=1)
p.write_text(s,encoding='utf-8')

# Cache bust the translator on every root page that loads it.
for hp in Path('.').glob('*.html'):
    h=hp.read_text(encoding='utf-8')
    h=re.sub(r'i18n-ui\.js\?v=[^"\\s]+','i18n-ui.js?v='+VER,h)
    if hp.name=='index.html': h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
    hp.write_text(h,encoding='utf-8')
psw=Path('sw.js');sw=psw.read_text(encoding='utf-8');sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1);psw.write_text(sw,encoding='utf-8')
print('R104_APPLIED')
