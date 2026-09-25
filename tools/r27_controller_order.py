from pathlib import Path

old='<script src="r24-ai-controller.js?v=20260925-r24-control1" data-no-i18n="1"></script>'
new='<script src="r24-ai-controller.js?v=20260925-r24-control1" data-no-i18n="1" defer></script>'
changed=[]
for p in sorted(Path('.').glob('*.html')):
    if p.name.lower().startswith('google'): continue
    s=p.read_text(encoding='utf-8')
    if old in s:
        p.write_text(s.replace(old,new),encoding='utf-8');changed.append(p.name)

# Keep the source patcher idempotent for future releases.
p=Path('tools/r24_finish.py')
s=p.read_text(encoding='utf-8')
s=s.replace("tag='<script src=\"r24-ai-controller.js?v=20260925-r24-control1\" data-no-i18n=\"1\"></script>'","tag='<script src=\"r24-ai-controller.js?v=20260925-r24-control1\" data-no-i18n=\"1\" defer></script>'")
p.write_text(s,encoding='utf-8')

pages=[]
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    s=p.read_text(encoding='utf-8')
    if '</body>' not in s.lower():continue
    pages.append(p.name)
    assert new in s,p.name
assert len(pages)==44,len(pages)
assert "data-no-i18n=\"1\" defer" in Path('tools/r24_finish.py').read_text(encoding='utf-8')
print('R27 controller load-order PASS:',len(changed),'pages changed; 44/44 defer-last controller')
