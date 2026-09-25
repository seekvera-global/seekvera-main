from pathlib import Path
import re

VER='20260925-r54-ai-experience'
changed=[]
for p in Path('.').glob('*.html'):
    s=p.read_text(encoding='utf-8')
    t=re.sub(r'superapp\.js\?v=[^"\']+',f'superapp.js?v={VER}',s)
    t=re.sub(r'voice-ai\.js\?v=[^"\']+',f'voice-ai.js?v={VER}',t)
    if t!=s:
        p.write_text(t,encoding='utf-8')
        changed.append(p.name)
print('R54C cache bust changed',len(changed),changed)
if 'index.html' not in changed and VER not in Path('index.html').read_text(encoding='utf-8'):
    raise SystemExit('index cache bust not applied')
