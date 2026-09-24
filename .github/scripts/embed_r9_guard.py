from pathlib import Path
import re

VER='20260924-final-r9b'
guard=Path('locale-guard-r9.js').read_text(encoding='utf-8')
p=Path('i18n-ui.js')
s=p.read_text(encoding='utf-8')
marker='/* SEEKVERA R9 visible-UI locale guard */'
if marker not in s:
    s=guard+'\n\n'+s
p.write_text(s,encoding='utf-8')

count=0
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    s=p.read_text(encoding='utf-8')
    if 'i18n-ui.js' not in s: continue
    # Remove the separate R9 guard reference: the same code is now embedded in the established i18n asset.
    s=re.sub(r'\s*<script\s+src=["\']locale-guard-r9\.js(?:\?v=[^"\']+)?["\'][^>]*></script>\s*','\n',s,flags=re.I)
    # Cache-bust the established i18n asset so installed/mobile browsers fetch R9b.
    s=re.sub(r'i18n-ui\.js\?v=[^"\']+','i18n-ui.js?v='+VER,s)
    # Keep natural mobile voice cache-busted too.
    s=re.sub(r'voice-ai\.js\?v=[^"\']+','voice-ai.js?v='+VER,s)
    p.write_text(s,encoding='utf-8')
    count+=1
assert count>=44,count
assert marker in Path('i18n-ui.js').read_text(encoding='utf-8')
assert 'VOICE_SILENCE_MS=3200' in Path('voice-ai.js').read_text(encoding='utf-8')
print('Embedded R9 guard in i18n; pages updated:',count)
