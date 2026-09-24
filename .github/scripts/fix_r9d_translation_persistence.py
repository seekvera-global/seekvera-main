from pathlib import Path

p=Path('i18n-ui.js')
s=p.read_text(encoding='utf-8')
old="function bind(){capture(document);document.addEventListener('change',e=>{if(e.target?.id==='lang'||e.target?.id==='country')schedule(220)},true);new MutationObserver(ms=>{let added=false,locale=false;for(const m of ms){if(m.type==='attributes'&&m.target===document.documentElement&&['lang','dir'].includes(m.attributeName))locale=true;for(const n of m.addedNodes||[]){if(n.nodeType===1){capture(n);added=true}}}if(locale||added)schedule(180)}).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['lang','dir']});schedule(0)}"
new="function bind(){capture(document);document.addEventListener('change',e=>{if(e.target?.id==='lang'||e.target?.id==='country')schedule(120)},true);new MutationObserver(ms=>{let dirty=false,locale=false;const l=lang();for(const m of ms){if(m.type==='attributes'&&m.target===document.documentElement&&['lang','dir'].includes(m.attributeName))locale=true;if(m.type==='characterData'){const n=m.target;if(skipNode(n))continue;const now=n.nodeValue?.trim()||'';let src=textSource.get(n);if(!src&&worth(now)){textSource.set(n,now);src=now;dirty=true}else if(src&&l!=='en'){const expected=cached(l,src);if(!expected||now!==expected)dirty=true}}for(const n of m.addedNodes||[]){if(n.nodeType===1){capture(n);dirty=true}else if(n.nodeType===3&&!skipNode(n)){const now=n.nodeValue?.trim()||'';if(worth(now)&&!textSource.has(n)){textSource.set(n,now);dirty=true}}}}if(locale||dirty)schedule(locale?60:100)}).observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['lang','dir']});schedule(0)}"
if old not in s:
    raise SystemExit('R9c locale guard observer anchor not found')
s=s.replace(old,new,1)
s=s.replace("const VERSION='20260924-final-r9';","const VERSION='20260924-final-r9d';",1)
s=s.replace("serviceWorker.register('sw.js?v=20260924-az-r8')","serviceWorker.register('sw.js?v=20260924-final-r9d')")
p.write_text(s,encoding='utf-8')

for h in Path('.').glob('*.html'):
    t=h.read_text(encoding='utf-8')
    t=t.replace('i18n-ui.js?v=20260924-final-r9c','i18n-ui.js?v=20260924-final-r9d')
    t=t.replace('voice-ai.js?v=20260924-final-r9c','voice-ai.js?v=20260924-final-r9d')
    h.write_text(t,encoding='utf-8')

sw=Path('sw.js')
if sw.exists():
    t=sw.read_text(encoding='utf-8')
    t=t.replace('seekvera-final-r9c-20260924','seekvera-final-r9d-20260924')
    t=t.replace('i18n-ui.js?v=20260924-final-r9c','i18n-ui.js?v=20260924-final-r9d')
    t=t.replace('voice-ai.js?v=20260924-final-r9c','voice-ai.js?v=20260924-final-r9d')
    sw.write_text(t,encoding='utf-8')

print('R9d persistent translation patch applied')
