from pathlib import Path
p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8')
old="const language=langName(b.language,m),cat=category(hist.map(x=>x.content).join(' ')+' '+m),market=clean(b.country,100)||'Worldwide';"
new="const language=langName(b.language,m),hinted=clean(b.conversationIntent,30),cat=ROUTE[hinted]?hinted:category(hist.map(x=>x.content).join(' ')+' '+m),market=clean(b.country,100)||'Worldwide';"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R56B smartAI context anchor missing')
s=s.replace("Absolutely. Open the Jobs section from the direct button below, then tell me the country/city and job type so I can narrow the results.","Absolutely. I’m taking you directly to Jobs now. Tell me the country/city and job type there and I’ll narrow the results.")
s=s.replace("أكيد. افتح قسم الوظائف من الزر المباشر تحت الرد، وقل لي البلد أو المدينة ونوع الشغل الذي تريده حتى أضيّق لك النتائج.","أكيد. سأفتح لك قسم الوظائف مباشرة الآن. قل لي هناك البلد أو المدينة ونوع الشغل الذي تريده حتى أضيّق لك النتائج.")
s=s.replace("For a clear category request, tell the user the direct section button is available and move the conversation forward.","For a clear category request, say you are taking the user directly to the matching SEEKVERA section and continue the conversation there. Do not tell the user to press a section button.")
p.write_text(s,encoding='utf-8')
print('R56B worker context + direct navigation language patched')
