from pathlib import Path

# R76: bind the already-complete 98 static packs to every visible app-owned UI string,
# including elements intentionally skipped by the older generic translator (category lock,
# select options, late-rendered marketplace status text, and decorated captions/icons).

p=Path('i18n-ui.js')
s=p.read_text(encoding='utf-8')
anchor="function markAttr(el,a,v){let m=RENDERED_ATTR.get(el);if(!m){m={};RENDERED_ATTR.set(el,m)}m[a]=String(v||'').trim()}\n"
insert=r'''function staticPackText(l,src){src=String(src||'').trim();if(!src||l==='en')return src;const t=PACKS.get(norm(l))?.translations||{};return String(t[src]||t[plainKey(src)]||get(norm(l),src)||get(norm(l),plainKey(src))||src).trim()}
function translatedDecorated(t,src){src=String(src||'').trim();if(!src)return'';const direct=String(t[src]||'').trim();if(direct)return direct;const key=plainKey(src),v=String(t[key]||'').trim();if(!key||!v||v===key)return'';return src.replace(key,v)}
function sweepStaticPack(l){
 l=norm(l);if(l==='en')return;const t=PACKS.get(l)?.translations;if(!t||typeof t!=='object')return;
 const root=document.body||document.documentElement;if(!root)return;
 const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;
 while((n=w.nextNode())){
  const p=n.parentElement;if(!p||p.closest('script,style,noscript,code,pre,textarea,[data-user-content],.ai-msg'))continue;
  const raw=String(n.nodeValue||''),src=raw.trim(),v=translatedDecorated(t,src);
  if(src&&v&&v!==src)n.nodeValue=raw.replace(src,v);
 }
 for(const el of document.querySelectorAll('[placeholder],[aria-label],[title]')){
  if(el.closest?.('[data-user-content],.ai-msg'))continue;
  for(const a of ATTRS){const src=String(el.getAttribute(a)||'').trim(),v=translatedDecorated(t,src);if(src&&v&&v!==src)el.setAttribute(a,v)}
 }
}
'''
if 'function sweepStaticPack(l)' not in s:
    if anchor not in s: raise SystemExit('i18n sweep insert anchor missing')
    s=s.replace(anchor,anchor+insert,1)
else:
    old=r'''function staticPackText(l,src){src=String(src||'').trim();if(!src||l==='en')return src;const t=PACKS.get(norm(l))?.translations||{};return String(t[src]||get(norm(l),src)||src).trim()}
function sweepStaticPack(l){
 l=norm(l);if(l==='en')return;const t=PACKS.get(l)?.translations;if(!t||typeof t!=='object')return;
 const root=document.body||document.documentElement;if(!root)return;
 const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;
 while((n=w.nextNode())){
  const p=n.parentElement;if(!p||p.closest('script,style,noscript,code,pre,textarea,[data-user-content],.ai-msg'))continue;
  const raw=String(n.nodeValue||''),src=raw.trim(),v=String(t[src]||'').trim();
  if(src&&v&&v!==src)n.nodeValue=raw.replace(src,v);
 }
 for(const el of document.querySelectorAll('[placeholder],[aria-label],[title]')){
  if(el.closest?.('[data-user-content],.ai-msg'))continue;
  for(const a of ATTRS){const src=String(el.getAttribute(a)||'').trim(),v=String(t[src]||'').trim();if(src&&v&&v!==src)el.setAttribute(a,v)}
 }
}
'''
    if old not in s: raise SystemExit('existing i18n sweep block missing')
    s=s.replace(old,insert,1)
old="document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;applying=false}"
new="document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;sweepStaticPack(l);applying=false}"
if old in s:s=s.replace(old,new,1)
oldexp="window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang,loadPack,packReady:l=>PACKS.has(norm(l)),packCount:()=>PACKS.size};"
newexp="window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang,loadPack,t:(src,l=lang())=>staticPackText(norm(l),src),sweep:()=>sweepStaticPack(lang()),packReady:l=>PACKS.has(norm(l)),packCount:()=>PACKS.size};"
if oldexp in s:s=s.replace(oldexp,newexp,1)
elif newexp not in s:raise SystemExit('i18n export anchor missing')
p.write_text(s,encoding='utf-8')

p=Path('r22-category-lock.js')
s=p.read_text(encoding='utf-8')
old="function titles(l){const d=window.SEEKVERA_R14_CATEGORIES?.data?.[l];return Array.isArray(d)&&d.length>=31?d:EN_TITLES}"
new="function titles(l){const d=window.SEEKVERA_R14_CATEGORIES?.data?.[l],fallback=Array.isArray(d)&&d.length>=31?d:EN_TITLES,rt=window.SEEKVERA_I18N_R32;return l==='en'?EN_TITLES:EN_TITLES.map((src,i)=>{const v=rt?.t?.(src,l);return v&&v!==src?v:String(fallback[i]||src)})}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('category title anchor missing')
p.write_text(s,encoding='utf-8')

p=Path('superapp.js')
s=p.read_text(encoding='utf-8')
old="""async function localizedDynamic(src){
 for(let i=0;i<24&&!window.SEEKVERA_I18N_R32;i++)await new Promise(r=>setTimeout(r,10));
 const rt=window.SEEKVERA_I18N_R32,l=rt?.lang?.()||lang();
 if(l!=='en'&&rt?.loadPack)await rt.loadPack(l);
 return window.SEEKVERA_I18N?.t?.(src)||src
}"""
new="""async function localizedDynamic(src){
 for(let i=0;i<24&&!window.SEEKVERA_I18N_R32;i++)await new Promise(r=>setTimeout(r,10));
 const rt=window.SEEKVERA_I18N_R32,l=rt?.lang?.()||lang();
 if(l!=='en'&&rt?.loadPack)await rt.loadPack(l);
 return rt?.t?.(src,l)||window.SEEKVERA_I18N?.t?.(src)||src
}"""
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('dynamic i18n anchor missing')
p.write_text(s,encoding='utf-8')

print('R76 static UI binding fix applied')
