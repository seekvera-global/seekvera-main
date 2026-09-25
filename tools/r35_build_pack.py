from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import argparse, concurrent.futures, hashlib, html as htmlmod, json, random, re, time, unicodedata, urllib.error, urllib.parse, urllib.request

VERSION='20260925-r35-static-v2'
OUT=Path('i18n-r35')
OUT.mkdir(exist_ok=True)
ALIASES={'fil':'tl','he':'iw'}

DYNAMIC=[
    'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.',
    'No approved live marketplace listings are available right now.',
    'SEEKVERA does not generate fake listings.',
    'Loading approved listings…','Approved real listings only.','OPEN MARKETPLACE →',
    'Find, compare, choose — worldwide.','Find, compare, choose — worldwide',
    'I’m the SEEKVERA AI assistant. Tell me what you need and I’ll help you find the right section, compare options or search worldwide.',
    'Message SEEKVERA AI…','Online','Listening…','Thinking…','Try again','Close','Open','Send','Search',
]
JS_FILES=['global-ui.js','superapp.js','voice-ai.js','navigation.js','r24-ai-controller.js','r20-final-guard.js','r22-category-lock.js','r20-extra-categories.js','app.js']
BAD_EXACT={'SEEKVERA','R20','R31','R31C','R32','R35','HTML','CSS','JSON','GET','POST','POSTS'}

def clean_text(s:str)->str:return re.sub(r'\s+',' ',str(s or '')).strip()
def worth(s:str)->bool:
    s=clean_text(s)
    if len(s)<2 or len(s)>500 or s in BAD_EXACT:return False
    if re.fullmatch(r'[A-Z0-9_-]{2,12}',s):return False
    if re.fullmatch(r'[\d\s.,:+\-/%$€£₦¥₹#@]+',s):return False
    if re.match(r'^(?:https?://|www\.|mailto:|tel:)',s,re.I):return False
    if re.search(r'\b\S+@\S+\.\S+\b',s):return False
    if re.fullmatch(r'[\w./-]+\.(?:html|js|css|json|png|jpe?g|webp|svg)',s,re.I):return False
    if any(x in s for x in ['=>','function(','document.','window.','console.','querySelector','addEventListener']):return False
    return bool(re.search(r'[A-Za-z\u00C0-\u024F]',s))
def add(dst:set[str],s:str):
    s=clean_text(s)
    if worth(s):dst.add(s)

def languages()->list[str]:
    cat=Path('locale-r14-categories.js').read_text(encoding='utf-8')
    out=['en']
    for x in re.findall(r'(?:^|\n)([a-z]{2,3}):\[',cat):
        if x not in out:out.append(x)
    if len(out)!=98:raise SystemExit(f'Expected 98 SEEKVERA languages, got {len(out)}')
    return out

def source_strings()->list[str]:
    strings:set[str]=set()
    for p in sorted(Path('.').glob('*.html')):
        if p.name.lower().startswith('google'):continue
        soup=BeautifulSoup(p.read_text(encoding='utf-8',errors='ignore'),'html.parser')
        for tag in soup(['script','style','noscript','template']):tag.decompose()
        for opt in soup.find_all('option'):opt.decompose()
        for n in soup.find_all(string=True):
            if isinstance(n,NavigableString):add(strings,str(n))
        for el in soup.find_all(True):
            for a in ('placeholder','aria-label','title'):
                if el.has_attr(a):add(strings,el.get(a,''))
    for name in JS_FILES:
        p=Path(name)
        if not p.exists():continue
        s=p.read_text(encoding='utf-8',errors='ignore')
        pats=[r'(?:textContent|innerText|placeholder|title)\s*=\s*([\'"`])((?:\\.|(?!\1).){2,500})\1',r'(?:toast|showToast|setStatus|status|message)\s*\(\s*([\'"`])((?:\\.|(?!\1).){2,300})\1']
        for pat in pats:
            for m in re.finditer(pat,s,re.S):
                raw=m.group(2)
                if '${' in raw:continue
                try:
                    if '\\' in raw and all(ord(c)<128 for c in raw):raw=bytes(raw,'utf-8').decode('unicode_escape')
                except Exception:pass
                add(strings,raw)
    for x in DYNAMIC:add(strings,x)
    return sorted(strings,key=lambda x:(len(x),x.lower()))

def source_meta():
    src=source_strings();h=hashlib.sha256('\n'.join(src).encode()).hexdigest()[:16]
    return src,h

def ascii_digits(s:str)->str:
    out=[]
    for c in str(s or ''):
        try:out.append(str(unicodedata.digit(c)) if unicodedata.category(c)=='Nd' else c)
        except Exception:out.append(c)
    return ''.join(out)

def google_request(code:str,text:str,timeout=55)->str:
    tl=ALIASES.get(code,code)
    data=urllib.parse.urlencode({'client':'gtx','sl':'en','tl':tl,'dt':'t','q':text}).encode()
    req=urllib.request.Request('https://translate.googleapis.com/translate_a/single',data=data,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req,timeout=timeout) as r:obj=json.loads(r.read().decode('utf-8'))
    return ''.join(x[0] for x in obj[0] if x and x[0]).strip()

def html_google_batch(code:str,batch:list[str])->list[str]:
    body='\n'.join(f'<span id="sv{i:04d}">{htmlmod.escape(s)}</span>' for i,s in enumerate(batch))
    raw=google_request(code,body)
    soup=BeautifulSoup(raw,'html.parser');vals=[None]*len(batch)
    for sp in soup.find_all('span'):
        sid=ascii_digits(sp.get('id',''))
        m=re.fullmatch(r'sv(\d{4})',sid,re.I)
        if not m:continue
        i=int(m.group(1))
        if 0<=i<len(vals):vals[i]=clean_text(sp.get_text(' ',strip=True))
    missing=[i for i,v in enumerate(vals) if not v]
    if missing:raise ValueError(f'html markers missing {code}: {missing[:12]}')
    out=[str(v) for v in vals]
    same=sum(1 for a,b in zip(batch,out) if clean_text(a)==clean_text(b))
    if same>max(80,int(len(batch)*.72)):raise ValueError(f'too many untranslated strings {code}: {same}/{len(batch)}')
    return out

def single_google(code:str,s:str)->str:
    last=None
    for attempt in range(4):
        try:
            v=clean_text(google_request(code,s,35))
            if v:return v
        except Exception as e:last=e;time.sleep(.6+attempt*.7)
    raise RuntimeError(f'single google failed {code}: {last!r}')

def google_translate(code:str,batch:list[str],depth=0)->list[str]:
    last=None
    for attempt in range(2):
        try:
            vals=html_google_batch(code,batch);time.sleep(.08+random.random()*.10);return vals
        except Exception as e:
            last=e;print('HTML_RETRY',code,len(batch),attempt+1,repr(e),flush=True);time.sleep(.5+attempt*.6)
    if len(batch)>48:
        mid=len(batch)//2
        print('HTML_SPLIT',code,len(batch),'->',mid,len(batch)-mid,flush=True)
        return google_translate(code,batch[:mid],depth+1)+google_translate(code,batch[mid:],depth+1)
    print('SINGLE_FALLBACK',code,len(batch),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(lambda s:single_google(code,s),batch))

def lang_name(code:str)->str:
    try:
        from babel import Locale
        return Locale.parse(code).get_display_name('en') or code
    except Exception:return code

def pollinations_chunk(code:str,batch:list[str])->list[str]:
    name=lang_name(code)
    prompt=(f'Translate this JSON array of website user-interface strings from English into {name} ({code}). '
            f'Keep SEEKVERA, URLs, numbers, currency codes, product names and placeholders unchanged. '
            f'Return ONLY one valid JSON array of exactly {len(batch)} strings in the same order, no markdown.\n'+json.dumps(batch,ensure_ascii=False))
    url='https://text.pollinations.ai/'+urllib.parse.quote(prompt)+'?model=openai&private=true'
    req=urllib.request.Request(url,headers={'Accept':'text/plain','User-Agent':'SEEKVERA-R35-pack-builder/2.0'})
    with urllib.request.urlopen(req,timeout=40) as r:raw=r.read().decode('utf-8').strip()
    raw=re.sub(r'^```(?:json)?\s*','',raw,flags=re.I);raw=re.sub(r'\s*```$','',raw)
    a,b=raw.find('['),raw.rfind(']')
    if a>=0 and b>a:raw=raw[a:b+1]
    vals=json.loads(raw)
    if not isinstance(vals,list) or len(vals)!=len(batch) or any(not str(x).strip() for x in vals):raise ValueError('bad pollinations batch')
    return [str(x).strip() for x in vals]

def pollinations_translate(code:str,source:list[str])->list[str]:
    out=[]
    for i in range(0,len(source),12):
        batch=source[i:i+12];last=None
        for attempt in range(3):
            try:out.extend(pollinations_chunk(code,batch));break
            except Exception as e:last=e;print('PUBLIC_RETRY',code,i,attempt+1,repr(e),flush=True);time.sleep(1+attempt*1.5)
        else:raise RuntimeError(f'public fallback failed {code}/{i}: {last!r}')
    return out

def build(code:str):
    langs=languages()
    if code not in langs:raise SystemExit(f'Unsupported SEEKVERA language: {code}')
    source,h=source_meta();print('SOURCE',len(source),h,'LANG',code,flush=True)
    if code=='en':vals=source[:];provider='local'
    else:
        try:vals=google_translate(code,source);provider='google-html'
        except Exception as e:
            print('GOOGLE_FATAL_FALLBACK',code,repr(e),flush=True);vals=pollinations_translate(code,source);provider='public-ai'
    if len(vals)!=len(source):raise RuntimeError(f'{code}: {len(vals)} != {len(source)}')
    trans={s:v for s,v in zip(source,vals)}
    critical='No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.'
    if code!='en' and clean_text(trans.get(critical,''))==critical:raise RuntimeError(f'{code}: critical sentence remained English')
    payload={'version':VERSION,'sourceHash':h,'language':code,'count':len(source),'provider':provider,'translations':trans}
    p=OUT/f'{code}.json';p.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('PACK_PASS',code,len(source),provider,p,flush=True)

def write_source():
    src,h=source_meta();langs=languages()
    Path('i18n-r35-source.json').write_text(json.dumps({'version':VERSION,'sourceHash':h,'count':len(src),'strings':src},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    Path('i18n-r35-languages.json').write_text(json.dumps(langs,separators=(',',':')),encoding='utf-8')
    print('SOURCE_PASS',len(src),h,'LANGS',len(langs),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang');ap.add_argument('--source-only',action='store_true');a=ap.parse_args()
    if a.source_only:write_source()
    elif a.lang:build(a.lang)
    else:raise SystemExit('Use --lang CODE or --source-only')
