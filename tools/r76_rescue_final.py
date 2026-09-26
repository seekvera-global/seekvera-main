from __future__ import annotations
from pathlib import Path
import argparse, collections, http.cookiejar, importlib.util, json, re, time, urllib.parse, urllib.request, urllib.error

VER='20260926-r76-complete-global-final'
BING_LANGS={'fr','it','nl','ro','to','fy','xh','tn'}
MYMEMORY_LANGS={'sr'}
TRANSLATEAPI_LANGS={'kl','rm'}
ALL=BING_LANGS|MYMEMORY_LANGS|TRANSLATEAPI_LANGS
BAD_FALLBACKS={
    'i understood your request. i’m taking you directly to the best matching section now.',
    "i understood your request. i'm taking you directly to the best matching section now.",
    'i’m taking you directly to the best matching section now.',
}


def load_builder():
    spec=importlib.util.spec_from_file_location('r76_builder',Path('tools/r76_build_pack.py'))
    if not spec or not spec.loader: raise RuntimeError('r76_build_pack.py loader missing')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def clean(v):
    s=str(v or '').strip()
    s=re.sub(r'^```(?:text)?\s*','',s,flags=re.I);s=re.sub(r'```$','',s).strip()
    if len(s)>=2 and s[0]==s[-1] and s[0] in ('"',"'"):s=s[1:-1].strip()
    return s


class Bing:
    def __init__(self):
        self.headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36','Accept-Language':'en-US,en;q=0.9'}
        self.calls=0;self.refresh()
    def refresh(self):
        self.cj=http.cookiejar.CookieJar();self.op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        html=self.op.open(urllib.request.Request('https://www.bing.com/translator',headers=self.headers),timeout=25).read().decode('utf-8','replace')
        igm=re.search(r'IG:"([^"]+)"',html) or re.search(r'"IG":"([^"]+)"',html)
        ab=re.search(r'params_AbusePreventionHelper\s*=\s*\[(\d+),"([^"]+)",(\d+)\]',html)
        if not igm or not ab:raise RuntimeError('Bing session markers missing')
        self.key,self.token,_=ab.groups();self.ig=igm.group(1);self.calls=0
    def one(self,lang,text):
        last=None
        for attempt in range(4):
            try:
                if self.calls>=40:self.refresh()
                data=urllib.parse.urlencode({'fromLang':'en','to':lang,'text':text,'token':self.token,'key':self.key,'tryFetchingGenderDebiasedTranslations':'true'}).encode()
                url=f'https://www.bing.com/ttranslatev3?isVertical=1&&IG={urllib.parse.quote(self.ig)}&IID=translator.5024.1'
                req=urllib.request.Request(url,data=data,headers={**self.headers,'Content-Type':'application/x-www-form-urlencoded','Referer':'https://www.bing.com/translator'},method='POST')
                raw=self.op.open(req,timeout=25).read().decode('utf-8','replace');self.calls+=1
                d=json.loads(raw)
                if not isinstance(d,list) or not d or not d[0].get('translations'):raise RuntimeError('Bing returned no translations: '+raw[:260])
                out=clean(d[0]['translations'][0].get('text'))
                if not out:raise RuntimeError('Bing empty translation')
                return out
            except Exception as e:
                last=e;time.sleep(1.1*(attempt+1));self.refresh()
        raise RuntimeError(f'Bing failed {lang}: {last!r}')


def mymemory_one(lang,text):
    last=None
    for attempt in range(4):
        try:
            u='https://api.mymemory.translated.net/get?'+urllib.parse.urlencode({'q':text,'langpair':'en|'+lang})
            req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 SEEKVERA-R76/1.0','Accept':'application/json'})
            with urllib.request.urlopen(req,timeout=25) as r:d=json.loads(r.read().decode('utf-8','replace'))
            out=clean((d.get('responseData') or {}).get('translatedText'))
            if str(d.get('responseStatus') or 200)!='200' or not out:raise RuntimeError('MyMemory response '+repr(d)[:350])
            return out
        except Exception as e:last=e;time.sleep(1.2*(attempt+1))
    raise RuntimeError(f'MyMemory failed {lang}: {last!r}')


def translateapi_one(lang,text):
    last=None
    for attempt in range(4):
        try:
            body=json.dumps({'text':text,'source_language':'en','target_languages':[lang]},ensure_ascii=False).encode('utf-8')
            req=urllib.request.Request('https://translateapi.ai/translate/',data=body,headers={'content-type':'application/json','accept':'application/json','user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36'},method='POST')
            with urllib.request.urlopen(req,timeout=45) as r:d=json.loads(r.read().decode('utf-8','replace'))
            out=clean((d.get('translations') or {}).get(lang))
            if not d.get('success') or not out:raise RuntimeError('TranslateAPI response '+repr(d)[:350])
            return out
        except urllib.error.HTTPError as e:
            raw=e.read().decode('utf-8','replace');last=RuntimeError(f'TranslateAPI HTTP {e.code}: {raw[:250]}')
            if e.code==402:raise last
            time.sleep(1.5*(attempt+1))
        except Exception as e:last=e;time.sleep(1.5*(attempt+1))
    raise RuntimeError(f'TranslateAPI failed {lang}: {last!r}')


def fallback_translate(lang,text,bing=None):
    # Verified provider order. TranslateAPI is the only verified anonymous engine
    # for Kalaallisut/Romansh; Serbian has MyMemory; the other eight use Bing first.
    if lang in BING_LANGS:
        try:return bing.one(lang,text),'bing-web'
        except Exception as e:
            print('R76_BING_FALLBACK',lang,repr(e),flush=True)
            return translateapi_one(lang,text),'translateapi-web'
    if lang in MYMEMORY_LANGS:
        try:return mymemory_one(lang,text),'mymemory'
        except Exception as e:
            print('R76_MYMEMORY_FALLBACK',lang,repr(e),flush=True)
            return translateapi_one(lang,text),'translateapi-web'
    return translateapi_one(lang,text),'translateapi-web'


def real_phrase(s):
    return len(re.findall(r"[A-Za-z][A-Za-z'’+-]{2,}",str(s)))>=2 and len(str(s).strip())>=10


def validate_new(b,lang,srcs,vals):
    if len(srcs)!=len(vals):raise RuntimeError('translation count mismatch')
    bad=[]
    for s,v in zip(srcs,vals):
        v=clean(v)
        if not v or not b.translation_sane(s,v):bad.append((s,v,'sane'))
        if v.lower() in BAD_FALLBACKS:bad.append((s,v,'generic-fallback'))
    unchanged=[s for s,v in zip(srcs,vals) if real_phrase(s) and b.clean_text(s)==b.clean_text(v)]
    if len(unchanged)>max(8,int(len(srcs)*.18)):bad.append(('unchanged',unchanged[:8],len(unchanged)))
    freq=collections.Counter(clean(v) for v in vals if clean(v))
    if freq and freq.most_common(1)[0][1]>max(5,int(len(vals)*.10)):bad.append(('duplicate-output',freq.most_common(5),'too-many'))
    if bad:raise RuntimeError(f'{lang}: quality validation failed {bad[:8]}')


def build(lang):
    if lang not in ALL:raise RuntimeError('unexpected rescue language '+lang)
    b=load_builder();src=json.loads(Path('i18n-r76-source.json').read_text(encoding='utf-8'));strings=src['strings']
    oldp=Path('i18n-r32')/(lang+'.json');old=json.loads(oldp.read_text(encoding='utf-8')) if oldp.exists() else {'translations':{}}
    oldt=old.get('translations') or {}
    translations={s:clean(oldt.get(s)) for s in strings if clean(oldt.get(s))}
    missing=[s for s in strings if s not in translations]
    missing_chars=sum(len(s) for s in missing)
    print('R76_FINAL_RESCUE',lang,'reused',len(translations),'new',len(missing),'chars',missing_chars,'total',len(strings),flush=True)
    # TranslateAPI's anonymous web tier reports a 5k daily source-character quota.
    # Rare-language jobs get their own runner/IP and should fit comfortably.
    if lang in TRANSLATEAPI_LANGS and missing_chars>4900:
        raise RuntimeError(f'{lang}: {missing_chars} missing source chars exceed safe anonymous quota')
    vals=[];providers=[];bing=Bing() if lang in BING_LANGS else None
    for i,s in enumerate(missing,1):
        v,p=fallback_translate(lang,s,bing);v=clean(v);vals.append(v);providers.append(p)
        if i%10==0 or i==len(missing):print('R76_FINAL_PROGRESS',lang,i,'of',len(missing),p,flush=True)
        time.sleep(.08 if p=='bing-web' else .18)
    validate_new(b,lang,missing,vals)
    for s,v in zip(missing,vals):translations[s]=v
    assert len(translations)==src['count']==len(strings),(lang,len(translations),src['count'])
    provider='old-pack+'+'+'.join(dict.fromkeys(providers))
    payload={'version':VER,'sourceHash':src['sourceHash'],'language':lang,'count':src['count'],'provider':provider,'translations':translations}
    out=Path('i18n-r76');out.mkdir(exist_ok=True);(out/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('R76_FINAL_RESCUE_PASS',lang,len(translations),provider,flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();build(a.lang)
