from pathlib import Path

# 1) Deal Agent: keep the unauthenticated status on a source string that is already
# present in every static language pack, so the offline/static translator can render it.
p=Path('deal-agent.js')
s=p.read_text(encoding='utf-8')
old="}else $('#authStatus').textContent='Not signed in. Deal Agent remains OFF by default.'}"
new="}else $('#authStatus').textContent='Not signed in.'}"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('Deal Agent auth-status anchor missing')
p.write_text(s,encoding='utf-8')

# 2) Marketplace/Post Ad: SELECT/OPTION text is intentionally skipped by the generic
# translator because changing option text can change its submitted value. Give each
# option a stable canonical value, then localize only its visible label from the already
# loaded static pack. Canonical category values therefore remain unchanged for DB/API use.
block=r'''<script data-no-i18n="1" id="sv-category-option-locale">
(()=>{'use strict';
 const IDX={'Property':5,'Cars & Auto':6,'Jobs':7,'Shopping':8,'Services':10,'Equipment':11,'Boats':12,'Import & Export':13,'Shipping & Logistics':14,'Solar & Energy':18,'Education':19,'Health':20,'Food & Restaurants':9,'Technology & Software':16,'Business':30,'Aircraft':2};
 function apply(){
  const sel=document.getElementById('category');if(!sel)return;
  const lang=window.SEEKVERA_I18N_R32?.lang?.()||document.documentElement.lang||'en';
  const table=window.SEEKVERA_R14_CATEGORIES?.data?.[lang]||null;
  const tr=window.SEEKVERA_I18N?.t;
  for(const o of sel.options){
   const src=o.dataset.svCategorySource||o.textContent.trim();
   if(!o.dataset.svCategorySource){o.dataset.svCategorySource=src;o.setAttribute('value',o.getAttribute('value')||src)}
   let label=typeof tr==='function'?String(tr(src)||'').trim():'';
   if(!label||label===src){
    if(table&&Number.isInteger(IDX[src]))label=table[IDX[src]]||src;
    else if(table&&src==='Travel & Hotels')label=(table[1]||'')+' / '+(table[3]||'');
    else label=src;
   }
   if(o.textContent!==label)o.textContent=label;
  }
 }
 function later(){apply();setTimeout(apply,60);setTimeout(apply,250)}
 document.addEventListener('change',e=>{if(e.target?.id==='lang'||e.target?.id==='country')later()},true);
 new MutationObserver(ms=>{if(ms.some(m=>['lang','data-seekvera-pack-ready','data-seekvera-i18n-ready'].includes(m.attributeName)))later()}).observe(document.documentElement,{attributes:true,attributeFilter:['lang','data-seekvera-pack-ready','data-seekvera-i18n-ready']});
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',later,{once:true});else later();
})();
</script>'''
for name in ('marketplace.html','post-ad.html'):
    p=Path(name);s=p.read_text(encoding='utf-8')
    if 'id="sv-category-option-locale"' not in s:
        if '</body>' not in s:raise SystemExit(name+' body close missing')
        s=s.replace('</body>',block+'\n</body>',1)
    p.write_text(s,encoding='utf-8')

print('R51 deep locale fix applied: marketplace/post-ad option labels + Deal Agent status')
