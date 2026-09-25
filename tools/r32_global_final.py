from pathlib import Path
import re

VER='20260925-r44-stable-locale'
changed=[]

def write(path,text):
    p=Path(path); old=p.read_text(encoding='utf-8') if p.exists() else ''
    if old!=text:
        p.write_text(text,encoding='utf-8'); changed.append(path)

# Replace the old layered translation file with one deterministic universal runtime.
write('i18n-ui.js',Path('r32-i18n.js').read_text(encoding='utf-8'))

# Locale coordinator: keep 248-country source of truth, expose all 98 languages, and never
# let the delayed auto-country boot routine overwrite a user choice made just after page load.
p=Path('locale-r15.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"version:'[^']+'",f"version:'{VER}'",s,count=1)
if 'function ensureAllLanguageOptions()' not in s:
    anchor='function boot(){'
    helper="""function ensureAllLanguageOptions(){
  const l=$('#lang');if(!l)return;
  let dn=null;try{dn=new Intl.DisplayNames([normalizeLang(document.documentElement.lang||navigator.language||'en')],{type:'language'})}catch{}
  for(const code of Object.keys(LANG_PRIMARY))ensureOption(l,code,dn?.of(code)||code);
}
function boot(){ensureAllLanguageOptions();"""
    if anchor not in s: raise SystemExit('locale-r15 boot anchor missing')
    s=s.replace(anchor,helper,1)
old_boot="""  else setTimeout(()=>{
    let cc='';try{cc=String(localStorage.getItem('seekvera_country')||'').toUpperCase()}catch{}
    if(cc&&cc!=='WW'&&PROFILES[cc])applyState(localeStateFrom('country',cc),{explicit:false,reason:'boot-auto'});
    else applyState(localeStateFrom('country','WW'),{explicit:false,reason:'boot-worldwide'});
  },2800);"""
new_boot="""  else setTimeout(()=>{
    const late=storedState();
    if(late){applyState(late,{explicit:false,reason:'boot-late-user-choice'});return}
    let cc='';try{cc=String(localStorage.getItem('seekvera_country')||'').toUpperCase()}catch{}
    if(cc&&cc!=='WW'&&PROFILES[cc])applyState(localeStateFrom('country',cc),{explicit:false,reason:'boot-auto'});
    else applyState(localeStateFrom('country','WW'),{explicit:false,reason:'boot-worldwide'});
  },2800);"""
if old_boot in s:s=s.replace(old_boot,new_boot,1)
elif 'boot-late-user-choice' not in s:raise SystemExit('locale-r15 delayed boot anchor missing')
write('locale-r15.js',s)

# R14 is fallback only. When R32 exists it must never rewrite localized text/direction.
p=Path('locale-r14.js'); s=p.read_text(encoding='utf-8')
s,n=re.subn(r"(fil:\[(?:`[^`]*`,){18})`Live marketplace`",r"\1`Aktuwal na pamilihan`",s,count=1)
if n!=1 and 'Aktuwal na pamilihan' not in s: raise SystemExit('Filipino R14 live-marketplace anchor missing')
s=s.replace("const RTL=new Set(['ar','fa','ur','he','dv']);","const RTL=new Set(['ar','fa','ur','he','ps','dv']);",1)
if "const RTL=new Set(['ar','fa','ur','he','ps','dv']);" not in s: raise SystemExit('R14 RTL anchor missing')
old="function apply(){const {c,p}=pack();"
new="function apply(){if(window.SEEKVERA_I18N_R32?.schedule){window.SEEKVERA_I18N_R32.schedule(0);return}const {c,p}=pack();"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R14 apply anchor missing')
write('locale-r14.js',s)

# Dynamic marketplace content is localized before paint to avoid English flash/jitter.
p=Path('superapp.js'); s=p.read_text(encoding='utf-8')
s=s.replace("/^(ar|fa|ur)$/.test(el.value)","/^(ar|fa|ur|he|ps|dv)$/.test(el.value)")
s=s.replace("/^(ar|fa|ur)$/.test(lang())","/^(ar|fa|ur|he|ps|dv)$/.test(lang())")
new_live=r'''async function localizedDynamic(src){
 for(let i=0;i<24&&!window.SEEKVERA_I18N_R32;i++)await new Promise(r=>setTimeout(r,10));
 const rt=window.SEEKVERA_I18N_R32,l=rt?.lang?.()||lang();
 if(l!=='en'&&rt?.loadPack)await rt.loadPack(l);
 return window.SEEKVERA_I18N?.t?.(src)||src
}
function refreshDynamicI18n(){window.SEEKVERA_I18N_R32?.schedule?.(0)}
async function loadLiveListings(){const box=$('#liveListings');if(!box)return;try{const url=`${SB}/rest/v1/marketplace_listings?select=ad_ref,title,category,country,city,price,currency,price_type&status=eq.approved&expires_at=gt.${encodeURIComponent(new Date().toISOString())}&order=featured_rank.desc,created_at.desc&limit=8`;const r=await fetch(url,{headers:{apikey:SB_KEY,Authorization:`Bearer ${SB_KEY}`}});if(!r.ok)throw new Error();const rows=await r.json();if(!rows.length){const text=await localizedDynamic('No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.');box.innerHTML=`<div class="sv-empty">${esc(text)}</div>`;refreshDynamicI18n();return}const noPrice=await localizedDynamic('Price not supplied');box.innerHTML=rows.map(x=>`<a class="sv-listing" href="marketplace.html?q=${encodeURIComponent(x.title)}"><div class="sv-listing-media">🛒</div><div class="sv-listing-body"><h3 data-user-content="1">${esc(x.title)}</h3><div class="sv-listing-meta" data-user-content="1">${esc([x.category,x.city,x.country].filter(Boolean).join(' · '))}</div>${x.price!=null?`<div class="sv-price">${esc(x.currency||'')} ${Number(x.price).toLocaleString()}</div>`:`<div class="sv-listing-meta">${esc(noPrice)}</div>`}</div></a>`).join('');refreshDynamicI18n()}catch{const text=await localizedDynamic('Live listings could not be loaded right now. Try the Marketplace section directly.');box.innerHTML=`<div class="sv-empty">${esc(text)}</div>`;refreshDynamicI18n()}}
function bindRequest()'''
pat=r"async function loadLiveListings\(\)\{.*?\}\nfunction bindRequest\(\)"
s,n=re.subn(pat,lambda m:new_live,s,count=1,flags=re.S)
if n!=1 and 'async function localizedDynamic(src)' not in s:raise SystemExit('superapp live listing anchor missing')
write('superapp.js',s)

# AI: never answer a simple greeting in English when another language is selected.
p=Path('worker-r31.js'); s=p.read_text(encoding='utf-8')
old="function instantGreeting(language){const x=language.toLowerCase();if(x==='arabic')return'أهلاً! أنا مساعد SEEKVERA. قل لي ماذا تحتاج وسأساعدك بسرعة وأوصلك للقسم المناسب.';if(x==='french')return'Bonjour ! Je suis l’assistant SEEKVERA. Dites-moi ce dont vous avez besoin et je vous guiderai rapidement.';if(x==='chinese')return'你好！我是 SEEKVERA 助手。告诉我你需要什么，我会快速帮你找到合适的栏目。';if(x==='hindi')return'नमस्ते! मैं SEEKVERA सहायक हूँ। बताइए आपको क्या चाहिए, मैं जल्दी सही सेक्शन तक पहुँचने में मदद करूँगा।';return'Hi! I’m the SEEKVERA assistant. Tell me what you need and I’ll quickly help you find the right section.'}"
new="function instantGreeting(language){const x=language.toLowerCase();if(x==='english')return'Hi! I’m the SEEKVERA assistant. Tell me what you need and I’ll quickly help you find the right section.';if(x==='arabic')return'أهلاً! أنا مساعد SEEKVERA. قل لي ماذا تحتاج وسأساعدك بسرعة وأوصلك للقسم المناسب.';if(x==='french')return'Bonjour ! Je suis l’assistant SEEKVERA. Dites-moi ce dont vous avez besoin et je vous guiderai rapidement.';if(x==='chinese')return'你好！我是 SEEKVERA 助手。告诉我你需要什么，我会快速帮你找到合适的栏目。';if(x==='hindi')return'नमस्ते! मैं SEEKVERA सहायक हूँ। बताइए आपको क्या चाहिए, मैं जल्दी सही सेक्शन तक पहुँचने में मदद करूँगा।';return''}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('instantGreeting anchor missing')
old="if(simple(m))return json(req,{ok:true,response:instantGreeting(language),model:'seekvera-local-instant',language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath:'r31-local-instant'});"
new="if(simple(m)){const greeting=instantGreeting(language);if(greeting)return json(req,{ok:true,response:greeting,model:'seekvera-local-instant',language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath:'r32-local-instant'});}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('simple greeting anchor missing')
anchor="async function runModel(env,md,messages,maxTokens){"
helper="""async function localizedFallback(env,language,cat){const base=fallbackGuide(language==='Arabic'?'Arabic':'English',cat);if(language==='English'||language==='Arabic')return base;try{const r=await Promise.race([runModel(env,FAST,[{role:'system',content:`Translate the user-interface help sentence into ${language}. Return only the translation.`},{role:'user',content:base}],140),(async()=>{await sleep(1800);throw Error('fallback translate timeout')})()]);if(r?.text)return r.text}catch{}return'…'}\n"""
if helper.strip() not in s:
    if anchor not in s: raise SystemExit('runModel anchor missing')
    s=s.replace(anchor,helper+anchor,1)
old="const response=got?.text||fallbackGuide(language,cat),model=got?.model||'seekvera-latency-fallback';"
new="const response=got?.text||await localizedFallback(env,language,cat),model=got?.model||'seekvera-r32-localized-fallback';"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('fallback response anchor missing')
s=s.replace("text=text.replace(/2026-09-25 · R20/g,'2026-09-25 · R31C');","text=text.replace(/2026-09-25 · R(?:20|31C|32)/g,'2026-09-25 · R32');",1)
s=s.replace("h.set('x-seekvera-release','r31c')","h.set('x-seekvera-release','r32-global-final')",1)
s=s.replace("r31Runtime:'atomic-locale-localized-currency-fast-voice-smart-ai-r31c'","r31Runtime:'atomic-locale-localized-currency-fast-voice-smart-ai-r31c',r32:true,r32Runtime:'248-country-full-ui-language-lock-global-final'",1)
write('worker-r31.js',s)

# Bust every page/PWA cache so old phones cannot keep a competing translation runtime.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    t=p.read_text(encoding='utf-8'); before=t
    t=re.sub(r'i18n-ui\.js\?v=[^\"\']+',f'i18n-ui.js?v={VER}',t)
    t=re.sub(r'locale-r14\.js\?v=[^\"\']+',f'locale-r14.js?v={VER}',t)
    t=re.sub(r'locale-r15\.js\?v=[^\"\']+',f'locale-r15.js?v={VER}',t)
    t=re.sub(r'superapp\.js\?v=[^\"\']+',f'superapp.js?v={VER}',t)
    t=re.sub(r'sw\.js\?v=[^\"\']+',f'sw.js?v={VER}',t)
    if p.name=='index.html':
        t=re.sub(r'2026-09-25 · R(?:20|31C|32|43)','2026-09-25 · R44',t)
    if t!=before: p.write_text(t,encoding='utf-8'); changed.append(p.name)

p=Path('sw.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"const CACHE='[^']+'",f"const CACHE='seekvera-r44-stable-locale-20260925'",s,count=1)
write('sw.js',s)

print('R44 changed',len(changed),'files')
for x in changed: print(x)
