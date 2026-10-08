"""Incremental current-source translation. Stage every pack; never publish partial output."""
import argparse,difflib,hashlib,importlib.util,json,re,subprocess,time,urllib.request,urllib.error
from pathlib import Path
from babel import Locale
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent
VERSION='20261008-r125-runtime-source-coverage'
def canonical(s):return ' '.join(str(s).split())
def atomic_json(path,data):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')));tmp.replace(path)
def source_inventory():
 old=json.loads((ROOT/'i18n-r32-source.json').read_text())
 spec=importlib.util.spec_from_file_location('base',ROOT/'tools/r35_build_pack.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 b.JS_FILES=[p.name for p in ROOT.glob('*.js') if not p.name.startswith(('worker','i18n','locale'))]
 values=set(old['strings'])|set(b.source_strings())
 games=(ROOT/'games.js').read_text()
 for s in re.findall(r"desc:'([^']+)'",games):b.add(values,s)
 for s in re.findall(r"cat:'([^']+)'",games):b.add(values,s+' games')
 voice=(ROOT/'voice-ai.js').read_text()
 for s in re.findall(r"setVoicePlaceholder\([^,]+,\s*'([^']+)'",voice):b.add(values,s)
 for name in ['global-ui.js','games.js','r31-ui-polish.js','r24-ai-controller.js','navigation.js','superapp.js']:
  raw=(ROOT/name).read_text()
  for m in re.finditer(r'innerHTML\s*=\s*([\'"`])((?:\\.|(?!\1).){2,30000})\1',raw,re.S):
   soup=BeautifulSoup(m[2],'html.parser')
   for el in soup.select('script,style,[data-no-translate],.ai-msg,.sv-global-msg'):el.decompose()
   for t in soup.find_all(string=True):
    if '${' not in str(t):b.add(values,str(t))
   for el in soup.find_all(True):
    for a in ['placeholder','title','aria-label']:
     text=el.get(a,'')
     if '${' not in text:b.add(values,text)
 for s in ['All games','Touch controls','Voice','Voice reply','Safety Gate','Back','Page navigation','SEEKVERA quick tools']:
  b.add(values,s)
 old_set=set(old['strings'])
 values={s for s in values if s in old_set or not re.fullmatch(r'\d{4}-\d\d-\d\d\s*·\s*R\d+',s)}
 return sorted(values,key=lambda s:(len(s),s.lower(),s))
def reviewed_labels():
 code=(ROOT/'i18n-ui.js').read_text();initial='I’m the SEEKVERA AI assistant. Tell me what you need and I’ll help you find the right section, compare options or search worldwide.'
 script='const vm=require("vm");const c={INITIAL_AI:'+json.dumps(initial)+'};vm.createContext(c);vm.runInContext('+json.dumps(code[code.index('const QUICK='):code.index('function api(')])+'+";globalThis.labels=QUICK",c);process.stdout.write(JSON.stringify(c.labels));'
 return json.loads(subprocess.check_output(['node','-e',script],cwd=ROOT,text=True))
def suspicious_overlap(source,value):
 if re.search(r'[{}<>;]|https?://|[\w.]+\.(?:com|org|js|html)',source) or re.match(r'R\d.*(?:trigger|deploy)',source,re.I) or source.startswith('Al Jazeera, Al Arabiya, CNN, BBC, Reuters'):return False
 words=lambda x:re.findall(r"[A-Za-z][A-Za-z'’+-]*",x.lower())
 if source.startswith('Type a country or city:'):source=source.split(':',1)[0]
 a,b=words(source),words(value)
 return len(a)>=5 and difflib.SequenceMatcher(None,a,b,autojunk=False).find_longest_match().size>=5
def translate(language,strings):
 payload=json.dumps({'language':language,'strings':strings},ensure_ascii=False).encode()
 req=urllib.request.Request('https://seekveraglobal.com/api/ui-translate',data=payload,headers={'content-type':'application/json','user-agent':'Mozilla/5.0'},method='POST')
 with urllib.request.urlopen(req,timeout=45) as r:d=json.loads(r.read())
 vals=d.get('translations')
 if not d.get('ok') or not isinstance(vals,list) or len(vals)!=len(strings) or any(not isinstance(v,str) or not v.strip() for v in vals):raise RuntimeError('Invalid translation response: '+str(d)[:400])
 bad=[(s,v) for s,v in zip(strings,vals) if suspicious_overlap(s,v)]
 if bad:raise RuntimeError('Target output still contains a long English source phrase: '+repr(bad[0])[:350])
 return vals,d.get('model','unknown')
def translate_small(language,strings):
 try:
  for attempt in range(3):
   try:return translate(language,strings)
   except (urllib.error.URLError,TimeoutError,ConnectionResetError) as e:
    if isinstance(e,urllib.error.HTTPError) or attempt==2:raise
    time.sleep(1+attempt)
 except Exception as e:
  detail=str(e)
  if isinstance(e,urllib.error.HTTPError):detail+=' '+e.read().decode()[:900]
  if 'daily_free_ai_limit' in detail:raise RuntimeError(detail) from e
  if len(strings)<=1:raise RuntimeError(detail) from e
  print('SPLIT_RETRY',language,len(strings),detail[:180],flush=True)
  mid=len(strings)//2
  a,ap=translate_small(language,strings[:mid]);b,bp=translate_small(language,strings[mid:]);return a+b,ap if ap==bp else ap+'+'+bp
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--languages');ap.add_argument('--stage',default=str(ROOT.parent/'locale-stage'));ap.add_argument('--inventory-only',action='store_true');ap.add_argument('--shard');ap.add_argument('--retranslate',default='');args=ap.parse_args()
 source=source_inventory();old=json.loads((ROOT/'i18n-r32-source.json').read_text());delta=[s for s in source if s not in old['strings']]
 stage=Path(args.stage);stage.mkdir(parents=True,exist_ok=True)
 source_hash=hashlib.sha256('\n'.join(source).encode()).hexdigest()[:16]
 src={'version':VERSION,'sourceHash':source_hash,'count':len(source),'strings':source}
 (stage/'source.json').write_text(json.dumps(src,ensure_ascii=False,separators=(',',':')))
 (stage/'new-keys.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2))
 print('CURRENT_SOURCE',len(source),'DELTA',len(delta),source_hash,flush=True)
 if args.inventory_only:return
 manifest=json.loads((ROOT/'i18n-r32/manifest.json').read_text());langs=args.languages.split(',') if args.languages else manifest['languages'];reviewed=reviewed_labels();failures=[];completed=[]
 if args.shard:
  part,total=map(int,args.shard.split('/'));assert 0<=part<total;langs=langs[part::total]
 progress=stage/('progress-part-'+str(part)+'.json' if args.shard else 'progress.json')
 for code in langs:
  if code not in manifest['languages']:raise RuntimeError('Unsupported language '+code)
  out=stage/(code+'.json')
  if out.exists():
   data=json.loads(out.read_text())
   if code not in args.retranslate.split(',') and data.get('sourceHash')==source_hash and all(data.get('translations',{}).get(k) for k in source) and data.get('qualityPolicy')=='source-overlap-5-v1' and (code=='en' or not any(suspicious_overlap(k,data['translations'][k]) for k in source)):completed.append(code);print('RESUME',code,flush=True);continue
  base=json.loads((ROOT/'i18n-r32'/f'{code}.json').read_text());trans=base['translations'];providers=set();retranslated=set()
  if out.exists():
   saved=json.loads(out.read_text())
   if saved.get('language')==code and saved.get('qualityPolicy')=='source-overlap-5-v1':trans.update(saved.get('translations',{}));retranslated.update(saved.get('retranslatedKeys',[]))
  trans.update(reviewed.get(code,{}))
  folded={canonical(k).casefold():v for k,v in trans.items()}
  for key,value in list(trans.items()):
   if key and not key[0].isalnum():
    plain=re.sub(r'^[\W_]+','',key,flags=re.UNICODE).strip()
    translated=re.sub(r'^[\W_]+','',value,flags=re.UNICODE).strip()
    if plain and translated:folded.setdefault(canonical(plain).casefold(),translated)
  for key in source:
   if key not in trans and canonical(key).casefold() in folded:trans[key]=folded[canonical(key).casefold()]
  missing=[k for k in source if not trans.get(k) or (code!='en' and suspicious_overlap(k,trans[k])) or (code in args.retranslate.split(',') and k not in retranslated and len(re.findall(r'[A-Za-z]+',k))>=3 and not re.search(r'[{}<>;]|https?://',k))]
  if code=='en':trans.update({k:k for k in source});missing=[]
  try:
   for start in range(0,len(missing),16):
    batch=missing[start:start+16];vals,provider=translate_small('Romansh (Rumantsch Grischun, Switzerland)' if code=='rm' else Locale.parse(code).get_language_name('en'),batch)
    trans.update(dict(zip(batch,vals)));providers.add(provider);retranslated.update(batch)
    print('DELTA_BATCH',code,start+len(batch),len(missing),provider,flush=True)
    # Persist a resumable successful prefix even if a later provider call fails.
    atomic_json(out,{'version':VERSION,'sourceHash':source_hash,'language':code,'count':len(source),'qualityPolicy':'source-overlap-5-v1','retranslatedKeys':sorted(retranslated),'provider':'existing+'+'+'.join(sorted(providers)),'translations':{k:trans[k] for k in source if trans.get(k)}})
    time.sleep(.3)
   assert all(trans.get(k) for k in source),code
   assert code=='en' or not any(suspicious_overlap(k,trans[k]) for k in source),code
   atomic_json(out,{'version':VERSION,'sourceHash':source_hash,'language':code,'count':len(source),'qualityPolicy':'source-overlap-5-v1','retranslatedKeys':sorted(retranslated),'provider':'existing+'+'+'.join(sorted(providers)),'translations':{k:trans[k] for k in source}})
   completed.append(code);print('COMPLETE_PACK',code,len(source),flush=True)
  except Exception as e:
   detail=str(e)
   if isinstance(e,urllib.error.HTTPError):detail+=' '+e.read().decode()[:900]
   failures.append({'language':code,'error':detail});print('DELTA_FAILURE',code,detail,flush=True)
   if 'daily_free_ai_limit' in detail:break
  progress.write_text(json.dumps({'sourceHash':source_hash,'completed':completed,'failures':failures,'finalApproval':False},ensure_ascii=False,indent=2))
 progress.write_text(json.dumps({'sourceHash':source_hash,'completed':completed,'failures':failures,'finalApproval':False},ensure_ascii=False,indent=2))
 if set(completed)==set(manifest['languages']) and not failures:
  manifest.update(version=VERSION,sourceHash=source_hash,sourceCount=len(source))
  manifest['providers']={'incremental-existing+validated-runtime':98}
  (stage/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')))
  print('ALL_98_STAGED_NOT_PUBLISHED',flush=True)
 else:print('STAGED_ONLY',len(completed),'FAILED',len(failures),flush=True)
if __name__=='__main__':main()
