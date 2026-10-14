// Script screening shares the production validator; never linguistic certification.
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync(process.env.WORKER_VALIDATOR_SOURCE||'worker.js','utf8'),ctx={};vm.createContext(ctx);vm.runInContext(source.slice(source.indexOf('function uiLanguage('),source.indexOf('export default{async fetch')),ctx);
let input='';process.stdin.setEncoding('utf8');process.stdin.on('data',s=>input+=s);process.stdin.on('end',()=>{
 const packs=JSON.parse(input),issues={};
 for(const [code,values] of Object.entries(packs)){
  const pattern=ctx.uiScriptPattern(code);
  const missing=Object.entries(values).filter(([key,value])=>key==='SV-YYYYMMDD-XXXXXXXX'&&value!==key||/[A-Za-z]/.test(key)&&!/[{}<>;]|https?:\/\/|[\w.]+\.(?:com|org|js|html)/i.test(key)&&value!==key&&pattern&&!pattern.test(value));
  if(missing.length)issues[code]={count:missing.length,sources:missing.map(([source])=>source),examples:missing.slice(0,5).map(([source,value])=>({source,value}))};
 }
 process.stdout.write(JSON.stringify(issues));
});
