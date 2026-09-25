from pathlib import Path

p=Path('r32-i18n.js')
s=p.read_text(encoding='utf-8')

if 'r32-static-v5' in s:
    print('R32 static-pack runtime already patched v5')
    raise SystemExit(0)
if 'r32-static-v4' in s:
    raise SystemExit('Older generated R32 runtime detected; restore the source runtime before applying v5')

s=s.replace("const SRC=new WeakMap(),ATTRSRC=new WeakMap(),MEM=new Map();",
            "const SRC=new WeakMap(),ATTRSRC=new WeakMap(),MEM=new Map(),PACKS=new Map(),PACKING=new Map(),RENDERED_TEXT=new WeakMap(),RENDERED_ATTR=new WeakMap();",1)

anchor="function put(l,s,v){v=String(v||'').trim();if(!v||v===s)return;MEM.set(l+'\\u0000'+s,v);try{localStorage.setItem(k(l,s),v)}catch{}}"
addition=anchor+"\n/* r32-static-v5: atomic local packs + render/source separation */\n"+r"""async function loadPack(l){
 l=norm(l);if(l==='en')return true;if(PACKS.has(l))return true;if(PACKING.has(l))return PACKING.get(l);
 const task=(async()=>{try{const r=await fetch('/i18n-r32/'+encodeURIComponent(l)+'.json?v=20260925-r32-static-v5',{cache:'force-cache'});if(!r.ok)throw Error('pack '+r.status);const d=await r.json();const t=d?.translations;if(!t||typeof t!=='object')throw Error('invalid pack');for(const [src,v] of Object.entries(t)){const val=String(v||'').trim();if(val&&val!==src)MEM.set(l+'\u0000'+src,val)}PACKS.set(l,d);document.documentElement.dataset.seekveraPackReady=l;return true}catch(e){console.warn('SEEKVERA local language pack unavailable',l,e);return false}finally{PACKING.delete(l)}})();
 PACKING.set(l,task);return task
}
function markAttr(el,a,v){let m=RENDERED_ATTR.get(el);if(!m){m={};RENDERED_ATTR.set(el,m)}m[a]=String(v||'').trim()}
"""
if anchor not in s: raise SystemExit('put anchor missing')
s=s.replace(anchor,addition,1)

old="async function translate(l,arr){const unique=[...new Set(arr.filter(s=>worth(s)&&!get(l,s)))];if(!unique.length)return;"
new="async function translate(l,arr){await loadPack(l);const unique=[...new Set(arr.filter(s=>worth(s)&&!get(l,s)))];if(!unique.length)return;"
if old not in s: raise SystemExit('translate anchor missing')
s=s.replace(old,new,1)

old="function setText(n,src,l){const v=l==='en'?src:get(l,src);if(v){const raw=n.nodeValue||'',t=raw.trim();n.nodeValue=t?raw.replace(t,v):v;return true}if(l!=='en'&&n.parentElement?.closest?.('header,main,footer,nav,.sv-modal')){const raw=n.nodeValue||'',t=raw.trim();if(t&&t!=='…')n.nodeValue=raw.replace(t,'…')}return false}\nfunction setAttr(el,a,src,l){const v=l==='en'?src:get(l,src);if(v){el.setAttribute(a,v);return true}if(l!=='en'&&a==='placeholder')el.setAttribute(a,'…');return false}"
new="function setText(n,src,l){const v=l==='en'?src:get(l,src);if(!v)return false;const raw=n.nodeValue||'',t=raw.trim(),next=t?raw.replace(t,v):v;RENDERED_TEXT.set(n,String(next).trim());if(next!==raw)n.nodeValue=next;return true}\nfunction setAttr(el,a,src,l){const v=l==='en'?src:get(l,src);if(!v)return false;markAttr(el,a,v);if(el.getAttribute(a)!==v)el.setAttribute(a,v);return true}"
if old not in s: raise SystemExit('setText/setAttr anchor missing')
s=s.replace(old,new,1)

old="async function apply(){const my=++seq,l=lang();applying=true;document.documentElement.lang=l;document.documentElement.dir=RTL.has(l)?'rtl':'ltr';capture(document);const texts=[],attrs=[],need=[];"
new="async function apply(){const my=++seq,l=lang();if(l!=='en'){await loadPack(l);if(my!==seq)return}applying=true;document.documentElement.lang=l;document.documentElement.dir=RTL.has(l)?'rtl':'ltr';capture(document);const texts=[],attrs=[],need=[];"
if old not in s: raise SystemExit('apply anchor missing')
s=s.replace(old,new,1)

old="new MutationObserver(ms=>{if(applying)return;let dirty=false;for(const m of ms){if(m.type==='characterData'){const n=m.target;if(!skipped(n)){const now=n.nodeValue?.trim();if(worth(now)&&!SRC.has(n))SRC.set(n,now);dirty=true}}for(const n of m.addedNodes||[]){if(n.nodeType===1){capture(n);dirty=true}else if(n.nodeType===3&&!skipped(n)){const s=n.nodeValue?.trim();if(worth(s)&&!SRC.has(n))SRC.set(n,s);dirty=true}}}if(dirty)schedule(55)}).observe(document.documentElement,{subtree:true,childList:true,characterData:true});schedule(0);"
new="new MutationObserver(ms=>{if(applying)return;let dirty=false;for(const m of ms){if(m.type==='characterData'){const n=m.target;if(!skipped(n)){const now=String(n.nodeValue||'').trim(),rendered=RENDERED_TEXT.get(n);if(rendered!==undefined&&now===rendered)continue;RENDERED_TEXT.delete(n);if(worth(now)){SRC.set(n,now);dirty=true}}}else if(m.type==='attributes'){const el=m.target,a=m.attributeName;if(el&&a&&ATTRS.includes(a)&&!el.closest?.(SKIP)){const now=String(el.getAttribute(a)||'').trim(),rendered=RENDERED_ATTR.get(el)?.[a];if(rendered!==undefined&&now===rendered)continue;const rm=RENDERED_ATTR.get(el);if(rm)delete rm[a];if(worth(now)){let mm=ATTRSRC.get(el);if(!mm){mm={};ATTRSRC.set(el,mm)}mm[a]=now;dirty=true}}}for(const n of m.addedNodes||[]){if(n.nodeType===1){capture(n);dirty=true}else if(n.nodeType===3&&!skipped(n)){const now=String(n.nodeValue||'').trim();if(worth(now)){SRC.set(n,now);dirty=true}}}}if(dirty)schedule(PACKS.has(lang())?0:30)}).observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:ATTRS});loadPack(lang()).then(()=>schedule(0));schedule(0);"
if old not in s: raise SystemExit('mutation observer anchor missing')
s=s.replace(old,new,1)

old="window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang};"
new="window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang,loadPack,packReady:l=>PACKS.has(norm(l)),packCount:()=>PACKS.size};"
if old not in s: raise SystemExit('export anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('R32 static-pack runtime patched v5')
