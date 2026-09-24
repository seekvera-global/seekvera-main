from pathlib import Path
import re,json,subprocess
for f in ['locale-r15.js','locale-r14.js','locale-r14-categories.js','global-ui.js','i18n-ui.js','navigation.js','voice-ai.js','worker.js','sw.js']:
    subprocess.run(['node','--check',f],check=True)
r=Path('locale-r15.js').read_text();g=Path('global-ui.js').read_text();n=Path('navigation.js').read_text();i=Path('i18n-ui.js').read_text();a=Path('locale-r14.js').read_text();c=Path('locale-r14-categories.js').read_text();idx=Path('index.html').read_text();w=Path('worker.js').read_text();sw=Path('sw.js').read_text();v=Path('voice-ai.js').read_text()
def prof(x):
    m=re.search(r'Object\.fromEntries\(`([^`]+)`\.split',x,re.S);assert m
    return {z.split(':',1)[0]:tuple(z.split(':',1)[1].split(',',1)) for z in m.group(1).split(';') if z}
rp,gp=prof(r),prof(g);assert rp==gp and len(rp)==248
lm=re.search(r'const WORLD_LANGS=\[([^\]]+)\]',n,re.S);assert lm
langs=re.findall(r"'([^']+)'",lm.group(1));assert len(langs)==98
lp=json.loads(re.search(r'const LANG_PRIMARY=(\{[^;]+\});',r,re.S).group(1));cp=json.loads(re.search(r'const CURRENCY_PRIMARY=(\{[^;]+\});',r,re.S).group(1));assert set(lp)==set(langs) and len(cp)>=150
assert all(x[0] in lp and x[1] in cp for x in rp.values())
dl={x[0] for x in rp.values()};al=set(re.findall(r'^([a-z]{2,3}):\[',a,re.M));cl=set(re.findall(r'^([a-z]{2,3}):\[',c,re.M));cl.add('en');assert dl<=al and dl<=cl
pages=[]
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    s=p.read_text();assert 'locale-r15.js?v=20260924-r15' in s,p.name;pages.append(p.name)
assert len(pages)>=44 and idx.count('id="categories"')==1 and 'r5-chips' not in idx and 'r8-department-strip' not in idx
assert 'const svLocaleControl=id=>' in g and 'const i18nLocaleControl=id=>' in i and "c=document.getElementById('country')" not in i and 'const localeControl=id=>' in n
assert "seekvera-r15-atomic-20260924" in sw and "'./locale-r15.js'" in sw and 'function locateOnce()' in r and 'startLocationTracking' in r
assert 'setTimeout(apply,80)' not in a and 'setTimeout(apply,100)' not in c and "t:k=>{const {p}=pack()" in a
assert 'speechSynthesis' in v and '/api/transcribe' in v and 'safetyGateVersion' in w and 'centralSafetyGate' in w
assert 'navigator.geolocation' in Path('wifi.html').read_text() and 'google.com/maps/search' in Path('tourism.html').read_text()
print('STATIC R15 PASS:',len(rp),'countries;',len(langs),'languages;',len(cp),'currencies;',len(pages),'pages')
