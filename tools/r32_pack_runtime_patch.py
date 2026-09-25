from pathlib import Path

p=Path('r32-i18n.js')
s=p.read_text(encoding='utf-8')

s=s.replace("const SRC=new WeakMap(),ATTRSRC=new WeakMap(),MEM=new Map();",
            "const SRC=new WeakMap(),ATTRSRC=new WeakMap(),MEM=new Map(),PACKS=new Map(),PACKING=new Map();",1)

anchor="function put(l,s,v){v=String(v||'').trim();if(!v||v===s)return;MEM.set(l+'\\u0000'+s,v);try{localStorage.setItem(k(l,s),v)}catch{}}"
addition=anchor+"\n"+r"""async function loadPack(l){
 if(l==='en')return true;if(PACKS.has(l))return true;if(PACKING.has(l))return PACKING.get(l);
 const task=(async()=>{try{const r=await fetch('/i18n-r32/'+encodeURIComponent(l)+'.json?v=20260925-r32-static-v2',{cache:'force-cache'});if(!r.ok)throw Error('pack '+r.status);const d=await r.json();const t=d?.translations;if(!t||typeof t!=='object')throw Error('invalid pack');for(const [src,v] of Object.entries(t)){const val=String(v||'').trim();if(val)MEM.set(l+'\u0000'+src,val)}PACKS.set(l,d);document.documentElement.dataset.seekveraPackReady=l;return true}catch(e){console.warn('SEEKVERA local language pack unavailable',l,e);return false}finally{PACKING.delete(l)}})();
 PACKING.set(l,task);return task
}"""
if anchor not in s: raise SystemExit('put anchor missing')
s=s.replace(anchor,addition,1)

old="async function translate(l,arr){const unique=[...new Set(arr.filter(s=>worth(s)&&!get(l,s)))];if(!unique.length)return;"
new="async function translate(l,arr){await loadPack(l);const unique=[...new Set(arr.filter(s=>worth(s)&&!get(l,s)))];if(!unique.length)return;"
if old not in s: raise SystemExit('translate anchor missing')
s=s.replace(old,new,1)

old="if(m.type==='characterData'){const n=m.target;if(!skipped(n)){const now=n.nodeValue?.trim();if(worth(now)&&!SRC.has(n))SRC.set(n,now);dirty=true}}"
new="if(m.type==='characterData'){const n=m.target;if(!skipped(n)){const now=n.nodeValue?.trim();if(worth(now))SRC.set(n,now);dirty=true}}else if(m.type==='attributes'){const el=m.target,a=m.attributeName;if(el&&a&&ATTRS.includes(a)&&!el.closest?.(SKIP)){const now=el.getAttribute(a)?.trim();if(worth(now)){let mm=ATTRSRC.get(el);if(!mm){mm={};ATTRSRC.set(el,mm)}mm[a]=now;dirty=true}}}"
if old not in s: raise SystemExit('mutation anchor missing')
s=s.replace(old,new,1)

old="}).observe(document.documentElement,{subtree:true,childList:true,characterData:true});schedule(0);"
new="}).observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:ATTRS});loadPack(lang()).then(()=>schedule(0));schedule(0);"
if old not in s: raise SystemExit('observer options anchor missing')
s=s.replace(old,new,1)

old="window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang};"
new="window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang,loadPack,packReady:l=>PACKS.has(norm(l)),packCount:()=>PACKS.size};"
if old not in s: raise SystemExit('export anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('R32 static-pack runtime patched')
