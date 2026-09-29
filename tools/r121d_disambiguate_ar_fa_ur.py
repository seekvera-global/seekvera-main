from pathlib import Path
import re

VER='20260929-r121d-ar-fa-ur-disambiguation'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,count=1)
old="if(/[پچژگ]/u.test(t)||/(?:برای|پیدا|بگرد|می.?خواهم|میخوام|لطفاً|لطفا|شغل|کار)/u.test(s))return'fa';"
new="if(/[پچژگک]/u.test(t)||/(?:برای|پیدا|بگرد|می.?خواهم|میخوام)/u.test(s))return'fa';"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R121D Persian detector anchor missing')
if 'r121d:true' not in s:
    marker="r121c:true,r121cRuntime:'persian-urdu-arabic-script-command-routing'"
    if marker not in s:raise SystemExit('R121D health anchor missing')
    s=s.replace(marker,"r121d:true,r121dRuntime:'arabic-persian-urdu-disambiguation',"+marker,1)
p.write_text(s,encoding='utf-8')
print('R121D Arabic/Persian/Urdu disambiguation patched')
