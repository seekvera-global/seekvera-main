from pathlib import Path
p=Path('r24-ai-controller.js')
s=p.read_text(encoding='utf-8')
old="function explicitCode(text,kind){const re=kind==='language'?/\\b(?:lang(?:uage)?|locale)\\s*[:=]?\\s*([a-z]{2,3})\\b/i:/\\b(?:country|market)\\s*[:=]?\\s*([a-z]{2})\\b/i;const m=String(text||'').match(re);return m?m[1]:''}"
new="function explicitCode(text,kind){const t=String(text||'').trim();const key=kind==='language'?'(?:lang(?:uage)?|locale)':'(?:country|market)';const n=kind==='language'?'{2,3}':'{2}';let m=t.match(new RegExp('\\\\b'+key+'\\\\s*[:=]\\\\s*([a-z]'+n+')\\\\b','i'));if(m)return m[1];m=t.match(new RegExp('\\\\b'+key+'\\\\s+([a-z]'+n+')\\\\s*$','i'));return m?m[1]:''}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R56E explicitCode anchor missing')
p.write_text(s,encoding='utf-8')
print('R56E explicit code parser made strict')
