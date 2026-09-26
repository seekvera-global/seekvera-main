from __future__ import annotations
from pathlib import Path
import argparse, importlib.util, json, re, time, urllib.parse, urllib.request

VER='20260926-r76-complete-global-final'
CACHE=Path('/tmp/r76-lingva-cache.json')
INSTANCES=[
    'https://lingva.ml',
    'https://translate.jae.fi',
    'https://translate.projectsegfau.lt',
    'https://translate.dr460nf1r3.org',
    'https://lingva.garudalinux.org',
    'https://translate.plausibility.cloud',
]

def load_builder():
    spec=importlib.util.spec_from_file_location('r76_builder',Path('tools/r76_build_pack.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def load_cache():
    try:return json.loads(CACHE.read_text(encoding='utf-8'))
    except Exception:return {}

def save_cache(d):
    CACHE.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

def clean_result(v:str)->str:
    v=str(v or '').strip()
    if len(v)>=2 and v[0]==v[-1] and v[0] in ('"',"'"):
        v=v[1:-1].strip()
    return v

def lingva_one(b,lang,text,cache):
    key=lang+'\0'+text
    if key in cache:
        return cache[key],'lingva-cache'
    q=urllib.parse.quote(text,safe='')
    start=abs(hash(key))%len(INSTANCES)
    errs=[]
    for off in range(len(INSTANCES)):
        base=INSTANCES[(start+off)%len(INSTANCES)]
        url=f'{base}/api/v1/en/{urllib.parse.quote(lang,safe="")}/{q}'
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 SEEKVERA-R76/1.0','Accept':'application/json'})
            with urllib.request.urlopen(req,timeout=12) as r:
                data=json.loads(r.read().decode('utf-8','replace'))
            v=clean_result(data.get('translation'))
            if v and b.translation_sane(text,v):
                cache[key]=v;save_cache(cache)
                return v,'lingva:'+urllib.parse.urlparse(base).netloc
            errs.append((base,'bad-result'))
        except Exception as e:
            errs.append((base,repr(e)[:120]))
    raise RuntimeError(f'lingva failed {lang}: {errs[-3:]}')

def app_ai_one(b,lang,text):
    # Last-resort translation through SEEKVERA's own server-side AI. This avoids
    # leaving a visible English fallback when public translation relays are down.
    target=b.lang_name(lang)
    prompt=(f'Translate this SEEKVERA interface text from English into {target} ({lang}). '
            'Return ONLY the translated text, with the same meaning, punctuation, numbers, URLs and brand name SEEKVERA. '
            'Do not explain. Text: '+text)
    body=json.dumps({'message':prompt,'country':'Worldwide','language':lang,'scope':'worldwide','fast':True},ensure_ascii=False).encode('utf-8')
    req=urllib.request.Request('https://seekveraglobal.com/api/ai',data=body,headers={'Content-Type':'application/json','User-Agent':'SEEKVERA-R76-TRANSLATE'},method='POST')
    with urllib.request.urlopen(req,timeout=30) as r:data=json.loads(r.read().decode('utf-8','replace'))
    v=clean_result(data.get('response') or data.get('reply') or data.get('answer'))
    if not v or not b.translation_sane(text,v):raise RuntimeError(f'app-ai bad translation {lang}: {v[:120]!r}')
    return v,'seekvera-ai'

def translate_missing(b,lang,items):
    cache=load_cache();out=[];providers=[]
    for i,s in enumerate(items,1):
        try:v,p=lingva_one(b,lang,s,cache)
        except Exception as e:
            print('R76_LINGVA_FALLBACK',lang,i,len(items),repr(e),flush=True)
            v,p=app_ai_one(b,lang,s)
        out.append(v);providers.append(p)
        if i%10==0 or i==len(items):print('R76_TRANSLATED',lang,i,'of',len(items),p,flush=True)
        time.sleep(.10)
    return out,'+'.join(dict.fromkeys(providers))

def looks_like_real_english_phrase(s:str)->bool:
    words=re.findall(r"[A-Za-z][A-Za-z'’+-]{2,}",str(s))
    return len(words)>=2 and len(str(s).strip())>=10

def build(lang:str):
    b=load_builder();src=json.loads(Path('i18n-r76-source.json').read_text(encoding='utf-8'));strings=src['strings']
    oldp=Path('i18n-r32')/(lang+'.json')
    old=json.loads(oldp.read_text(encoding='utf-8')) if oldp.exists() else {'translations':{}}
    oldt=old.get('translations') or {}
    translations={s:str(oldt.get(s,'')).strip() for s in strings if str(oldt.get(s,'')).strip()}
    missing=[s for s in strings if s not in translations]
    print('R76_RESCUE4',lang,'reused',len(translations),'new',len(missing),'total',len(strings),flush=True)
    providers=['old-pack']
    if lang=='en':
        for s in missing:translations[s]=s
    else:
        vals,provider=translate_missing(b,lang,missing);providers.append(provider)
        assert len(vals)==len(missing),(lang,len(vals),len(missing))
        for s,v in zip(missing,vals):
            v=clean_result(v)
            if not v or not b.translation_sane(s,v):raise RuntimeError(f'{lang}: bad new translation {s!r}')
            translations[s]=v

        # Correct only genuine unchanged multi-word English UI phrases. Cognates
        # such as Contact/Hotel/Radio are valid and are not treated as failures.
        retry=[s for s in b.FORCE_UI if s in translations and looks_like_real_english_phrase(s) and b.clean_text(translations[s])==b.clean_text(s)]
        if retry:
            vals2,provider2=translate_missing(b,lang,retry);providers.append(provider2)
            for s,v in zip(retry,vals2):
                v=clean_result(v)
                if v and b.translation_sane(s,v):translations[s]=v

    assert len(translations)==src['count']==len(strings),(lang,len(translations),src['count'])
    payload={'version':VER,'sourceHash':src['sourceHash'],'language':lang,'count':src['count'],'provider':'+'.join(dict.fromkeys(providers)),'translations':translations}
    out=Path('i18n-r76');out.mkdir(exist_ok=True)
    (out/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('R76_RESCUE4_PASS',lang,len(translations),payload['provider'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();build(a.lang)
