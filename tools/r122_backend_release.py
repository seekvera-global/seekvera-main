from pathlib import Path
import re
VER='20260929-r122-unified-direct-routing'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,count=1)
if 'r122:true' not in s:
    marker="r121e:true,r121eRuntime:'urdu-first-persian-distinctive-detection'"
    if marker not in s: raise SystemExit('R122 health anchor missing')
    s=s.replace(marker,"r122:true,r122Runtime:'unified-home-direct-routing-and-language-independent-voice',"+marker,1)
p.write_text(s,encoding='utf-8')
print('R122 backend release marked')
