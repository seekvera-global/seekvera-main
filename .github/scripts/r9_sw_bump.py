from pathlib import Path
import re
VER='20260924-final-r9b'
count=0
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    s=p.read_text(encoding='utf-8')
    if 'serviceWorker.register' not in s: continue
    ns=re.sub(r"sw\.js\?v=[^'\"]+",f'sw.js?v={VER}',s)
    if ns!=s:
        p.write_text(ns,encoding='utf-8'); count+=1
print('service worker registration pages updated',count)
assert "const CACHE='seekvera-final-r9b-20260924'" in Path('sw.js').read_text(encoding='utf-8')
