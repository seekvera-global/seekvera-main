from pathlib import Path
p=Path('r24-ai-controller.js');s=p.read_text(encoding='utf-8')
old="const m=new Map();for(const c of codes)add(m,c,c);for(const[c,names]of Object.entries(AR_COUNTRIES))for(const n of names)add(m,n,c);for(const[c,names]of Object.entries(COUNTRY_ALIASES))for(const n of names)add(m,n,c);"
new="const m=new Map();/* Raw 2-letter country codes are not natural-language aliases: words like 'to' must never become Tonga. Explicit codes remain supported by explicitCode(). */for(const[c,names]of Object.entries(AR_COUNTRIES))for(const n of names)add(m,n,c);for(const[c,names]of Object.entries(COUNTRY_ALIASES))for(const n of names)add(m,n,c);"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R61D country code collision anchor missing')
p.write_text(s,encoding='utf-8')
print('R61D country code collision fixed')
