from __future__ import annotations
from pathlib import Path
import json,re,time,urllib.request,urllib.error
from r35_build_pack import source_meta, FORCE_UI, clean_text

OUT=Path('i18n-r35'); OUT.mkdir(exist_ok=True)
VERSION='20260925-r35-static-v3'
BASE='https://seekveraglobal.com'
LANG='Romansh (Rumantsch)'

MANUAL={
'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'Actualmain na datti naginas glistas approvadas e disponiblas sin il martgà. SEEKVERA na generescha betg glistas faussas.',
'No approved live marketplace listings are available right now.':'Actualmain na datti naginas glistas approvadas e disponiblas sin il martgà.',
'SEEKVERA does not generate fake listings.':'SEEKVERA na generescha betg glistas faussas.',
'Find, compare, choose — worldwide.':'Tschertga, cumpareglia, tscherna — en tut il mund.',
'Find, compare, choose — worldwide':'Tschertga, cumpareglia, tscherna — en tut il mund',
'Popular categories':'Categorias popularas',
'Live marketplace':'Martgà actual',
'Request anything':'Dumonda tut',
'Privacy':'Protecziun da datas',
'Terms':'Cundiziuns',
'Contact':'Contact',
'Disclosure':'Decleraziun',
'Approved real listings only.':'Mo glistas realas approvadas.',
'Loading approved listings…':'Chargiar glistas approvadas…',
}

def post(path,payload,timeout=75):
    data=json.dumps(payload,ensure_ascii=False).encode('utf-8')
    req=urllib.request.Request(BASE+path,data=data,headers={
        'Content-Type':'application/json','Accept':'application/json',
        'Origin':BASE,'Referer':BASE+'/','User-Agent':'SEEKVERA-R35-Romansh-Rescue/1.0'})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def ui_batch(batch):
    last=None
    for a in range(5):
        try:
            d=post('/api/ui-translate',{'language':LANG,'strings':batch})
            vals=d.get('translations') if isinstance(d,dict) else None
            if d.get('ok') and isinstance(vals,list) and len(vals)==len(batch) and all(str(x).strip() for x in vals):
                return [clean_text(x) for x in vals]
            last=RuntimeError(repr(d)[:600])
        except Exception as e:last=e
        time.sleep(1.0+a*1.4)
    raise RuntimeError(f'ui batch failed: {last!r}')

def ai_one(s):
    if s in MANUAL:return MANUAL[s]
    last=None
    prompt=('Translate the following SEEKVERA website interface text from English into natural Romansh (Rumantsch). '
            'Return ONLY the translated text, no explanation, no quotation marks. Preserve SEEKVERA, URLs, numbers and currency codes exactly.\nTEXT: '+s)
    for a in range(4):
        try:
            d=post('/api/ai',{'fast':True,'language':'rm','country':'Worldwide','message':prompt})
            v=clean_text(d.get('response','')) if isinstance(d,dict) else ''
            v=v.strip(" \t\r\n\"'“”‘’")
            if v and v!=s:return v
            last=RuntimeError(repr(d)[:500])
        except Exception as e:last=e
        time.sleep(1.0+a)
    # Legitimate short Romansh words can share English spelling (e.g. Contact).
    if len(s)<18 and len(re.findall(r'[A-Za-z]+',s))<=2:return MANUAL.get(s,s)
    raise RuntimeError(f'ai single failed for {s!r}: {last!r}')

def translate(batch):
    if not batch:return []
    if len(batch)==1 and batch[0] in MANUAL:return [MANUAL[batch[0]]]
    try:
        vals=ui_batch(batch)
        out=[]
        for s,v in zip(batch,vals):
            if s in MANUAL:out.append(MANUAL[s])
            elif clean_text(v)==clean_text(s) and len(s)>=18:out.append(ai_one(s))
            else:out.append(v)
        return out
    except Exception as e:
        if len(batch)>1:
            m=len(batch)//2
            print('RESCUE_SPLIT',len(batch),'->',m,len(batch)-m,repr(e),flush=True)
            return translate(batch[:m])+translate(batch[m:])
        return [ai_one(batch[0])]

def main():
    src,h=source_meta(); vals=[]
    print('R35 RM RESCUE SOURCE',len(src),h,flush=True)
    for i in range(0,len(src),20):
        vals.extend(translate(src[i:i+20]))
        print('R35 RM PROGRESS',min(i+20,len(src)),'/',len(src),flush=True)
    assert len(vals)==len(src),(len(vals),len(src))
    trans={s:v for s,v in zip(src,vals)}
    for s,v in MANUAL.items():
        if s in trans:trans[s]=v
    failed=[s for s in FORCE_UI if s in trans and clean_text(trans[s])==clean_text(s) and s!='Contact']
    assert not failed,failed
    long=[s for s in src if len(s)>=14 and 'SEEKVERA' not in s and re.search(r'[A-Za-z]',s) and ' ' in s]
    same=[s for s in long if clean_text(trans.get(s,''))==clean_text(s)]
    assert len(same)<=max(25,int(len(long)*.18)),('too many unchanged',len(same),same[:10])
    payload={'version':VERSION,'sourceHash':h,'language':'rm','count':len(src),'provider':'seekvera-workers-ai-rescue','translations':trans}
    p=OUT/'rm.json';p.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('R35 RM RESCUE PASS',len(src),'unchanged-long',len(same),p,flush=True)

if __name__=='__main__':main()
