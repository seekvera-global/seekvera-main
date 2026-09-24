from pathlib import Path

# Fix the real race: a delayed /api/locale response must never override a user's manual country choice.
p=Path('global-ui.js')
s=p.read_text(encoding='utf-8')
old="async function autoCountryLocale(){const saved=String(localStorage.getItem('seekvera_country')||'').toUpperCase();if(localStorage.getItem('seekvera_country_explicit')==='1'&&saved&&saved!=='WW'){applyCountryProfile(saved);return}let code='';try{const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),2600);const r=await fetch(api('/api/locale'),{signal:ctrl.signal,cache:'no-store'});clearTimeout(timer);if(r.ok){const d=await r.json();if(/^[A-Z]{2}$/.test(d?.country||''))code=d.country}}catch{}if(!code)code=regionFromDevice();if(code&&COUNTRY_PROFILE[code])applyCountryProfile(code);}"
new="async function autoCountryLocale(){const saved=String(localStorage.getItem('seekvera_country')||'').toUpperCase();if(localStorage.getItem('seekvera_country_explicit')==='1'){if(saved&&saved!=='WW'&&COUNTRY_PROFILE[saved])applyCountryProfile(saved);return}let code='';try{const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),2600);const r=await fetch(api('/api/locale'),{signal:ctrl.signal,cache:'no-store'});clearTimeout(timer);if(r.ok){const d=await r.json();if(/^[A-Z]{2}$/.test(d?.country||''))code=d.country}}catch{}if(localStorage.getItem('seekvera_country_explicit')==='1')return;if(!code)code=regionFromDevice();if(localStorage.getItem('seekvera_country_explicit')==='1')return;if(code&&COUNTRY_PROFILE[code])applyCountryProfile(code);}"
if old not in s:
    raise SystemExit('autoCountryLocale R7 anchor not found')
s=s.replace(old,new,1)

old_bind="$('#country')?.addEventListener('change',e=>{const code=String(e.target.value||'').toUpperCase();if(!localeSyncing&&code!=='WW')applyCountryProfile(code,{markExplicit:true});setTimeout(localizeControls,0)})"
new_bind="$('#country')?.addEventListener('change',e=>{const code=String(e.target.value||'').toUpperCase();if(!localeSyncing){if(code==='WW'){localStorage.setItem('seekvera_country','WW');localStorage.setItem('seekvera_country_explicit','1')}else applyCountryProfile(code,{markExplicit:true})}setTimeout(localizeControls,0)})"
if old_bind in s:
    s=s.replace(old_bind,new_bind,1)
elif new_bind not in s:
    raise SystemExit('country manual-choice anchor not found')

p.write_text(s,encoding='utf-8')

# Make R9e a clean cache boundary across the live app.
p=Path('i18n-ui.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const VERSION='20260924-final-r9d';","const VERSION='20260924-final-r9e';",1)
s=s.replace("serviceWorker.register('sw.js?v=20260924-final-r9d')","serviceWorker.register('sw.js?v=20260924-final-r9e')")
p.write_text(s,encoding='utf-8')

for h in Path('.').glob('*.html'):
    t=h.read_text(encoding='utf-8')
    t=t.replace('global-ui.js?v=20260924-az-r8','global-ui.js?v=20260924-final-r9e')
    t=t.replace('global-ui.js?v=20260924-final-r9d','global-ui.js?v=20260924-final-r9e')
    t=t.replace('i18n-ui.js?v=20260924-final-r9d','i18n-ui.js?v=20260924-final-r9e')
    t=t.replace('voice-ai.js?v=20260924-final-r9d','voice-ai.js?v=20260924-final-r9e')
    h.write_text(t,encoding='utf-8')

sw=Path('sw.js')
if sw.exists():
    t=sw.read_text(encoding='utf-8')
    t=t.replace('seekvera-final-r9d-20260924','seekvera-final-r9e-20260924')
    t=t.replace('global-ui.js?v=20260924-az-r8','global-ui.js?v=20260924-final-r9e')
    t=t.replace('global-ui.js?v=20260924-final-r9d','global-ui.js?v=20260924-final-r9e')
    t=t.replace('i18n-ui.js?v=20260924-final-r9d','i18n-ui.js?v=20260924-final-r9e')
    t=t.replace('voice-ai.js?v=20260924-final-r9d','voice-ai.js?v=20260924-final-r9e')
    sw.write_text(t,encoding='utf-8')

print('R9e manual locale priority + cache boundary applied')
