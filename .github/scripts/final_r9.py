from pathlib import Path
import re

VER='20260924-final-r9'

# Voice: 3.2s natural silence; on phones use recorder + silence detector to avoid WebSpeech premature cuts.
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=s.replace('VOICE_SILENCE_MS=2100','VOICE_SILENCE_MS=3200')
s=s.replace("if(!SpeechRecognition){serverVoice(targetId,activeButton);return}","if(!SpeechRecognition||/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)){serverVoice(targetId,activeButton);return}")
p.write_text(s,encoding='utf-8')

# Keep the R8 patch generator aligned so a later rerun cannot roll voice back.
p=Path('.github/scripts/az_quality_r8.py')
s=p.read_text(encoding='utf-8').replace('VOICE_SILENCE_MS=2100','VOICE_SILENCE_MS=3200')
p.write_text(s,encoding='utf-8')

# Deploy/audit checks must validate the new silence behavior.
for fn in ['.github/workflows/deploy-cloudflare.yml','.github/workflows/az-quality-r8.yml']:
    p=Path(fn); s=p.read_text(encoding='utf-8').replace('VOICE_SILENCE_MS=2100','VOICE_SILENCE_MS=3200'); p.write_text(s,encoding='utf-8')

# Inject R9 locale guard BEFORE legacy i18n on every public HTML page and bust voice cache.
count=0
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):
        continue
    s=p.read_text(encoding='utf-8')
    if 'i18n-ui.js' not in s:
        continue
    if 'locale-guard-r9.js' not in s:
        # preserve whatever i18n query string/attributes the page already uses
        m=re.search(r'<script\s+src=["\']i18n-ui\.js[^>]*></script>',s,re.I)
        if not m:
            raise SystemExit(f'No i18n script tag anchor in {p}')
        guard=f'<script src="locale-guard-r9.js?v={VER}" defer></script>\n'
        s=s[:m.start()]+guard+s[m.start():]
    s=re.sub(r'voice-ai\.js\?v=[^"\']+','voice-ai.js?v='+VER,s)
    p.write_text(s,encoding='utf-8')
    count+=1

# Validation: public pages share the guard; home visible English strings are covered by quick Arabic map.
assert count >= 44, count
home=Path('index.html').read_text(encoding='utf-8')
assert 'locale-guard-r9.js?v='+VER in home
assert home.index('locale-guard-r9.js') < home.index('i18n-ui.js')
for required in ['AI & Search','Flights','Find it faster. Compare it better.','Choose a country once and SEEKVERA switches']:
    assert required in home, required

guard=Path('locale-guard-r9.js').read_text(encoding='utf-8')
for required in ["'AI & Search':'الذكاء والبحث'","'Flights':'الرحلات الجوية'","'Find it faster. Compare it better.':'اعثر عليه أسرع. قارنه بشكل أفضل.'"]:
    assert required in guard, required
print('R9 patched pages:',count)
