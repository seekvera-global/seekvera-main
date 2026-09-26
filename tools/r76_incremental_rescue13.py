from __future__ import annotations
import argparse, importlib.util, re, time, urllib.parse, urllib.request, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

spec=importlib.util.spec_from_file_location('r76_rescue8',Path('tools/r76_incremental_rescue8.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old_validate=m.validate_new

# Bing's anonymous translator endpoint can revoke sessions with HTTP 401.
# Use the already verified Google multi-host fallback for all former Bing languages.
m.BING_LANGS=set()
m.GOOGLE_LANGS={'fr','it','nl','ro','to','fy','xh','tn','kl'}

def google_repair(lang,text):
    last=None
    hosts=[('translate.google.com','at','/translate_a/single'),('clients5.google.com','dict-chrome-ex','/translate_a/t'),('translate.googleapis.com','gtx','/translate_a/single')]
    for host,client,path in hosts:
        for attempt in range(3):
            try:
                q=urllib.parse.urlencode({'client':client,'sl':'en','tl':lang,'dt':'t','q':text})
                req=urllib.request.Request('https://'+host+path+'?'+q,headers={'User-Agent':'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'})
                d=json.loads(urllib.request.urlopen(req,timeout=15).read().decode('utf-8','replace'))
                out=m.clean(d[0] if host=='clients5.google.com' and isinstance(d,list) and d else ''.join(str(x[0] or '') for x in (d[0] if isinstance(d,list) and d else []) if isinstance(x,list)))
                if out:return out
            except Exception as e:
                last=e;time.sleep(.35*(attempt+1))
    raise RuntimeError(f'Google repair failed {lang}: {last!r}')

def visible_phrase(s):
    t=str(s or '').strip()
    if not t:return False
    # CSS/JS fragments were captured by older source extraction but are not visible UI text.
    # Do not spend translation time on them and never mutate syntax that the app may depend on.
    if any(x in t for x in ('{','}','!important','=>','document.','window.','html.','#categories','.r5-','.sv-','overflow:','transition:','animation:','font-weight:','min-width:','max-width:','word-break:')):return False
    if re.search(r'https?://|^[.#][A-Za-z0-9_-]+|[A-Za-z0-9_-]+\([^)]*\)\s*\{',t):return False
    return True

def validate_with_repair(builder,lang,srcs,vals):
    jobs=[]
    for i,(s,v) in enumerate(zip(srcs,vals)):
        words=re.findall(r"[A-Za-z][A-Za-z'’+-]{2,}",str(s))
        if visible_phrase(s) and len(words)>=2 and len(str(s).strip())>=10 and builder.clean_text(s)==builder.clean_text(v):
            jobs.append((i,s))
    repaired=0
    if jobs:
        # Repair independent unchanged phrases concurrently. This keeps full leakage checks
        # while avoiding several minutes of serial network waits on a small tail of phrases.
        with ThreadPoolExecutor(max_workers=3) as ex:
            futs={ex.submit(google_repair,lang,s):(i,s) for i,s in jobs}
            for f in as_completed(futs):
                i,s=futs[f]
                try:
                    x=f.result()
                    if builder.clean_text(x) and builder.clean_text(x)!=builder.clean_text(s):
                        vals[i]=x;repaired+=1;print('R76_REPAIR_UNCHANGED',lang,repr(s),'=>',repr(x),flush=True)
                except Exception as e:
                    print('R76_REPAIR_SKIP',lang,repr(s),repr(e),flush=True)
    print('R76_REPAIRED_COUNT',lang,repaired,'candidates',len(jobs),flush=True)
    return old_validate(builder,lang,srcs,vals)

m.validate_new=validate_with_repair

# Allow legitimate unchanged proper names/loan words from primary providers; pack-level
# validation above repairs real multi-word English phrases before enforcing leakage limits.
def mymemory_allow(lang,text):
    last=None
    for attempt in range(5):
        try:
            u='https://api.mymemory.translated.net/get?'+urllib.parse.urlencode({'q':text,'langpair':'en|'+lang})
            req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 SEEKVERA-R76'})
            d=json.loads(urllib.request.urlopen(req,timeout=15).read().decode('utf-8','replace'))
            out=m.clean((d.get('responseData') or {}).get('translatedText'))
            if out:return out
            raise RuntimeError('empty')
        except Exception as e:
            last=e;time.sleep(.7*(attempt+1))
    raise RuntimeError(f'MyMemory failed {lang}: {last!r}')

def google_allow(lang,text):
    return google_repair(lang,text)

m.mymemory_one=mymemory_allow
m.google_one=google_allow

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();m.build(a.lang)
