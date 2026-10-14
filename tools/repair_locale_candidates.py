"""Repair only public, provenanced candidate strings and checkpoint completed batches."""
import argparse,concurrent.futures,hashlib,importlib,json,sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--checkout',required=True);ap.add_argument('--stage',required=True);ap.add_argument('--languages',required=True);ap.add_argument('--workers',type=int,default=2,choices=range(1,4));ap.add_argument('--batch-size',type=int,default=4,choices=range(1,9));args=ap.parse_args()
 checkout=Path(args.checkout).resolve();sys.path.insert(0,str(checkout));builder=importlib.import_module('tools.build_current_locale_delta');assert builder.ROOT==checkout
 source=builder.source_inventory();source_hash=hashlib.sha256('\n'.join(source).encode()).hexdigest()[:16]
 proof=json.loads((checkout/'docs/public-ui-translation-provenance.json').read_text());assert proof.get('publicRepository') is True and not proof.get('mismatches') and proof['sourceHash']==source_hash
 for name,expected in proof['publicBlobHashes'].items():
  raw=(checkout/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==expected,name
 builder.ALLOWED_PUBLIC_STRINGS=set(source);print('VERIFIED_PUBLIC_UI_ONLY',len(source),source_hash,flush=True)
 stage=Path(args.stage);manifest=json.loads((checkout/'i18n-r32/manifest.json').read_text());failures=[];completed=[];stop=False
 for code in args.languages.split(','):
  assert code in manifest['languages'];path=stage/(code+'.json');data=json.loads(path.read_text());assert data['sourceHash']==source_hash
  values=data['translations'];providers={data.get('provider','existing')};retranslated=set(data.get('retranslatedKeys',[]))
  if 'SV-YYYYMMDD-XXXXXXXX' in source:values['SV-YYYYMMDD-XXXXXXXX']='SV-YYYYMMDD-XXXXXXXX'
  wrong=builder.script_mismatches(code,values);missing=[k for k in source if not values.get(k) or k in wrong or code!='en' and builder.suspicious_overlap(k,values[k])]
  batches=[missing[i:i+args.batch_size] for i in range(0,len(missing),args.batch_size)];print('REPAIR',code,len(missing),'strings',flush=True)
  language=builder.translation_language_name(code)
  def process(batch):
   translations,provider=builder.translate_small(language,batch);return batch,translations,provider
  iterator=iter(batches);done_count=0
  with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
   pending={}
   def submit_next():
    if stop:return
    batch=next(iterator,None)
    if batch:pending[executor.submit(process,batch)]=batch
   for _ in range(args.workers):submit_next()
   while pending:
    done,_=concurrent.futures.wait(pending,return_when=concurrent.futures.FIRST_COMPLETED)
    for future in done:
     batch=pending.pop(future)
     try:
      batch,translations,provider=future.result();values.update(zip(batch,translations));retranslated.update(batch);providers.add(provider);done_count+=len(batch)
      data.update(translations={k:values[k] for k in source if values.get(k)},retranslatedKeys=sorted(retranslated),provider='+'.join(sorted(providers)));builder.atomic_json(path,data)
      print('SAVED',code,done_count,'/',len(missing),flush=True)
     except Exception as error:
      failures.append({'language':code,'strings':batch,'error':str(error)[:1200]});print('FAILED',code,str(error)[:250],flush=True)
      if 'daily_free_ai_limit' in str(error):stop=True
     submit_next()
  data.update(translations={k:values[k] for k in source if values.get(k)},retranslatedKeys=sorted(retranslated),provider='+'.join(sorted(providers)));builder.atomic_json(path,data)
  if all(values.get(k) for k in source) and not builder.script_mismatches(code,values) and (code=='en' or not any(builder.suspicious_overlap(k,values[k]) for k in source)):completed.append(code)
  if stop:break
 report={'sourceHash':source_hash,'requestedLanguages':args.languages.split(','),'completed':completed,'failures':failures,'published':False,'finalApproval':False,'linguisticAccuracyCertified':False}
 builder.atomic_json(stage/'repair-progress.json',report);print(json.dumps({'completed':completed,'failedBatches':len(failures)}),flush=True);return 0 if not failures and set(completed)==set(args.languages.split(',')) else 1
if __name__=='__main__':raise SystemExit(main())
