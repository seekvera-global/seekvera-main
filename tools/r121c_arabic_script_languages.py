from pathlib import Path
import re

VER='20260929-r121c-arabic-script-language-routing'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,count=1)

old=" const s=String(message||'').toLowerCase().trim();\n if(employmentIntent(message))return'jobs';"
new=""" const s=String(message||'').toLowerCase().trim();
 if(employmentIntent(message))return'jobs';
 if(/(?:کار.{0,24}(?:پیدا|بگرد)|(?:پیدا|بگرد).{0,24}کار|شغل.{0,24}(?:پیدا|بگرد)|(?:پیدا|بگرد).{0,24}شغل)/u.test(s))return'jobs';
 if(/(?:نوکری|ملازمت).{0,28}(?:تلاش|ڈھونڈ|چاہ)|(?:تلاش|ڈھونڈ).{0,28}(?:نوکری|ملازمت)/u.test(s))return'jobs';"""
if old in s:s=s.replace(old,new,1)
elif "نوکری|ملازمت" not in s:raise SystemExit('R121C direct jobs anchor missing')

old=" const t=String(message||''),s=t.toLowerCase();\n if(/[\\u0600-\\u06ff]/u.test(t))return messageLanguage(t,suggested);"
new=""" const t=String(message||''),s=t.toLowerCase();
 if(/[پچژگ]/u.test(t)||/(?:برای|پیدا|بگرد|می.?خواهم|میخوام|لطفاً|لطفا|شغل|کار)/u.test(s))return'fa';
 if(/[ٹڈڑںھۓے]/u.test(t)||/(?:میرے|لیے|نوکری|ملازمت|ڈھونڈ|دکھاؤ|چاہیے|کرو)/u.test(s))return'ur';
 if(/[ښږڅځټړ]/u.test(t))return'ps';
 if(/[ڵۆێ]/u.test(t))return'ku';
 if(/[\\u0600-\\u06ff]/u.test(t))return messageLanguage(t,suggested);"""
if old in s:s=s.replace(old,new,1)
elif "if(/[پچژگ]/u.test(t)" not in s:raise SystemExit('R121C fast language anchor missing')

if 'r121c:true' not in s:
    marker="r121b:true,r121bRuntime:'repaired-global-command-inflections-and-language-detection'"
    if marker not in s:raise SystemExit('R121C health anchor missing')
    s=s.replace(marker,"r121c:true,r121cRuntime:'persian-urdu-arabic-script-command-routing',"+marker,1)

p.write_text(s,encoding='utf-8')
print('R121C Persian/Urdu routing patched')
