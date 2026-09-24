from pathlib import Path
p=Path('tools/r16_ai_final_patch.py')
s=p.read_text(encoding='utf-8')
old="s2, n = pat.subn(new_cmd, s, count=1)"
new="s2, n = pat.subn(lambda _m: new_cmd, s, count=1)"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('R16 bootstrap anchor missing')
p.write_text(s,encoding='utf-8')
print('R16 patch bootstrap fixed regex replacement')