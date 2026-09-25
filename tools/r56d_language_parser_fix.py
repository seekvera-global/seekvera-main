from pathlib import Path
p=Path('r24-ai-controller.js')
s=p.read_text(encoding='utf-8')
old="function buildLanguageNames(){if(languageNames)return languageNames;const m=new Map();for(const c of LANGS)add(m,c,c);for(const[c,names]of Object.entries(AR_ALIASES))for(const n of names)add(m,n,c);"
new="function buildLanguageNames(){if(languageNames)return languageNames;const m=new Map();/* Raw 2/3-letter language codes are intentionally NOT aliases here: words like 'to' must not be mistaken for Tongan. Explicit codes remain supported by explicitCode(). */for(const[c,names]of Object.entries(AR_ALIASES))for(const n of names)add(m,n,c);"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R56D buildLanguageNames anchor missing')
p.write_text(s,encoding='utf-8')
print('R56D ambiguous short language-code aliases removed')
