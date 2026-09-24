from pathlib import Path
import re

changed=[]
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):
        continue
    s=p.read_text(encoding='utf-8')
    t=s
    t=re.sub(r'i18n-ui\.js\?v=[^"\']+', 'i18n-ui.js?v=20260924-r12', t)
    t=re.sub(r'navigation\.js\?v=[^"\']+', 'navigation.js?v=20260924-r12', t)
    t=re.sub(r'sw\.js\?v=[^"\']+', 'sw.js?v=20260924-r11', t)
    t=t.replace('Release 2026‑09‑23', 'Release 2026‑09‑24')
    t=t.replace('Release 2026-09-23', 'Release 2026-09-24')
    if t!=s:
        p.write_text(t,encoding='utf-8')
        changed.append(p.name)

if len(changed)<40:
    raise SystemExit(f'Expected >=40 public HTML pages updated, got {len(changed)}')
print('R12 cache refresh updated',len(changed),'HTML pages')
