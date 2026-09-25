from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import concurrent.futures, hashlib, json, random, re, time, unicodedata, urllib.error, urllib.parse, urllib.request

VERSION='20260925-r32-static-v4'
OUT=Path('i18n-r32')
OUT.mkdir(exist_ok=True)

# SEEKVERA's 98 supported language codes come from the audited local category bundle.
cat_src=Path('locale-r14-categories.js').read_text(encoding='utf-8')
LANGS=['en']
for x in re.findall(r'(?:^|\n)([a-z]{2,3}):\[',cat_src):
    if x not in LANGS: LANGS.append(x)
if len(LANGS)!=98:
    raise SystemExit(f'Expected 98 SEEKVERA languages, got {len(LANGS)}')

ALIASES={'fil':'tl','he':'iw'}
ID_PREFIX='98765432'
ID_SUFFIX='12345678'

DYNAMIC=[
    'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.',
    'No approved live marketplace listings are available right now.',
    'SEEKVERA does not generate fake listings.',
    'Loading approved listings…',
    'Approved real listings only.',
    'OPEN MARKETPLACE →',
    'Find, compare, choose — worldwide.',
    'Find, compare, choose — worldwide',
    'I’m the SEEKVERA AI assistant. Tell me what you need and I’ll help you find the right section, compare options or search worldwide.',
    'Message SEEKVERA AI…',
    'Online',
    'Listening…',
    'Thinking…',
    'Try again',
    'Close',
    'Open',
    'Send',
    'Search',
]

JS_FILES=[
    'global-ui.js','superapp.js','voice-ai.js','navigation.js','r24-ai-controller.js',
    'r20-final-guard.js','r22-category-lock.js','r20-extra-categories.js','app.js'
]
BAD_EXACT={'SEEKVERA','R20','R31','R31C','R32','HTML','CSS','JSON','GET','POST','POSTS'}

def clean_text(s:str)->str:
    return re.sub(r'\s+',' ',str(s or '')).strip()

def worth(s:str)->bool:
    s=clean_text(s)
    if len(s)<2 or len(s)>500: return False
    if s in BAD_EXACT: return False
    if re.fullmatch(r'[A-Z0-9_-]{2,12}',s): return False
    if re.fullmatch(r'[\d\s.,:+\-/%$€£₦¥₹#@]+',s): return False
    if re.match(r'^(?:https?://|www\.|mailto:|tel:)',s,re.I): return False
    if re.search(r'\b\S+@\S+\.\S+\b',s): return False
    if re.fullmatch(r'[\w./-]+\.(?:html|js|css|json|png|jpe?g|webp|svg)',s,re.I): return False
    if any(x in s for x in ['=>','function(','document.','window.','console.','querySelector','addEventListener']): return False
    return bool(re.search(r'[A-Za-z\u00C0-\u024F]',s))

def add(dst:set[str],s:str):
    s=clean_text(s)
    if worth(s): dst.add(s)

strings:set[str]=set()
for p in sorted(Path('.').glob('*.html')):
    if p.name.lower().startswith('google'): continue
    soup=BeautifulSoup(p.read_text(encoding='utf-8',errors='ignore'),'html.parser')
    for tag in soup(['script','style','noscript','template']): tag.decompose()
    for opt in soup.find_all('option'): opt.decompose()
    for n in soup.find_all(string=True):
        if isinstance(n,NavigableString): add(strings,str(n))
    for el in soup.find_all(True):
        for a in ('placeholder','aria-label','title'):
            if el.has_attr(a): add(strings,el.get(a,''))

# Capture common dynamically inserted UI literals without sweeping prompts/system code.
for name in JS_FILES:
    p=Path(name)
    if not p.exists(): continue
    s=p.read_text(encoding='utf-8',errors='ignore')
    patterns=[
        r'(?:textContent|innerText|placeholder|title)\s*=\s*([\'"`])((?:\\.|(?!\1).){2,500})\1',
        r'(?:toast|showToast|setStatus|status|message)\s*\(\s*([\'"`])((?:\\.|(?!\1).){2,300})\1',
    ]
    for pat in patterns:
        for m in re.finditer(pat,s,re.S):
            raw=m.group(2)
            if '${' in raw: continue
            try: raw=bytes(raw,'utf-8').decode('unicode_escape') if '\\' in raw and all(ord(c)<128 for c in raw) else raw
            except Exception: pass
            add(strings,raw)

for x in DYNAMIC: add(strings,x)
SOURCE=sorted(strings,key=lambda x:(len(x),x.lower()))
SOURCE_HASH=hashlib.sha256('\n'.join(SOURCE).encode()).hexdigest()[:16]
Path('i18n-r32-source.json').write_text(json.dumps({'version':VERSION,'sourceHash':SOURCE_HASH,'count':len(SOURCE),'strings':SOURCE},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('R32 static source strings:',len(SOURCE),'hash',SOURCE_HASH,'chars',sum(map(len,SOURCE)),flush=True)

def ascii_digits(s:str)->str:
    # Some locales (notably Dzongkha) localize numeric IDs. Normalize every Unicode Nd digit
    # only for locating markers; slices are taken from the untouched raw translation.
    out=[]
    for c in s:
        try:
            if unicodedata.category(c)=='Nd': out.append(str(unicodedata.digit(c)))
            else: out.append(c)
        except Exception:
            out.append(c)
    return ''.join(out)

def marker(i:int)->str:
    return f'{ID_PREFIX}{i:04d}{ID_SUFFIX}'

def indexed_google_batch(code:str,batch:list[str])->list[str]:
    tl=ALIASES.get(code,code)
    ids=[marker(i) for i in range(len(batch))]
    body='\n'.join(f'{ids[i]} {s}' for i,s in enumerate(batch))
    data=urllib.parse.urlencode({'client':'gtx','sl':'en','tl':tl,'dt':'t','q':body}).encode()
    req=urllib.request.Request('https://translate.googleapis.com/translate_a/single',data=data,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req,timeout=60) as r:
        obj=json.loads(r.read().decode('utf-8'))
    raw=''.join(x[0] for x in obj[0] if x and x[0])
    norm=ascii_digits(raw)
    positions=[norm.find(x) for x in ids]
    if any(p<0 for p in positions) or positions!=sorted(positions):
        missing=[i for i,p in enumerate(positions) if p<0]
        raise ValueError(f'indexed markers missing/reordered {code}: {missing[:20]}')
    vals=[]
    for i,pos in enumerate(positions):
        start=pos+len(ids[i])
        end=positions[i+1] if i+1<len(positions) else len(raw)
        val=raw[start:end].strip()
        if not val:
            raise ValueError(f'empty indexed translation {code}/{i}')
        vals.append(val)
    if len(vals)!=len(batch):
        raise ValueError(f'indexed count mismatch {code}: {len(vals)} != {len(batch)}')
    return vals

def pollinations_batch(code:str,batch:list[str])->list[str]:
    language_names={'rm':'Romansh'}
    name=language_names.get(code,code)
    prompt=(f'Translate this JSON array of user-interface strings from English into {name}. '
            f'Keep SEEKVERA, URLs, numbers, currency codes and placeholders unchanged. '
            f'Return ONLY one valid JSON array of exactly {len(batch)} strings, same order, no markdown.\n'+json.dumps(batch,ensure_ascii=False))
    url='https://text.pollinations.ai/'+urllib.parse.quote(prompt)+'?model=openai&private=true'
    req=urllib.request.Request(url,headers={'Accept':'text/plain','User-Agent':'SEEKVERA-R32-static-builder/4.0'})
    with urllib.request.urlopen(req,timeout=60) as r:
        raw=r.read().decode('utf-8').strip()
    raw=re.sub(r'^```(?:json)?\s*','',raw,flags=re.I);raw=re.sub(r'\s*```$','',raw)
    a,b=raw.find('['),raw.rfind(']')
    if a>=0 and b>a: raw=raw[a:b+1]
    vals=json.loads(raw)
    if not isinstance(vals,list) or len(vals)!=len(batch) or any(not str(x).strip() for x in vals):
        raise ValueError('bad Pollinations translation batch')
    return [str(x).strip() for x in vals]

def translate_google(code:str,batch:list[str])->list[str]:
    last=None
    for attempt in range(8):
        try:
            vals=indexed_google_batch(code,batch)
            time.sleep(.35+random.random()*.25)
            return vals
        except ValueError as e:
            last=e
            # A malformed provider response is retried once as two still-large indexed requests.
            # Never degrade to hundreds of single-string calls.
            if len(batch)>160:
                mid=len(batch)//2
                print('INDEX_SPLIT',code,len(batch),'->',mid,len(batch)-mid,flush=True)
                return translate_google(code,batch[:mid])+translate_google(code,batch[mid:])
            time.sleep(min(10,1.5*(attempt+1)))
        except urllib.error.HTTPError as e:
            last=e
            if e.code in (405,429,500,502,503,504):
                delay=min(60,3*(2**attempt))+random.random()*2
                print('PROVIDER_RETRY',code,e.code,'attempt',attempt+1,'sleep',round(delay,1),flush=True)
                time.sleep(delay)
            else:
                time.sleep(min(15,2*(attempt+1)))
        except Exception as e:
            last=e;time.sleep(min(15,2*(attempt+1))+random.random())
    raise RuntimeError(f'{code} indexed Google translation failed: {last!r}')

def translate_rm(batch:list[str])->list[str]:
    last=None
    for attempt in range(7):
        try:
            vals=pollinations_batch('rm',batch);time.sleep(.5);return vals
        except Exception as e:
            last=e;time.sleep(min(45,3*(attempt+1)))
    raise RuntimeError(f'rm translation failed: {last!r}')

def chunks(items:list[str],max_items=55,max_chars=6000):
    out=[];cur=[];n=0
    for s in items:
        extra=len(s)+2
        if cur and (len(cur)>=max_items or n+extra>max_chars):out.append(cur);cur=[];n=0
        cur.append(s);n+=extra
    if cur:out.append(cur)
    return out

def build_language(code:str):
    if code=='en':
        trans={s:s for s in SOURCE}
    else:
        target=OUT/f'{code}.json'
        if target.exists():
            try:
                old=json.loads(target.read_text(encoding='utf-8'))
                if old.get('sourceHash')==SOURCE_HASH and len(old.get('translations',{}))==len(SOURCE):
                    return code,len(SOURCE),'cached'
            except Exception: pass
        trans={}
        if code=='rm':
            for batch in chunks(SOURCE):
                vals=translate_rm(batch)
                for src,val in zip(batch,vals): trans[src]=val
        else:
            vals=translate_google(code,SOURCE)
            for src,val in zip(SOURCE,vals): trans[src]=val
        if len(trans)!=len(SOURCE): raise RuntimeError(f'{code}: incomplete pack')
    payload={'version':VERSION,'sourceHash':SOURCE_HASH,'language':code,'count':len(SOURCE),'translations':trans}
    (OUT/f'{code}.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    return code,len(trans),'built'

results=[]
# Only two concurrent providers: 97 Google requests total, not thousands.
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
    futs={ex.submit(build_language,c):c for c in LANGS}
    for f in concurrent.futures.as_completed(futs):
        r=f.result();results.append(r);print('PACK',r,flush=True)

if len(results)!=98: raise SystemExit('Not all language packs were built')
manifest={'version':VERSION,'sourceHash':SOURCE_HASH,'sourceCount':len(SOURCE),'languages':LANGS,'packs':98}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('R32 STATIC PACKS PASS',json.dumps(manifest),flush=True)
