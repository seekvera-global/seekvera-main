from __future__ import annotations
from pathlib import Path
import concurrent.futures,json,re,time,urllib.parse,urllib.request

ALIASES={'fil':'tl','he':'iw'}
CODELIKE=re.compile(r'(@media|grid-template|\{[^}]*\}|=>|function\(|document\.|window\.|querySelector|addEventListener)',re.I)
CRITICAL=['Popular categories','Live marketplace','Request anything','No approved live marketplace listings are available right now.','SEEKVERA does not generate fake listings.','Find, compare, choose — worldwide.']


def bad_value(src:str,val:str)->bool:
    s=str(src or '').strip();v=str(val or '').strip();sl=max(1,len(s))
    if not v:return True
    if len(v)>max(500,sl*10):return True
    # Extremely long translated values for a short UI label are always corruption.
    if sl<=80 and len(v)>700:return True
    return False


def google_single(code:str,text:str)->str:
    tl=ALIASES.get(code,code)
    data=urllib.parse.urlencode({'client':'gtx','sl':'en','tl':tl,'dt':'t','q':text}).encode()
    last=None
    for attempt in range(6):
        try:
            req=urllib.request.Request('https://translate.googleapis.com/translate_a/single',data=data,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req,timeout=35) as r:obj=json.loads(r.read().decode('utf-8'))
            out=''.join(x[0] for x in obj[0] if x and x[0]).strip()
            if out:return out
        except Exception as e:
            last=e;time.sleep(.5+attempt*.7)
    raise RuntimeError(f'{code} single translation failed: {last!r}')


def main():
    root=Path('i18n-r32');src_meta=json.loads(Path('i18n-r32-source.json').read_text(encoding='utf-8'))
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['packs']==98 and len(manifest['languages'])==98
    assert src_meta['count']==967 and manifest['sourceHash']==src_meta['sourceHash']
    packs={}
    tasks=[]
    for code in manifest['languages']:
        p=root/f'{code}.json';d=json.loads(p.read_text(encoding='utf-8'));packs[code]=(p,d)
        assert d['sourceHash']==src_meta['sourceHash'] and d['count']==967 and len(d['translations'])==967,code
        if code=='en':continue
        for s,v in d['translations'].items():
            if bad_value(s,v):tasks.append((code,s))
    print('R49 BAD ENTRIES',len(tasks),'LANGUAGES',sorted(set(c for c,_ in tasks)),flush=True)
    def repair(item):
        code,s=item
        if CODELIKE.search(s):return code,s,s,'preserve-code'
        v=google_single(code,s)
        if bad_value(s,v):raise RuntimeError(f'repair still anomalous {code}: {s[:80]!r} -> {len(v)}')
        return code,s,v,'google-single'
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        fixed=list(ex.map(repair,tasks))
    touched=set()
    for code,s,v,provider in fixed:
        p,d=packs[code];d['translations'][s]=v;d['provider']='integrity-repaired-single';touched.add(code)
    for code in touched:
        p,d=packs[code];p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    # Final fail-closed validation.
    failures=[]
    for code,(p,d) in packs.items():
        if code!='en':
            for s,v in d['translations'].items():
                if bad_value(s,v):failures.append((code,s[:90],len(s),len(str(v or ''))))
            for s in CRITICAL:
                if s in d['translations'] and str(d['translations'][s]).strip()==s:failures.append((code,'critical-untranslated:'+s,len(s),len(s)))
    if failures:raise SystemExit('R49 validation failed '+repr(failures[:20]))
    print('R49 PACK INTEGRITY PASS',json.dumps({'repairedEntries':len(fixed),'repairedLanguages':sorted(touched)},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
