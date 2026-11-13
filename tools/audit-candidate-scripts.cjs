// Script screening shares the production validator; never linguistic certification.
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync(process.env.WORKER_VALIDATOR_SOURCE||'worker.js','utf8'),ctx={};
const marker='function uiScriptPattern(code){';
const start=source.indexOf(marker);
if(start<0)throw new Error('uiScriptPattern validator not found in worker source');
let depth=0,end=-1;
for(let i=start+marker.length-1;i<source.length;i++){
 if(source[i]==='{')depth++;
 else if(source[i]==='}'&&--depth===0){end=i+1;break;}
}
if(end<0)throw new Error('uiScriptPattern validator has an unclosed function body');
const scriptPatternSource=source.slice(start,end);
vm.createContext(ctx);vm.runInContext(scriptPatternSource+'\nthis.uiScriptPattern=uiScriptPattern;',ctx);
function classify(code,sourceText,value,pattern){
 if(sourceText==='SV-YYYYMMDD-XXXXXXXX'&&value!==sourceText)return 'reserved_identifier_mutation';
 const sourceDate=/^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\s*[·|•-]\s*R\d+$/u.test(sourceText);
 const targetDate=/^\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\s*[·|•-]\s*R\d+$/u.test(value);
 if(sourceDate&&targetDate)return 'date_version_format_review';
 const normalize=s=>String(s).normalize('NFKC').toLowerCase().replace(/[\p{P}\p{S}\s]/gu,'');
 if(normalize(sourceText)===normalize(value))return 'case_or_punctuation_only_review';
 if(pattern&&!pattern.test(value))return /[A-Za-z]/.test(value)?'latin_only_or_mixed_without_target_script':'wrong_or_unverified_script';
 return 'target_script_present_manual_review';
}
let input='';process.stdin.setEncoding('utf8');process.stdin.on('data',s=>input+=s);process.stdin.on('end',()=>{
 const packs=JSON.parse(input),issues={};
 for(const [code,values] of Object.entries(packs)){
  const pattern=ctx.uiScriptPattern(code);
  const missing=Object.entries(values).filter(([key,value])=>key==='SV-YYYYMMDD-XXXXXXXX'&&value!==key||/[A-Za-z]/.test(key)&&!/[{}<>;]|https?:\/\/|[\w.]+\.(?:com|org|js|html)/i.test(key)&&value!==key&&pattern&&!pattern.test(value));
  if(missing.length){
   const examples=missing.slice(0,5).map(([source,value])=>({source,value,category:classify(code,source,value,pattern)}));
   const categoryCounts={};
   for(const [source,value] of missing){const category=classify(code,source,value,pattern);categoryCounts[category]=(categoryCounts[category]||0)+1;}
   issues[code]={count:missing.length,sources:missing.map(([source])=>source),examples,categoryCounts};
  }
 }
 process.stdout.write(JSON.stringify(issues));
});
