from pathlib import Path
import re

# Inject the atomic locale coordinator before older locale engines on every public page.
tag='<script src="locale-r15.js?v=20260924-r15" defer></script>'
pages=[]
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):
        continue
    s=p.read_text(encoding='utf-8')
    t=re.sub(r'\s*<script src="locale-r15\.js\?v=[^"]+" defer></script>','',s)
    m=re.search(r'<script src="(?:superapp|voice-ai|global-ui|i18n-ui)\.js\?v=[^"]+" defer></script>',t)
    if m:
        t=t[:m.start()]+tag+'\n'+t[m.start():]
    elif '</body>' in t:
        t=t.replace('</body>',tag+'\n</body>',1)
    else:
        raise SystemExit(f'No R15 script anchor in {p.name}')
    t=re.sub(r'sw\.js\?v=[^"\']+','sw.js?v=20260924-r15',t)
    if p.name=='index.html':
        t=re.sub(r'Release 2026-09-24 · Worldwide R\d+','Release 2026-09-24 · Worldwide R15',t)
    if t!=s:
        p.write_text(t,encoding='utf-8')
    pages.append(p.name)

# Scope old global locale code to the real top locale selects.
p=Path('global-ui.js'); s=p.read_text(encoding='utf-8')
old="const $=s=>document.querySelector(s);const lang="
new="const svLocaleControl=id=>document.querySelector(`.sv-controls select#${id},select#${id}.sv-select`);const $=s=>s==='#country'?svLocaleControl('country'):s==='#lang'?svLocaleControl('lang'):s==='#currency'?svLocaleControl('currency'):document.querySelector(s);const lang="
if old in s:
    s=s.replace(old,new,1)
elif 'const svLocaleControl=id=>' not in s:
    raise SystemExit('global-ui selector anchor missing')
p.write_text(s,encoding='utf-8')

# Scope the general i18n engine too. Department pages may legitimately have input#country.
p=Path('i18n-ui.js'); s=p.read_text(encoding='utf-8')
if 'const i18nLocaleControl=id=>' not in s:
    s=s.replace("const api=p=>`${WORKER}${p}`;","const api=p=>`${WORKER}${p}`;\nconst i18nLocaleControl=id=>document.querySelector(`.sv-controls select#${id},select#${id}.sv-select`);",1)
s=s.replace('script,style,noscript,code,pre,svg,canvas,[data-no-i18n],#country,#lang,#currency','script,style,noscript,code,pre,svg,canvas,[data-no-i18n],.sv-controls #country,.sv-controls #lang,.sv-controls #currency')
s=s.replace('[data-no-i18n],#country,#lang,#currency','[data-no-i18n],.sv-controls #country,.sv-controls #lang,.sv-controls #currency')
s=s.replace("c=document.getElementById('country'),s=document.getElementById('lang'),cur=document.getElementById('currency')","c=i18nLocaleControl('country'),s=i18nLocaleControl('lang'),cur=i18nLocaleControl('currency')")
s=s.replace("const s=document.getElementById('lang');if(s&&!s.dataset.i18nR3)","const s=i18nLocaleControl('lang');if(s&&!s.dataset.i18nR3)")
s=re.sub(r"serviceWorker\.register\('sw\.js\?v=[^']+'\)","serviceWorker.register('sw.js?v=20260924-r15')",s)
s=s.replace("setTimeout(()=>{bind();apply()},500)","setTimeout(()=>{bind();apply()},80)")
p.write_text(s,encoding='utf-8')

# Navigation must use the same scoped controls and must not repaint five times.
p=Path('navigation.js'); s=p.read_text(encoding='utf-8')
if 'const localeControl=id=>' not in s:
    s=s.replace("let localeTimer=0,translateSeq=0;","let localeTimer=0,translateSeq=0;\nconst localeControl=id=>document.querySelector(`.sv-controls select#${id},select#${id}.sv-select`);",1)
s=s.replace("document.getElementById('lang')","localeControl('lang')")
s=s.replace("document.getElementById('country')","localeControl('country')")
s=s.replace("if(code==='WW')o.textContent='🌐';","if(code==='WW')o.textContent='🌐 '+(window.SEEKVERA_LOCALE_R14?.t?.('worldwide')||'Worldwide');")
s=re.sub(r"function scheduleLocalePass\(\)\{\s*clearTimeout\(localeTimer\);\s*const passes=\[0,120,500,1200\];\s*for\(const ms of passes\)setTimeout\(runLocaleEngines,ms\);\s*localeTimer=setTimeout\(runLocaleEngines,1800\);\s*\}","function scheduleLocalePass(){clearTimeout(localeTimer);localeTimer=setTimeout(runLocaleEngines,50)}",s,count=1)
s=s.replace("    const c=localeControl('country');if(!c)return;\n    c.value=code;c.dispatchEvent(new Event('input',{bubbles:true}));c.dispatchEvent(new Event('change',{bubbles:true}));","    const c=localeControl('country');\n    if(window.SEEKVERA_LOCALE_R15)window.SEEKVERA_LOCALE_R15.setCountry(code);\n    else {if(!c)return;c.value=code;c.dispatchEvent(new Event('input',{bubbles:true}));c.dispatchEvent(new Event('change',{bubbles:true}));}")
s=s.replace("  document.addEventListener('change',e=>{if(e.target?.id==='country'||e.target?.id==='lang'){if(e.target.id==='lang')localStorage.setItem('seekvera_lang',e.target.value);queueMicrotask(runLocaleEngines);scheduleLocalePass()}},true);","  document.addEventListener('change',e=>{const t=e.target;if(t&&(t===localeControl('country')||t===localeControl('lang'))){if(t===localeControl('lang'))localStorage.setItem('seekvera_lang',t.value);queueMicrotask(runLocaleEngines);scheduleLocalePass()}},true);")
p.write_text(s,encoding='utf-8')

# R14 deterministic visible translations: one pass only, no back-and-forth repaint.
p=Path('locale-r14.js'); s=p.read_text(encoding='utf-8')
s=s.replace("document.getElementById('lang')?.value","document.querySelector('.sv-controls select#lang,select#lang.sv-select')?.value")
s=s.replace("let timer=0;function schedule(ms=0){clearTimeout(timer);timer=setTimeout(()=>{apply();setTimeout(apply,80);setTimeout(apply,260)},ms)}","let timer=0;function schedule(ms=0){clearTimeout(timer);timer=setTimeout(apply,ms)}")
s=s.replace("window.SEEKVERA_LOCALE_R14={apply,schedule,languages:Object.keys(L),version:'20260924-r14'};","window.SEEKVERA_LOCALE_R14={apply,schedule,t:k=>{const {p}=pack();return p[IDX[k]]||L.en[IDX[k]]},languages:Object.keys(L),version:'20260924-r15'};")
p.write_text(s,encoding='utf-8')
p=Path('locale-r14-categories.js'); s=p.read_text(encoding='utf-8')
s=s.replace("document.getElementById('lang')?.value","document.querySelector('.sv-controls select#lang,select#lang.sv-select')?.value")
s=s.replace("let timer=0;function schedule(ms=0){clearTimeout(timer);timer=setTimeout(()=>{apply();setTimeout(apply,100);setTimeout(apply,300)},ms)}","let timer=0;function schedule(ms=0){clearTimeout(timer);timer=setTimeout(apply,ms)}")
p.write_text(s,encoding='utf-8')

# R15 itself: scope selects, preserve coherent programmatic country changes, add opt-in location/map/tracking helpers.
p=Path('locale-r15.js'); s=p.read_text(encoding='utf-8')
s=s.replace("const $=s=>document.querySelector(s);","const localeEl=id=>document.querySelector(`.sv-controls select#${id},select#${id}.sv-select`);const $=s=>s==='#country'?localeEl('country'):s==='#lang'?localeEl('lang'):s==='#currency'?localeEl('currency'):document.querySelector(s);",1)
s=s.replace("const t=e.target;if(!t||!['country','lang','currency'].includes(t.id))return;","const t=e.target;if(!t||!['country','lang','currency'].includes(t.id)||t!==$('#'+t.id))return;",1)
old="if(!e.isTrusted&&source!=='country'&&coherentProgrammaticChange(t))source='country';\n  const state=localeStateFrom(source,t.value);"
new="if(!e.isTrusted&&source!=='country'&&coherentProgrammaticChange(t)){let cc='US';try{cc=String(localStorage.getItem('seekvera_country')||'US').toUpperCase()}catch{};return applyState(localeStateFrom('country',cc),{explicit:false,reason:'programmatic-country'})}\n  const state=localeStateFrom(source,t.value);"
if old in s:
    s=s.replace(old,new,1)
if 'function locateOnce()' not in s:
    loc=r'''
let locationWatchId=null;
function savePosition(pos){const c=pos?.coords;if(!c)return null;const out={latitude:Number(c.latitude),longitude:Number(c.longitude),accuracy:Number(c.accuracy||0),timestamp:Date.now()};try{localStorage.setItem('seekvera_last_location',JSON.stringify(out));localStorage.setItem('seekvera_last_lat',String(out.latitude));localStorage.setItem('seekvera_last_lng',String(out.longitude))}catch{}return out}
function locateOnce(){return new Promise((resolve,reject)=>{if(!navigator.geolocation)return reject(new Error('geolocation_unavailable'));navigator.geolocation.getCurrentPosition(p=>resolve(savePosition(p)),reject,{enableHighAccuracy:true,timeout:12000,maximumAge:60000})})}
function mapUrl(c){return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(c.latitude+','+c.longitude)}`}
function ensureMapLink(c){const b=$('#nearMe');if(!b||!c)return null;let a=document.getElementById('svNearMap');if(!a){a=document.createElement('a');a.id='svNearMap';a.target='_blank';a.rel='noopener noreferrer';a.textContent='🗺️';a.setAttribute('aria-label','Open current location on map');a.style.marginInlineStart='8px';b.insertAdjacentElement('afterend',a)}a.href=mapUrl(c);a.hidden=false;return a}
function bindLocationTools(){const b=$('#nearMe');if(!b||b.dataset.r15Bound==='1')return;b.dataset.r15Bound='1';b.addEventListener('click',async()=>{b.disabled=true;const old=b.textContent;b.textContent='📍 …';try{const c=await locateOnce();ensureMapLink(c);b.textContent='📍 ✓'}catch{b.textContent=old}finally{b.disabled=false}})}
function startLocationTracking(onUpdate){if(!navigator.geolocation)throw new Error('geolocation_unavailable');if(locationWatchId!==null)navigator.geolocation.clearWatch(locationWatchId);locationWatchId=navigator.geolocation.watchPosition(p=>{const c=savePosition(p);if(c&&typeof onUpdate==='function')onUpdate(c)},()=>{},{enableHighAccuracy:true,maximumAge:15000,timeout:20000});return locationWatchId}
function stopLocationTracking(){if(locationWatchId!==null&&navigator.geolocation){navigator.geolocation.clearWatch(locationWatchId);locationWatchId=null}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bindLocationTools,{once:true});else bindLocationTools();
'''
    s=s.replace("const st=document.createElement('style');",loc+"const st=document.createElement('style');",1)
    s=s.replace("debug:()=>({lastSignature,lastReason,syncing})","debug:()=>({lastSignature,lastReason,syncing}),\n  location:{locate:locateOnce,startTracking:startLocationTracking,stopTracking:stopLocationTracking,mapUrl}",1)
p.write_text(s,encoding='utf-8')

# Cache bust all locale engines and make them network-first.
p=Path('sw.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"const CACHE='[^']+';","const CACHE='seekvera-r15-atomic-20260924';",s,count=1)
if "'./locale-r15.js'" not in s:
    s=s.replace("'./i18n-ui.js','./i18n-premium.css'","'./i18n-ui.js','./locale-r15.js','./locale-r14.js','./locale-r14-categories.js','./i18n-premium.css'",1)
s=s.replace("(?:i18n-ui|voice-ai|global-ui|superapp|navigation)\\.js$","(?:i18n-ui|voice-ai|global-ui|superapp|navigation|locale-r15|locale-r14|locale-r14-categories)\\.js$")
p.write_text(s,encoding='utf-8')

# Future Cloudflare deploys must watch the new locale files.
p=Path('.github/workflows/deploy-cloudflare.yml'); s=p.read_text(encoding='utf-8')
if "- 'locale-r15.js'" not in s:
    s=s.replace("      - 'i18n-ui.js'\n","      - 'i18n-ui.js'\n      - 'locale-r15.js'\n      - 'locale-r14.js'\n      - 'locale-r14-categories.js'\n",1)
s=s.replace("assert 'seekvera-r11-worldwide-20260924' in sw","assert 'seekvera-r15-atomic-20260924' in sw")
p.write_text(s,encoding='utf-8')

print('R15 FINAL PATCH:',len(pages),'public pages')
