"""Audit staged packs without claiming linguistic review or publishing them."""
import argparse,datetime,json,subprocess
from pathlib import Path
from tools.build_current_locale_delta import ROOT,reviewed_labels,suspicious_overlap

def audit(stage,exit_code='not-run'):
 source=json.loads((stage/'source.json').read_text());languages=json.loads((ROOT/'i18n-r32/manifest.json').read_text())['languages'];reviewed=reviewed_labels();completed=[];failures={};packs={}
 for code in languages:
  path=stage/(code+'.json')
  if not path.exists():failures[code]=['missing_pack'];continue
  data=json.loads(path.read_text());values=data.get('translations',{});reasons=[]
  if data.get('sourceHash')!=source['sourceHash']:reasons.append('source_hash_mismatch')
  if data.get('qualityPolicy')!='source-overlap-5-v1':reasons.append('quality_policy_mismatch')
  if not all(isinstance(values.get(k),str) and values[k].strip() for k in source['strings']):reasons.append('missing_strings')
  if not all(values.get(k)==v for k,v in reviewed.get(code,{}).items() if k in source['strings']):reasons.append('reviewed_label_mismatch')
  overlap=[k for k in source['strings'] if code!='en' and suspicious_overlap(k,values.get(k,''))]
  if overlap:reasons.append('english_overlap:'+str(len(overlap)))
  if reasons:failures[code]=reasons
  else:completed.append(code)
  packs[code]=values
 script=Path(__file__).with_name('audit-candidate-scripts.cjs')
 script_issues=json.loads(subprocess.check_output(['node',str(script)],input=json.dumps(packs),text=True,cwd=ROOT))
 report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceHash':source['sourceHash'],'completed':completed,'completedCount':len(completed),'remaining':[c for c in languages if c not in completed],'structuralFailures':failures,'scriptWarnings':script_issues,'exitCode':str(exit_code),'published':False,'finalApproval':False,'linguisticAccuracyCertified':False,'scope':'Source coverage, reviewed labels, long English overlap and script screening. Structural completeness does not certify translation quality.'}
 report['resumeSucceeded']=str(exit_code)=='0' and not report['remaining']
 report['readyForLinguisticReview']=not report['remaining'] and not script_issues
 return report

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);args=ap.parse_args();stage=Path(args.stage);exit_path=stage/'resume-exit-code.txt';report=audit(stage,exit_path.read_text().strip() if exit_path.exists() else 'not-run');(stage/'resume-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:report[k] for k in ['completedCount','remaining','resumeSucceeded','readyForLinguisticReview','exitCode']}));return 0 if report['resumeSucceeded'] and report['readyForLinguisticReview'] else 1
if __name__=='__main__':raise SystemExit(main())
