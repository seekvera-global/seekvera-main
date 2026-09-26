from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup
import argparse, html as htmlmod, importlib.util, json, re, time, urllib.parse, urllib.request

VER='20260926-r76-complete-global-final'
ALL={'fr','it','nl','ro','sr','kl','to','fy','rm','xh','tn'}
ALIASES={'sr':'sr','kl':'kl','rm':'rm'}

spec=importlib.util.spec_from_file_location('r76_rescue8',Path('tools/r76_incremental_rescue8.py'))
m8=importlib.util.module_from_spec(spec);spec.loader.exec_module(m8)
spec2=importlib.util.spec_from_file_location('r76_builder',Path('tools/r76_build_pack.py'))
b=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(b)

def clean(v):return re.sub(r'\s+',' ',str(v or '')).strip()
def cssish(s):
    x=str(s or '').strip()
    return ('{' in x and '}' in x and ('!important' in x or x.startswith(('.', '#','html','body')) or 'transition:' in x or 'overflow:' in x))

def google_at_raw(lang,text):
    last=None
    for host,client,path in [
        ('translate.google.com','at','/translate_a/single'),
        ('clients5.google.com','dict-chrome-ex','/translate_a/t'),
        ('translate.googleapis.com','gtx','/translate_a/single')
    ]:
      for attempt in range(4):
        try:
            q=urllib.parse.urlencode({'client':client,'sl':'en','tl':lang,'dt':'t','q':text})
            req=urllib.request.Request('https://'+host+path+'?'+q,headers={'User-Agent':'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36','Accept-Language':'en-US,en;q=0.9'})
            raw=urllib.request.urlopen(req,timeout=35).read().decode('utf-8','replace');d=json.loads(raw)
            if host=='clients5.google.com':
                out=d[0] if isinstance(d,list) and d else ''
            else:
                out=''.join(str(x[0] or '') for x in (d[0] if isinstance(d,list) and d else []) if isinstance(x,list))
            out=str(out or '').strip()
            if not out:raise RuntimeError('empty output')
            return out
        except Exception as e:
            last=e;time.sleep(.8*(attempt+1))
    raise RuntimeError(f'Google AT failed {lang}: {last!r}')

def batch_translate(lang,items):
    if not items:return []
    if len(items)==1:
        return [clean(google_at_raw(lang,items[0]))]
    body='\n'.join(f'<span id="sv{i:03d}">{htmlmod.escape(s)}</span>' for i,s in enumerate(items))
    try:
        raw=google_at_raw(lang,body);soup=BeautifulSoup(raw,'html.parser');vals=[None]*len(items)
        for sp in soup.find_all('span'):
            sid=str(sp.get('id',''));mm=re.fullmatch(r'sv(\d{3})',sid,re.I)
            if mm:
                i=int(mm.group(1))
                if 0<=i<len(vals):vals[i]=clean(sp.get_text(' ',strip=True))
        if any(not x for x in vals):raise RuntimeError('missing html markers')
        for src,val in zip(items,vals):
            if not b.translation_sane(src,val):raise RuntimeError('corrupt oversized output')
        return vals
    except Exception as e:
        print('R76_AT_SPLIT',lang,len(items),repr(e),flush=True)
        mid=max(1,len(items)//2)
        return batch_translate(lang,items[:mid])+batch_translate(lang,items[mid:])

def build(lang):
    if lang not in ALL:raise RuntimeError('unsupported '+lang)
    src=json.loads(Path('i18n-r76-source.json').read_text(encoding='utf-8'));strings=src['strings']
    oldp=Path('i18n-r32')/(lang+'.json');old=json.loads(oldp.read_text(encoding='utf-8')) if oldp.exists() else {'translations':{}};oldt=old.get('translations') or {}
    trans={s:clean(oldt.get(s)) for s in strings if clean(oldt.get(s))};missing=[s for s in strings if s not in trans]
    print('R76_RESCUE12',lang,'reused',len(trans),'missing',len(missing),flush=True)
    if lang=='rm':
        absent=[s for s in missing if s not in m8.STATIC_RM]
        if absent:raise RuntimeError('Romansh static missing '+repr(absent))
        vals=[m8.STATIC_RM[s] for s in missing];provider='verified-static-rm'
    else:
        vals=[None]*len(missing);todo=[];idx=[]
        for i,s in enumerate(missing):
            if cssish(s):vals[i]=s
            else:idx.append(i);todo.append(s)
        out=[]
        for start in range(0,len(todo),20):
            chunk=todo[start:start+20];out.extend(batch_translate(lang,chunk));print('R76_AT_PROGRESS',lang,min(start+20,len(todo)),'of',len(todo),flush=True);time.sleep(.15)
        for i,v in zip(idx,out):vals[i]=v
        provider='google-at-html'
    if len(vals)!=len(missing) or any(v is None or not str(v).strip() for v in vals):raise RuntimeError(lang+' missing translated values')
    # Pack-level quality gate: unchanged proper names/loan words are fine, but not broad English leakage.
    real=[(s,clean(v)) for s,v in zip(missing,vals) if not cssish(s) and len(re.findall(r"[A-Za-z][A-Za-z'’+-]{2,}",s))>=2 and len(s)>=10]
    unchanged=[s for s,v in real if clean(s)==v]
    if len(unchanged)>max(10,int(len(real)*.22)):raise RuntimeError(f'{lang} excessive unchanged English {len(unchanged)}/{len(real)} {unchanged[:8]}')
    for s,v in zip(missing,vals):
        if not b.translation_sane(s,v):raise RuntimeError(f'{lang} corrupt translation {s!r} => {v!r}')
        trans[s]=clean(v)
    assert len(trans)==src['count']==1045,(lang,len(trans),src['count'])
    payload={'version':VER,'sourceHash':src['sourceHash'],'language':lang,'count':1045,'provider':'old-pack+'+provider,'translations':trans}
    outdir=Path('i18n-r76');outdir.mkdir(exist_ok=True);(outdir/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('R76_RESCUE12_PASS',lang,1045,payload['provider'],'unchangedMulti',len(unchanged),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();build(a.lang)
