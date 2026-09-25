from pathlib import Path
p=Path('r31-ui-polish.js')
s=p.read_text(encoding='utf-8')
old="function controlResult(q){try{const c=window.SEEKVERA_R24_CONTROLLER?.detectControls?.(q)||{};if(c.country||c.language){window.SEEKVERA_R24_CONTROLLER?.applyControls?.(c);return c}}catch{}return null}"
new="function forceControl(c){let changed=false;if(c?.country){const code=String(c.country).toUpperCase(),e=document.querySelector('#country');try{localStorage.setItem('seekvera_country',code)}catch{}if(e&&[...e.options].some(o=>o.value===code)){e.value=code;e.dispatchEvent(new Event('change',{bubbles:true}));changed=true}}if(c?.language){const code=String(c.language).toLowerCase(),e=document.querySelector('#lang');try{localStorage.setItem('seekvera_lang',code);localStorage.setItem('seekvera_language_explicit','1')}catch{}if(e){if(![...e.options].some(o=>o.value===code))e.add(new Option(code.toUpperCase(),code));e.value=code;e.dispatchEvent(new Event('change',{bubbles:true}));changed=true}document.documentElement.lang=code;document.documentElement.dir=RTL.has(code)?'rtl':'ltr'}try{window.SEEKVERA_R24_CONTROLLER?.applyControls?.(c)}catch{}return changed}\nfunction controlResult(q){try{const c=window.SEEKVERA_R24_CONTROLLER?.detectControls?.(q)||{};if(c.country||c.language){forceControl(c);return c}}catch{}return null}"
if old in s:s=s.replace(old,new,1)
elif 'function forceControl(c)' not in s:raise SystemExit('R56C controlResult anchor missing')
p.write_text(s,encoding='utf-8')
print('R56C immediate locale controls patched')
