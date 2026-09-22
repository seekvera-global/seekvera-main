from pathlib import Path
import re

VERSION='20260922-i18n-premium2'
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
print('Updated multilingual premium runtime on',len(htmls),'HTML pages')
