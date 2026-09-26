from pathlib import Path

# R76: bind the complete 98 static packs to every visible app-owned UI string and
# make every late/dynamic controller consume the CURRENT R32 language at write time.

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
let staticGuardStarted=false,staticGuardQueued=false;
function ensureStaticGuard(){
 if(staticGuardStarted||!document.documentElement)return;staticGuardStarted=true;
 new MutationObserver(ms=>{if(norm(lang())==='en')return;if(!ms.some(m=>m.type==='characterData'||m.type==='attributes'||(m.addedNodes&&m.addedNodes.length)))return;if(staticGuardQueued)return;staticGuardQueued=true;queueMicrotask(()=>{staticGuardQueued=false;sweepStaticPack(lang())})}).observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:ATTRS});
}
'''
if 'function sweepStaticPack(l)' not in s:
    if anchor not in s: raise SystemExit('i18n sweep insert anchor missing')
    s=s.replace(anchor,anchor+insert,1)
else:
    a=s.index('function staticPackText(l,src)')
    b=s.index('async function apply()',a)
    s=s[:a]+insert+s[b:]
old="document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;applying=false}"
new="document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;ensureStaticGuard();sweepStaticPack(l);try{window.SEEKVERA_GLOBAL_UI?.localizeControls?.()}catch{}try{window.SEEKVERA_R22_CATEGORY_LOCK?.lock?.()}catch{}try{window.SEEKVERA_SUPERAPP_I18N?.refreshDynamicBoxes?.()}catch{}sweepStaticPack(l);const settle=()=>{if(norm(lang())===l)sweepStaticPack(l)};setTimeout(settle,35);setTimeout(settle,90);setTimeout(settle,135);applying=false}"
if old in s:s=s.replace(old,new,1)
else:
    candidates=[
      "document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;sweepStaticPack(l);try{window.SEEKVERA_GLOBAL_UI?.localizeControls?.()}catch{}try{window.SEEKVERA_R22_CATEGORY_LOCK?.lock?.()}catch{}try{window.SEEKVERA_SUPERAPP_I18N?.refreshDynamicBoxes?.()}catch{}sweepStaticPack(l);const settle=()=>{if(norm(lang())===l)sweepStaticPack(l)};setTimeout(settle,35);setTimeout(settle,90);setTimeout(settle,135);applying=false}",
      "document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;sweepStaticPack(l);try{window.SEEKVERA_GLOBAL_UI?.localizeControls?.()}catch{}try{window.SEEKVERA_R22_CATEGORY_LOCK?.lock?.()}catch{}try{window.SEEKVERA_SUPERAPP_I18N?.refreshDynamicBoxes?.()}catch{}sweepStaticPack(l);applying=false}",
      "document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;sweepStaticPack(l);try{window.SEEKVERA_GLOBAL_UI?.localizeControls?.()}catch{}try{window.SEEKVERA_R22_CATEGORY_LOCK?.lock?.()}catch{}sweepStaticPack(l);applying=false}",
      "document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;sweepStaticPack(l);applying=false}"
    ]
    for c in candidates:
        if c in s:
            s=s.replace(c,new,1);break
    else: raise SystemExit('i18n apply completion anchor missing')
oldexp="window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang,loadPack,packReady:l=>PACKS.has(norm(l)),packCount:()=>PACKS.size};"
newexp="window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang,loadPack,t:(src,l=lang())=>staticPackText(norm(l),src),sweep:()=>sweepStaticPack(lang()),packReady:l=>PACKS.has(norm(l)),packCount:()=>PACKS.size};"
if oldexp in s:s=s.replace(oldexp,newexp,1)
elif newexp not in s:raise SystemExit('i18n export anchor missing')
p.write_text(s,encoding='utf-8')

p=Path('global-ui.js')
s=p.read_text(encoding='utf-8')
old="function labels(){return LOCALE_UI[langCode()]||LOCALE_UI.en}"
new="function labels(){const c=langCode(),base=LOCALE_UI[c]||LOCALE_UI.en,src=LOCALE_UI.en,rt=window.SEEKVERA_I18N_R32;return src.map((x,i)=>{const v=rt?.t?.(x,c);return v&&v!==x?v:String(base[i]||x)})}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('global labels anchor missing')
old_end="if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(init,20),{once:true});else setTimeout(init,20);\n})();"
new_end="if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(init,20),{once:true});else setTimeout(init,20);\nwindow.SEEKVERA_GLOBAL_UI={localizeControls};\n})();"
if old_end in s:s=s.replace(old_end,new_end,1)
elif "window.SEEKVERA_GLOBAL_UI={localizeControls};" not in s:raise SystemExit('global export anchor missing')
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
start=s.index('async function localizedDynamic(src){')
end=s.index('function bindRequest(){',start)
replacement=r'''async function localizedDynamic(src){
 for(let i=0;i<40&&!window.SEEKVERA_I18N_R32;i++)await new Promise(r=>setTimeout(r,10));
 const rt=window.SEEKVERA_I18N_R32;let l=rt?.lang?.()||lang();
 if(l!=='en'&&rt?.loadPack)await rt.loadPack(l);
 const live=rt?.lang?.()||lang();
 if(live!==l){l=live;if(l!=='en'&&rt?.loadPack)await rt.loadPack(l)}
 return rt?.t?.(src,l)||window.SEEKVERA_I18N?.t?.(src)||src
}
async function renderDynamicBox(box,src){
 if(!box||!src)return;box.dataset.r76I18nSource=src;const token=String((Number(box.dataset.r76I18nToken)||0)+1);box.dataset.r76I18nToken=token;
 let text=await localizedDynamic(src);const rt=window.SEEKVERA_I18N_R32,l=rt?.lang?.()||lang();if(l!=='en'&&rt?.loadPack)await rt.loadPack(l);text=rt?.t?.(src,l)||text;
 if(box.dataset.r76I18nSource===src&&box.dataset.r76I18nToken===token){let empty=box.querySelector('.sv-empty');if(!empty){box.innerHTML='<div class="sv-empty"></div>';empty=box.querySelector('.sv-empty')}empty.textContent=text}
}
async function refreshDynamicBoxes(){const box=$('#liveListings'),src=box?.dataset?.r76I18nSource;if(box&&src)await renderDynamicBox(box,src)}
function refreshDynamicI18n(){refreshDynamicBoxes().catch(()=>{});window.SEEKVERA_I18N_R32?.schedule?.(0)}
window.SEEKVERA_SUPERAPP_I18N={refreshDynamicBoxes};
async function loadLiveListings(){const box=$('#liveListings');if(!box)return;try{const url=`${SB}/rest/v1/marketplace_listings?select=ad_ref,title,category,country,city,price,currency,price_type&status=eq.approved&expires_at=gt.${encodeURIComponent(new Date().toISOString())}&order=featured_rank.desc,created_at.desc&limit=8`;const r=await fetch(url,{headers:{apikey:SB_KEY,Authorization:`Bearer ${SB_KEY}`}});if(!r.ok)throw new Error();const rows=await r.json();if(!rows.length){await renderDynamicBox(box,'No approved live marketplace listings are available right now.');refreshDynamicI18n();return}delete box.dataset.r76I18nSource;delete box.dataset.r76I18nToken;const noPrice=await localizedDynamic('Price not supplied');box.innerHTML=rows.map(x=>`<a class="sv-listing" href="marketplace.html?q=${encodeURIComponent(x.title)}"><div class="sv-listing-media">🛒</div><div class="sv-listing-body"><h3 data-user-content="1">${esc(x.title)}</h3><div class="sv-listing-meta" data-user-content="1">${esc([x.category,x.city,x.country].filter(Boolean).join(' · '))}</div>${x.price!=null?`<div class="sv-price">${esc(x.currency||'')} ${Number(x.price).toLocaleString()}</div>`:`<div class="sv-listing-meta">${esc(noPrice)}</div>`}</div></a>`).join('');refreshDynamicI18n()}catch{await renderDynamicBox(box,'Live listings could not be loaded right now. Try the Marketplace section directly.');refreshDynamicI18n()}}
'''
s=s[:start]+replacement+s[end:]
p.write_text(s,encoding='utf-8')

print('R76 static UI binding fix applied')
