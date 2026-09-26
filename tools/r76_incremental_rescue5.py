from __future__ import annotations
from pathlib import Path
import argparse, collections, http.cookiejar, importlib.util, json, re, time, urllib.parse, urllib.request

VER='20260926-r76-complete-global-final'
BING_LANGS={'fr','it','nl','ro','to','fy','xh','tn'}
CF_LANGS={'sr','kl','rm'}
BUILDER='https://seekveraglobal.com/api/__r76_translate_builder'
BAD_FALLBACKS={
    'i understood your request. i’m taking you directly to the best matching section now.',
    "i understood your request. i'm taking you directly to the best matching section now.",
    'i’m taking you directly to the best matching section now.',
}

def load_builder():
    spec=importlib.util.spec_from_file_location('r76_builder',Path('tools/r76_build_pack.py'))
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
                if self.calls>=45:self.refresh()
                data=urllib.parse.urlencode({'fromLang':'en','to':lang,'text':text,'token':self.token,'key':self.key,'tryFetchingGenderDebiasedTranslations':'true'}).encode()
                url=f'https://www.bing.com/ttranslatev3?isVertical=1&&IG={urllib.parse.quote(self.ig)}&IID=translator.5024.1'
                req=urllib.request.Request(url,data=data,headers={**self.headers,'Content-Type':'application/x-www-form-urlencoded','Referer':'https://www.bing.com/translator'},method='POST')
                raw=self.op.open(req,timeout=25).read().decode('utf-8','replace');self.calls+=1
                d=json.loads(raw)
                if not isinstance(d,list) or not d or not d[0].get('translations'):raise RuntimeError('Bing returned no translations: '+raw[:300])
                out=clean(d[0]['translations'][0].get('text'))
                if not out:raise RuntimeError('Bing empty translation')
                return out
            except Exception as e:
                last=e;time.sleep(1.2*(attempt+1));self.refresh()
        raise RuntimeError(f'Bing failed {lang}: {last!r}')

def cf_one(lang,text):
    last=None
    for attempt in range(4):
        try:
            body=json.dumps({'target':lang,'text':text},ensure_ascii=False).encode('utf-8')
            req=urllib.request.Request(BUILDER,data=body,headers={'content-type':'application/json','user-agent':'SEEKVERA-R76-HYBRID'},method='POST')
            with urllib.request.urlopen(req,timeout=45) as r:d=json.loads(r.read().decode('utf-8','replace'))
            out=clean(d.get('translation'))
            if not d.get('ok') or not out:raise RuntimeError('builder response '+repr(d)[:400])
            return out
        except Exception as e:last=e;time.sleep(1.5*(attempt+1))
    raise RuntimeError(f'Cloudflare builder failed {lang}: {last!r}')

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
    if lang not in BING_LANGS|CF_LANGS:raise RuntimeError('rescue5 unexpected language '+lang)
    b=load_builder();src=json.loads(Path('i18n-r76-source.json').read_text(encoding='utf-8'));strings=src['strings']
    oldp=Path('i18n-r32')/(lang+'.json');old=json.loads(oldp.read_text(encoding='utf-8')) if oldp.exists() else {'translations':{}}
    oldt=old.get('translations') or {}
    translations={s:clean(oldt.get(s)) for s in strings if clean(oldt.get(s))}
    missing=[s for s in strings if s not in translations]
    print('R76_RESCUE5',lang,'reused',len(translations),'new',len(missing),'total',len(strings),flush=True)
    provider='bing-web' if lang in BING_LANGS else 'cloudflare-ai-builder'
    vals=[]
    bing=Bing() if lang in BING_LANGS else None
    for i,s in enumerate(missing,1):
        v=bing.one(lang,s) if bing else cf_one(lang,s)
        vals.append(v)
        if i%10==0 or i==len(missing):print('R76_RESCUE5_PROGRESS',lang,i,'of',len(missing),provider,flush=True)
        time.sleep(.08 if bing else .15)
    validate_new(b,lang,missing,vals)
    for s,v in zip(missing,vals):translations[s]=clean(v)
    assert len(translations)==src['count']==len(strings),(lang,len(translations),src['count'])
    payload={'version':VER,'sourceHash':src['sourceHash'],'language':lang,'count':src['count'],'provider':'old-pack+'+provider,'translations':translations}
    out=Path('i18n-r76');out.mkdir(exist_ok=True);(out/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('R76_RESCUE5_PASS',lang,len(translations),payload['provider'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();build(a.lang)
