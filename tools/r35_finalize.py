from pathlib import Path
import re
VER='20260925-r35-global-final'
changed=[]

def write(path,text):
    p=Path(path);old=p.read_text(encoding='utf-8')
    if old!=text:p.write_text(text,encoding='utf-8');changed.append(path)

# The R32 patchers build the deterministic runtime; stamp the fully parallel-audited R35 release.
p=Path('i18n-ui.js');s=p.read_text(encoding='utf-8')
s=s.replace("const VERSION='20260925-r32-global-final';",f"const VERSION='{VER}';",1)
s=s.replace('20260925-r32-static-v4','20260925-r35-static-v1')
s=s.replace('20260925-r32-static-v3','20260925-r35-static-v1')
write('i18n-ui.js',s)

p=Path('locale-r15.js');s=p.read_text(encoding='utf-8')
s=re.sub(r"version:'20260925-r32-global-final'",f"version:'{VER}'",s,count=1)
write('locale-r15.js',s)

p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
s=s.replace("h.set('x-seekvera-release','r32-global-final')","h.set('x-seekvera-release','r35-global-final')")
s=s.replace("r32Runtime:'248-country-full-ui-language-lock-global-final'","r32Runtime:'248-country-full-ui-language-lock-global-final',r35:true,r35Runtime:'parallel-static-98-language-country-category-final'")
s=s.replace("2026-09-25 · R32","2026-09-25 · R35")
write('worker-r31.js',s)

p=Path('sw.js');s=p.read_text(encoding='utf-8')
s=re.sub(r"const CACHE='[^']+'", "const CACHE='seekvera-r35-global-final-20260925'",s,count=1)
write('sw.js',s)

for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    s=p.read_text(encoding='utf-8');before=s
    s=re.sub(r'i18n-ui\.js\?v=[^\"\']+',f'i18n-ui.js?v={VER}',s)
    s=re.sub(r'sw\.js\?v=[^\"\']+',f'sw.js?v={VER}',s)
    s=s.replace('2026-09-25 · R32','2026-09-25 · R35')
    if s!=before:p.write_text(s,encoding='utf-8');changed.append(p.name)
print('R35 FINALIZED',len(changed),'files')
for x in changed:print(x)
