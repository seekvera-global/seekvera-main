from pathlib import Path
import re

VERSION='20260922-final-r3'
PROD_HOST_EXPR="HOST==='seekveraglobal.com'||HOST==='www.seekveraglobal.com'||HOST.endsWith('workers.dev')"

# On the official custom domain, call /api/* on the same origin. This avoids
# WebKit/iPhone CORS failures while retaining the workers.dev fallback for
# GitHub Pages and other preview origins.
i18n=Path('i18n-ui.js')
s=i18n.read_text(encoding='utf-8')
old="const WORKER=location.hostname.endsWith('workers.dev')?'':'https://seekvera-main.seekvera-global.workers.dev';"
new=f"const HOST=location.hostname;const WORKER=({PROD_HOST_EXPR})?'':'https://seekvera-main.seekvera-global.workers.dev';"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('i18n-ui.js API base pattern not found')
i18n.write_text(s,encoding='utf-8')

global_ui=Path('global-ui.js')
s=global_ui.read_text(encoding='utf-8')
old="const W=location.hostname.endsWith('workers.dev')?'':'https://seekvera-main.seekvera-global.workers.dev';const api=p=>`${W}${p}`;"
new=f"const HOST=location.hostname;const W=({PROD_HOST_EXPR})?'':'https://seekvera-main.seekvera-global.workers.dev';const api=p=>`${{W}}${{p}}`;"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('global-ui.js API base pattern not found')
global_ui.write_text(s,encoding='utf-8')

htmls=[p for p in Path('.').glob('*.html') if not p.name.lower().startswith('google')]
for p in htmls:
    s=p.read_text(encoding='utf-8')
    s=re.sub(r'\n?<link rel="stylesheet" href="i18n-premium\.css\?v=[^"]+">','',s)
    s=re.sub(r'\n?<script src="i18n-ui\.js\?v=[^"]+" defer></script>','',s)
    if '</head>' not in s or '</body>' not in s:
        raise SystemExit(f'Invalid HTML shell: {p}')
    s=s.replace('</head>',f'<link rel="stylesheet" href="i18n-premium.css?v={VERSION}">\n</head>',1)
    s=s.replace('</body>',f'<script src="i18n-ui.js?v={VERSION}" defer></script>\n</body>',1)
    s=re.sub(r'global-ui\.js\?v=[^"\']+',f'global-ui.js?v={VERSION}',s)
    s=re.sub(r'global-ui\.css\?v=[^"\']+',f'global-ui.css?v={VERSION}',s)
    s=re.sub(r'voice-ai\.js\?v=[^"\']+',f'voice-ai.js?v={VERSION}',s)
    p.write_text(s,encoding='utf-8')
print('Updated multilingual final R3 runtime on',len(htmls),'HTML pages with same-origin production APIs')
