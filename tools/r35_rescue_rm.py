from __future__ import annotations
from pathlib import Path
import concurrent.futures,json,re,sys,time,urllib.request
from r35_build_pack import source_meta, FORCE_UI, clean_text

OUT=Path('i18n-r35'); OUT.mkdir(exist_ok=True)
VERSION='20260925-r35-static-v3'
BASE='https://seekveraglobal.com'
CODE=(sys.argv[1] if len(sys.argv)>1 else 'rm').lower()
NAMES={'rm':'Romansh (Rumantsch)','tn':'Tswana (Setswana)'}
if CODE not in NAMES: raise SystemExit('Rescue supports rm or tn')
LANG=NAMES[CODE]

MANUALS={
'rm':{
'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'Actualmain na datti naginas glistas approvadas e disponiblas sin il martgà. SEEKVERA na generescha betg glistas faussas.',
'No approved live marketplace listings are available right now.':'Actualmain na datti naginas glistas approvadas e disponiblas sin il martgà.',
'SEEKVERA does not generate fake listings.':'SEEKVERA na generescha betg glistas faussas.',
'Find, compare, choose — worldwide.':'Tschertga, cumpareglia, tscherna — en tut il mund.',
'Find, compare, choose — worldwide':'Tschertga, cumpareglia, tscherna — en tut il mund',
'Popular categories':'Categorias popularas','Live marketplace':'Martgà actual','Request anything':'Dumonda tut',
'Privacy':'Protecziun da datas','Terms':'Cundiziuns','Contact':'Contact','Disclosure':'Decleraziun',
'Approved real listings only.':'Mo glistas realas approvadas.','Loading approved listings…':'Chargiar glistas approvadas…'},
'tn':{
'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'Ga go na mananeo a a amogetsweng a mmaraka a a leng teng gone jaanong. SEEKVERA ga e dire mananeo a maaka.',
'No approved live marketplace listings are available right now.':'Ga go na mananeo a a amogetsweng a mmaraka a a leng teng gone jaanong.',
'SEEKVERA does not generate fake listings.':'SEEKVERA ga e dire mananeo a maaka.',
'Find, compare, choose — worldwide.':'Batla, bapisa, tlhopha — lefatshe ka bophara.',
'Find, compare, choose — worldwide':'Batla, bapisa, tlhopha — lefatshe ka bophara',
'Popular categories':'Dikarolo tse di tumileng','Live marketplace':'Mmaraka o o dirang','Request anything':'Kopa sengwe le sengwe',
'Privacy':'Bosephiri','Terms':'Melawana','Contact':'Ikgolaganye','Disclosure':'Tshedimosetso',
'Approved real listings only.':'Mananeo a nnete a a amogetsweng fela.','Loading approved listings…':'Go tsenngwa mananeo a a amogetsweng…'}
}
MANUAL=MANUALS[CODE]

def post(path,payload,timeout=75):
    data=json.dumps(payload,ensure_ascii=False).encode('utf-8')
    req=urllib.request.Request(BASE+path,data=data,headers={'Content-Type':'application/json','Accept':'application/json','Origin':BASE,'Referer':BASE+'/','User-Agent':'SEEKVERA-R35-Missing-Pack-Rescue/2.0'})
    with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read().decode('utf-8'))

def ui_batch(batch):
    last=None
    for a in range(5):
        try:
            d=post('/api/ui-translate',{'language':LANG,'strings':batch})
            vals=d.get('translations') if isinstance(d,dict) else None
            if d.get('ok') and isinstance(vals,list) and len(vals)==len(batch) and all(str(x).strip() for x in vals):return [clean_text(x) for x in vals]
            last=RuntimeError(repr(d)[:500])
        except Exception as e:last=e
        time.sleep(1+a*1.3)
    raise RuntimeError(f'ui batch failed: {last!r}')

def ai_one(s):
    if s in MANUAL:return MANUAL[s]
    last=None
    prompt=(f'Translate this SEEKVERA website interface text from English into natural {LANG}. Return ONLY the translated text, no explanation and no quotation marks. Preserve SEEKVERA, URLs, numbers and currency codes exactly.\nTEXT: '+s)
    for a in range(4):
        try:
            d=post('/api/ai',{'fast':True,'language':CODE,'country':'Worldwide','message':prompt})
            v=clean_text(d.get('response','')) if isinstance(d,dict) else ''
            v=v.strip(" \t\r\n\"'“”‘’")
            if v and v!=s:return v
            last=RuntimeError(repr(d)[:400])
        except Exception as e:last=e
        time.sleep(1+a)
    if len(s)<18 and len(re.findall(r'[A-Za-z]+',s))<=2:return MANUAL.get(s,s)
    raise RuntimeError(f'ai single failed {CODE} {s!r}: {last!r}')

def translate(batch):
    if not batch:return []
    if len(batch)==1 and batch[0] in MANUAL:return [MANUAL[batch[0]]]
    try:
        vals=ui_batch(batch);out=[]
        for s,v in zip(batch,vals):
            if s in MANUAL:out.append(MANUAL[s])
            elif clean_text(v)==clean_text(s) and len(s)>=18:out.append(ai_one(s))
            else:out.append(v)
        return out
    except Exception as e:
        if len(batch)>1:
            m=len(batch)//2;print('RESCUE_SPLIT',CODE,len(batch),'->',m,len(batch)-m,repr(e),flush=True)
            return translate(batch[:m])+translate(batch[m:])
        return [ai_one(batch[0])]

def main():
    src,h=source_meta();chunks=[src[i:i+20] for i in range(0,len(src),20)];vals=[]
    print('R35 RESCUE SOURCE',CODE,len(src),h,'chunks',len(chunks),flush=True)
    done=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        for translated in ex.map(translate,chunks):
            vals.extend(translated);done+=len(translated);print('R35 RESCUE PROGRESS',CODE,done,'/',len(src),flush=True)
    assert len(vals)==len(src),(CODE,len(vals),len(src))
    trans={s:v for s,v in zip(src,vals)}
    for s,v in MANUAL.items():
        if s in trans:trans[s]=v
    failed=[s for s in FORCE_UI if s in trans and clean_text(trans[s])==clean_text(s) and not (CODE=='rm' and s=='Contact')]
    assert not failed,(CODE,failed)
    long=[s for s in src if len(s)>=14 and 'SEEKVERA' not in s and re.search(r'[A-Za-z]',s) and ' ' in s]
    same=[s for s in long if clean_text(trans.get(s,''))==clean_text(s)]
    assert len(same)<=max(25,int(len(long)*.18)),(CODE,'too many unchanged',len(same),same[:10])
    payload={'version':VERSION,'sourceHash':h,'language':CODE,'count':len(src),'provider':'seekvera-workers-ai-rescue','translations':trans}
    p=OUT/f'{CODE}.json';p.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('R35 RESCUE PACK PASS',CODE,len(src),'unchanged-long',len(same),p,flush=True)

if __name__=='__main__':main()
