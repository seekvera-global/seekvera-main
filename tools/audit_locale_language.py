"""Offline language-identity screening; this does not certify translation accuracy.

Model: fastText lid.176.ftz, CC BY-SA 3.0.
https://fasttext.cc/docs/en/language-identification.html
Joulin et al., Bag of Tricks for Efficient Text Classification (2016),
and FastText.zip: Compressing text classification models (2016).
The model is a diagnostic dependency and is not bundled into the website.
"""
import argparse,json,re
from pathlib import Path
import fasttext
from build_current_locale_delta import suspicious_overlap

def main():
 p=argparse.ArgumentParser();p.add_argument('--packs',default='i18n-r32');p.add_argument('--model',required=True);p.add_argument('--output',default='docs/locale-language-screening.json');a=p.parse_args()
 m=fasttext.load_model(a.model);supported=set(m.get_labels());root=Path(a.packs)
 manifest=json.loads(Path('i18n-r32/manifest.json').read_text());rows=[]
 for code in manifest['languages']:
  path=root/(code+'.json')
  if not path.exists():rows.append({'language':code,'status':'missing'});continue
  d=json.loads(path.read_text());t=d['translations'];expected='__label__'+{'fil':'tl'}.get(code,code)
  text=' '.join(v for k,v in t.items() if len(k)>40 and not re.search(r'[{}<>;]|https?://',k))
  predictions=[{'language':label.removeprefix('__label__'),'probability':float(prob)} for prob,label in m.f.predict(text.replace('\n',' ')+'\n',3,0.0,'strict')]
  mismatch=expected in supported and predictions[0]['language']!=expected.removeprefix('__label__') and predictions[0]['probability']>=.7
  overlap=[] if code=='en' else [k for k,v in t.items() if suspicious_overlap(k,v)]
  rows.append({'language':code,'status':'wrong-language-likely' if mismatch else 'native-review-required' if expected not in supported else 'screened','predictions':predictions,'longEnglishOverlapCount':len(overlap),'longEnglishOverlapExamples':overlap[:5],'count':len(t),'sourceHash':d.get('sourceHash')})
 report={'purpose':'Offline screening only; classifier errors and unsupported languages require native review. No semantic or hardware certification.','finalApproval':False,'packs':str(root),'languages':rows}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'packs':str(root),'missing':sum(r['status']=='missing' for r in rows),'likelyWrongLanguage':[r['language'] for r in rows if r['status']=='wrong-language-likely'],'EnglishOverlapPacks':sum(r.get('longEnglishOverlapCount',0)>0 for r in rows),'unsupported':[r['language'] for r in rows if r['status']=='native-review-required']}))
if __name__=='__main__':main()
