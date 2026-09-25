from __future__ import annotations
from pathlib import Path
from babel import Locale
import concurrent.futures, json, os, re, time, urllib.error, urllib.request

BASE=os.environ.get('SEEKVERA_BASE','https://seekveraglobal.com').rstrip('/')
OUT=Path('i18n-r35');OUT.mkdir(exist_ok=True)
source=json.load(open('i18n-r35-source.json',encoding='utf-8'))
langs=json.load(open('i18n-r35-languages.json',encoding='utf-8'))
strings=source['strings']; source_hash=source['sourceHash']

def lang_name(code):
    aliases={'fil':'Filipino','he':'Hebrew','zh':'Chinese','tn':'Tswana','to':'Tongan','rm':'Romansh','dv':'Divehi','dz':'Dzongkha'}
    if code in aliases:return aliases[code]
    try:return Locale.parse(code).get_display_name('en')
    except Exception:return code

def post(language,batch,timeout=45):
    data=json.dumps({'language':language,'strings':batch},ensure_ascii=False).encode()
    req=urllib.request.Request(BASE+'/api/ui-translate',data=data,headers={'content-type':'application/json','Origin':'https://seekveraglobal.com','User-Agent':'SEEKVERA-R38-Recovery/1.0'})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        d=json.loads(r.read().decode('utf-8'))
        if r.status!=200 or not d.get('ok') or len(d.get('translations',[]))!=len(batch):raise RuntimeError(str(d)[:800])
        return [str(x).strip() for x in d['translations']]

def translate_batch(language,batch,depth=0):
    last=None
    for attempt in range(6):
        try:
            vals=post(language,batch)
            if all(vals):return vals
        except Exception as e:
            last=e; print('RECOVERY_RETRY',language,len(batch),attempt+1,repr(e),flush=True);time.sleep(min(8,.8*(attempt+1)))
    if len(batch)>1:
        mid=len(batch)//2
        return translate_batch(language,batch[:mid],depth+1)+translate_batch(language,batch[mid:],depth+1)
    raise RuntimeError(f'recovery failed {language}: {last!r}')

def build(code):
    target=OUT/f'{code}.json'
    if target.exists():return code,'existing'
    language=lang_name(code);print('RECOVER',code,language,flush=True)
    vals=[]
    for i in range(0,len(strings),20):
        b=strings[i:i+20];vals.extend(translate_batch(language,b));print('RECOVER_PROGRESS',code,min(i+20,len(strings)),'/',len(strings),flush=True)
        time.sleep(.08)
    if len(vals)!=len(strings):raise RuntimeError((code,len(vals),len(strings)))
    trans={s:v for s,v in zip(strings,vals)}
    critical='No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.'
    if code!='en' and trans.get(critical,'').strip()==critical:raise RuntimeError(f'{code}: critical text remained English')
    payload={'version':'20260925-r38-workers-ai-recovery','sourceHash':source_hash,'language':code,'count':len(strings),'provider':'seekvera-workers-ai-recovery','translations':trans}
    target.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    return code,'recovered'

missing=[c for c in langs if not (OUT/f'{c}.json').exists()]
print('RECOVERY_MISSING',missing,'count',len(missing),flush=True)
if not missing:raise SystemExit(0)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
    for result in ex.map(build,missing):print('RECOVERY_PASS',result,flush=True)
remaining=[c for c in langs if not (OUT/f'{c}.json').exists()]
if remaining:raise SystemExit('Still missing '+repr(remaining))
print('R38 ALL 98 PACK FILES PRESENT',flush=True)
