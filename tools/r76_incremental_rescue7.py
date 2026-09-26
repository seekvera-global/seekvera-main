from __future__ import annotations
from pathlib import Path
import argparse, collections, http.cookiejar, importlib.util, json, re, time, urllib.parse, urllib.request

VER='20260926-r76-complete-global-final'
BING_LANGS={'fr','it','nl','ro','to','fy','xh','tn'}
MYMEMORY_LANGS={'sr'}
GOOGLE_LANGS={'kl'}
CF_LANGS={'rm'}
BUILDER='https://seekveraglobal.com/api/__r76_translate_builder'
BAD={'[object object]','i understood your request. i’m taking you directly to the best matching section now.',"i understood your request. i'm taking you directly to the best matching section now."}

def load_builder():
    spec=importlib.util.spec_from_file_location('r76_builder',Path('tools/r76_build_pack.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def clean(v):
    s=str(v or '').strip();s=re.sub(r'^```(?:json|text)?\s*','',s,flags=re.I);s=re.sub(r'```$','',s).strip()
    if len(s)>=2 and s[0]==s[-1] and s[0] in ('"',"'"):s=s[1:-1].strip()
    return s

class Bing:
    def __init__(self):
        self.h={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36','Accept-Language':'en-US,en;q=0.9'};self.calls=0;self.refresh()
    def refresh(self):
        self.cj=http.cookiejar.CookieJar();self.op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        html=self.op.open(urllib.request.Request('https://www.bing.com/translator',headers=self.h),timeout=25).read().decode('utf-8','replace')
        ig=(re.search(r'IG:"([^"]+)"',html) or re.search(r'"IG":"([^"]+)"',html));ab=re.search(r'params_AbusePreventionHelper\s*=\s*\[(\d+),"([^"]+)",(\d+)\]',html)
        if not ig or not ab:raise RuntimeError('Bing session markers missing')
        self.key,self.token,_=ab.groups();self.ig=ig.group(1);self.calls=0
    def raw(self,lang,text):
        last=None
        for attempt in range(6):
            try:
                if self.calls>=30:self.refresh()
                data=urllib.parse.urlencode({'fromLang':'en','to':lang,'text':text,'token':self.token,'key':self.key}).encode()
                url=f'https://www.bing.com/ttranslatev3?isVertical=1&&IG={urllib.parse.quote(self.ig)}&IID=translator.5024.1'
                req=urllib.request.Request(url,data=data,headers={**self.h,'Content-Type':'application/x-www-form-urlencoded','Referer':'https://www.bing.com/translator'},method='POST')
                d=json.loads(self.op.open(req,timeout=30).read().decode('utf-8','replace'));self.calls+=1
                out=clean(d[0]['translations'][0]['text']) if isinstance(d,list) and d and d[0].get('translations') else ''
                if not out:raise RuntimeError('Bing empty')
                return out
            except Exception as e:
                last=e;time.sleep(1.5*(attempt+1));self.refresh()
        raise RuntimeError(f'Bing failed {lang}: {last!r}')
    def batch(self,lang,items):
        if len(items)==1:return [self.raw(lang,items[0])]
        marked=''.join(f'\n§§{i}§§\n{s}' for i,s in enumerate(items))
        try:
            out=self.raw(lang,marked);ms=list(re.finditer(r'§§\s*(\d+)\s*§§',out));vals=['']*len(items)
            if len(ms)!=len(items):raise RuntimeError('marker count')
            for j,m in enumerate(ms):
                idx=int(m.group(1));end=ms[j+1].start() if j+1<len(ms) else len(out);vals[idx]=clean(out[m.end():end])
            if all(vals):return vals
            raise RuntimeError('empty member')
        except Exception as e:
            print('R76_BING_SPLIT',lang,len(items),repr(e),flush=True)
            mid=max(1,len(items)//2);return self.batch(lang,items[:mid])+self.batch(lang,items[mid:])

def mymemory_one(lang,text):
    last=None
    for attempt in range(6):
        try:
            u='https://api.mymemory.translated.net/get?'+urllib.parse.urlencode({'q':text,'langpair':'en|'+lang});req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 SEEKVERA-R76'})
            d=json.loads(urllib.request.urlopen(req,timeout=25).read().decode('utf-8','replace'));out=clean((d.get('responseData') or {}).get('translatedText'))
            if not out or out.lower()==text.lower():raise RuntimeError('empty/unchanged')
            return out
        except Exception as e:last=e;time.sleep(1.2*(attempt+1))
    raise RuntimeError(f'MyMemory failed {lang}: {last!r}')

def google_one(lang,text):
    last=None
    for client,host in [('at','translate.google.com'),('dict-chrome-ex','clients5.google.com'),('gtx','translate.googleapis.com')]:
        for attempt in range(4):
            try:
                q=urllib.parse.urlencode({'client':client,'sl':'en','tl':lang,'dt':'t','q':text});path='/translate_a/t' if host=='clients5.google.com' else '/translate_a/single'
                req=urllib.request.Request('https://'+host+path+'?'+q,headers={'User-Agent':'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'})
                d=json.loads(urllib.request.urlopen(req,timeout=25).read().decode('utf-8','replace'))
                out=clean(d[0] if host=='clients5.google.com' and isinstance(d,list) and d else ''.join(str(x[0] or '') for x in (d[0] if isinstance(d,list) and d else []) if isinstance(x,list)))
                if not out or out.lower()==text.lower():raise RuntimeError('empty/unchanged')
                return out
            except Exception as e:last=e;time.sleep(.8*(attempt+1))
    raise RuntimeError(f'Google failed {lang}: {last!r}')

def cf_one(lang,text):
    last=None
    for attempt in range(10):
        try:
            body=json.dumps({'target':lang,'text':text},ensure_ascii=False).encode();req=urllib.request.Request(BUILDER,data=body,headers={'content-type':'application/json','user-agent':'SEEKVERA-R76-HYBRID'},method='POST')
            d=json.loads(urllib.request.urlopen(req,timeout=75).read().decode('utf-8','replace'));out=clean(d.get('translation'))
            if not d.get('ok') or not out or out.lower() in BAD or out.lower()==text.lower():raise RuntimeError('bad builder '+repr(d)[:300])
            return out
        except Exception as e:
            last=e;delay=min(3+attempt*2,18);print('R76_CF_RETRY',lang,attempt+1,delay,repr(e),flush=True);time.sleep(delay)
    raise RuntimeError(f'Cloudflare builder failed {lang}: {last!r}')

def cf_batch(lang,items):
    if len(items)==1:return [cf_one(lang,items[0])]
    try:
        out=cf_one(lang,json.dumps(items,ensure_ascii=False));arr=json.loads(clean(out));vals=[clean(x) for x in arr] if isinstance(arr,list) else []
        if len(vals)!=len(items) or not all(vals):raise RuntimeError('bad array size/content')
        return vals
    except Exception as e:
        print('R76_CF_SPLIT',lang,len(items),repr(e),flush=True);time.sleep(3)
        mid=max(1,len(items)//2);return cf_batch(lang,items[:mid])+cf_batch(lang,items[mid:])

def real_phrase(s):return len(re.findall(r"[A-Za-z][A-Za-z'’+-]{2,}",str(s)))>=2 and len(str(s).strip())>=10

def validate_new(b,lang,srcs,vals):
    bad=[]
    if len(srcs)!=len(vals):raise RuntimeError('count mismatch')
    for s,v in zip(srcs,vals):
        v=clean(v)
        if not v or not b.translation_sane(s,v) or v.lower() in BAD:bad.append((s,v))
    unchanged=[s for s,v in zip(srcs,vals) if real_phrase(s) and b.clean_text(s)==b.clean_text(v)]
    if len(unchanged)>max(8,int(len(srcs)*.18)):bad.append(('unchanged',unchanged[:8]))
    freq=collections.Counter(clean(v) for v in vals if clean(v))
    if freq and freq.most_common(1)[0][1]>max(5,int(len(vals)*.10)):bad.append(('duplicates',freq.most_common(3)))
    if bad:raise RuntimeError(f'{lang}: quality failed {bad[:8]}')

def build(lang):
    if lang not in BING_LANGS|MYMEMORY_LANGS|GOOGLE_LANGS|CF_LANGS:raise RuntimeError('unsupported '+lang)
    b=load_builder();src=json.loads(Path('i18n-r76-source.json').read_text());strings=src['strings'];oldp=Path('i18n-r32')/(lang+'.json');old=json.loads(oldp.read_text()) if oldp.exists() else {'translations':{}};oldt=old.get('translations') or {}
    translations={s:clean(oldt.get(s)) for s in strings if clean(oldt.get(s))};missing=[s for s in strings if s not in translations];vals=[]
    print('R76_RESCUE7',lang,'reused',len(translations),'new',len(missing),flush=True)
    if lang in BING_LANGS:
        provider='bing-web';bing=Bing()
        for start in range(0,len(missing),8):vals.extend(bing.batch(lang,missing[start:start+8]));print('R76_PROGRESS',lang,len(vals),'of',len(missing),flush=True);time.sleep(.5)
    elif lang in MYMEMORY_LANGS:
        provider='mymemory'
        for i,s in enumerate(missing,1):vals.append(mymemory_one(lang,s));print('R76_PROGRESS',lang,i,'of',len(missing),flush=True) if i%15==0 or i==len(missing) else None;time.sleep(.1)
    elif lang in GOOGLE_LANGS:
        provider='google-at'
        for i,s in enumerate(missing,1):vals.append(google_one(lang,s));print('R76_PROGRESS',lang,i,'of',len(missing),flush=True) if i%15==0 or i==len(missing) else None;time.sleep(.1)
    else:
        provider='cloudflare-glm-split'
        for start in range(0,len(missing),20):vals.extend(cf_batch(lang,missing[start:start+20]));print('R76_PROGRESS',lang,len(vals),'of',len(missing),flush=True);time.sleep(3)
    validate_new(b,lang,missing,vals)
    for s,v in zip(missing,vals):translations[s]=clean(v)
    assert len(translations)==src['count']==len(strings)
    payload={'version':VER,'sourceHash':src['sourceHash'],'language':lang,'count':src['count'],'provider':'old-pack+'+provider,'translations':translations};out=Path('i18n-r76');out.mkdir(exist_ok=True);(out/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
    print('R76_RESCUE7_PASS',lang,len(translations),payload['provider'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();build(a.lang)
