from pathlib import Path
p=Path('r60-runtime-guard.js')
s=p.read_text(encoding='utf-8')
old="window.addEventListener('seekvera:ai-response',()=>setTimeout(saveChat,40));window.addEventListener('pagehide',saveChat)"
new="window.addEventListener('seekvera:ai-response',saveChat);window.addEventListener('pagehide',saveChat)"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R60 synchronous chat save anchor missing')
p.write_text(s,encoding='utf-8')
print('R60 synchronous chat save patched')
