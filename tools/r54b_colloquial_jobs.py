from pathlib import Path

# Client-side instant routing: understand colloquial Arabic/Lebanese job wording.
p=Path('superapp.js')
s=p.read_text(encoding='utf-8')
old="jobs:['job','jobs','career','vacancy','work','وظيفة','عمل','工作']"
new="jobs:['job','jobs','career','vacancy','work','employment','hiring','وظيفة','وظائف','وظايف','عمل','شغل','فرصة عمل','دوام','工作']"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('superapp jobs keyword anchor missing')
p.write_text(s,encoding='utf-8')

# Server-side intent routing: mirror the same colloquial coverage.
p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8')
old="['jobs',/job|career|vacancy|وظيفة|عمل/u]"
new="['jobs',/job|career|vacancy|work|employment|hiring|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام/u]"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('worker jobs regex anchor missing')
p.write_text(s,encoding='utf-8')
print('R54B colloquial jobs intent PASS')
