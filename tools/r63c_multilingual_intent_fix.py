from pathlib import Path

terms="job|jobs|career|vacancy|work|employment|hiring|travail|emploi|emplois|trabajo|empleo|emprego|trabalho|lavoro|arbeit|stellen|stelle|iş|is ilanı|iş ilanı|работ|ваканси|工作|职位|仕事|求人|직업|채용|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام"

# Server fast/local category detector.
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
old="job|career|vacancy|work|employment|hiring|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام"
if old in s:s=s.replace(old,terms,1)
elif 'travail|emploi|emplois' not in s:raise SystemExit('R63C worker jobs intent anchor missing')
p.write_text(s,encoding='utf-8')

# Browser-side intent detector, so routing does not depend on the AI provider.
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8')
old="job|jobs|career|vacancy|work|employment|hiring|وظيفة|وظائف|وظايف|عمل|شغل|فرصة عمل|دوام"
if old in s:s=s.replace(old,terms,1)
elif 'travail|emploi|emplois' not in s:raise SystemExit('R63C browser jobs intent anchor missing')
p.write_text(s,encoding='utf-8')

print('R63C multilingual jobs intent patched')
