from pathlib import Path
import re

VER='20260929-r121b-global-intent-language'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')

# Repair the accidental literal backslash-n inserted between the Jobs and Travel rules.
s=s.replace("/iu],\\n ['travel'", "/iu],\n ['travel'", 1)
if "\\n ['travel'" in s:
    raise SystemExit('R121B literal newline token still present')

# Promote the repaired release marker and expose a health flag.
s=re.sub(r"const RELEASE='[^']+'", f"const RELEASE='{VER}'", s, count=1)
if 'r121b:true' not in s:
    marker="r121:true,r121Runtime:'global-command-inflections-and-fast-language-detection'"
    if marker not in s:
        raise SystemExit('R121B health marker anchor missing')
    s=s.replace(marker, "r121b:true,r121bRuntime:'repaired-global-command-inflections-and-language-detection',"+marker, 1)

p.write_text(s, encoding='utf-8')
print('R121B syntax repaired')
