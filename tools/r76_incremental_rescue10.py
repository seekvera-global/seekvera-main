from __future__ import annotations
import argparse, importlib.util, json, time, urllib.parse, urllib.request
from pathlib import Path

spec=importlib.util.spec_from_file_location('r76_rescue8',Path('tools/r76_incremental_rescue8.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def google_one_allow_shared(lang,text):
    last=None
    for client,host in [('at','translate.google.com'),('dict-chrome-ex','clients5.google.com'),('gtx','translate.googleapis.com')]:
        for attempt in range(4):
            try:
                q=urllib.parse.urlencode({'client':client,'sl':'en','tl':lang,'dt':'t','q':text});path='/translate_a/t' if host=='clients5.google.com' else '/translate_a/single'
                req=urllib.request.Request('https://'+host+path+'?'+q,headers={'User-Agent':'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'})
                d=json.loads(urllib.request.urlopen(req,timeout=25).read().decode('utf-8','replace'))
                out=m.clean(d[0] if host=='clients5.google.com' and isinstance(d,list) and d else ''.join(str(x[0] or '') for x in (d[0] if isinstance(d,list) and d else []) if isinstance(x,list)))
                if not out:raise RuntimeError('Google empty')
                return out
            except Exception as e:last=e;time.sleep(.8*(attempt+1))
    raise RuntimeError(f'Google failed {lang}: {last!r}')

def mymemory_one_allow_shared(lang,text):
    last=None
    for attempt in range(6):
        try:
            u='https://api.mymemory.translated.net/get?'+urllib.parse.urlencode({'q':text,'langpair':'en|'+lang})
            req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 SEEKVERA-R76'})
            d=json.loads(urllib.request.urlopen(req,timeout=25).read().decode('utf-8','replace'))
            out=m.clean((d.get('responseData') or {}).get('translatedText'))
            if not out:raise RuntimeError('MyMemory empty')
            return out
        except Exception as e:last=e;time.sleep(1.2*(attempt+1))
    raise RuntimeError(f'MyMemory failed {lang}: {last!r}')

m.google_one=google_one_allow_shared
m.mymemory_one=mymemory_one_allow_shared

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();m.build(a.lang)
