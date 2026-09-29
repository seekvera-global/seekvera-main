from pathlib import Path
import runpy

p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
old="const strongHint=nativeFamily&&nativeFamily!=='latin'?nativeLang:(nativeText&&nativeConfidence>=.60?softHint:'');"
new="const strongHint=nativeFamily&&nativeFamily!=='latin'?nativeLang:'';"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('R119C current strongHint anchor missing')
p.write_text(s,encoding='utf-8')
runpy.run_path('tools/r119b_voice_intent_atomic.py',run_name='__main__')
