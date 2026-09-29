from pathlib import Path
import re

VER='20260929-r121e-urdu-persian-disambiguation'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,count=1)
old=""" if(/[پچژگک]/u.test(t)||/(?:برای|پیدا|بگرد|می.?خواهم|میخوام)/u.test(s))return'fa';
 if(/[ٹڈڑںھۓے]/u.test(t)||/(?:میرے|لیے|نوکری|ملازمت|ڈھونڈ|دکھاؤ|چاہیے|کرو)/u.test(s))return'ur';"""
new=""" if(/[ٹڈڑںھۓے]/u.test(t)||/(?:میرے|لیے|نوکری|ملازمت|ڈھونڈ|دکھاؤ|چاہیے|کرو)/u.test(s))return'ur';
 if(/[پچژگ]/u.test(t)||/(?:برای|پیدا|بگرد|می.?خواهم|میخوام)/u.test(s))return'fa';"""
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R121E detector anchor missing')
if 'r121e:true' not in s:
    marker="r121d:true,r121dRuntime:'arabic-persian-urdu-disambiguation'"
    if marker not in s:raise SystemExit('R121E health anchor missing')
    s=s.replace(marker,"r121e:true,r121eRuntime:'urdu-first-persian-distinctive-detection',"+marker,1)
p.write_text(s,encoding='utf-8')
print('R121E Urdu/Persian disambiguation patched')
