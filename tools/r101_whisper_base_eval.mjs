import {chromium} from 'playwright';
import fs from 'node:fs';
const en=fs.readFileSync('/tmp/r101-en.wav').toString('base64');
const ar=fs.readFileSync('/tmp/r101-ar.wav').toString('base64');
const b=await chromium.launch({headless:true});
const p=await b.newPage();
p.on('console',m=>console.log('BROWSER',m.type(),m.text()));
await p.goto('https://seekveraglobal.com/?r101=model-'+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
const out=await p.evaluate(async({en,ar})=>{
  const mod=await import('/patched-transformers.js?r101='+Date.now());
  mod.env.allowRemoteModels=true;mod.env.remoteHost='https://huggingface.co/';mod.env.remotePathTemplate='{model}/resolve/{revision}/';mod.env.useBrowserCache=true;mod.env.backends.onnx.wasm.wasmPaths='https://cdn.jsdelivr.net/npm/onnxruntime-web@1.25.0-dev.20260212-1a71a5f46e/dist/';
  const pipe=await mod.pipeline('automatic-speech-recognition','Xenova/whisper-base',{dtype:'q8',device:'wasm'});
  const mk=b64=>{const x=atob(b64),u=new Uint8Array(x.length);for(let i=0;i<x.length;i++)u[i]=x.charCodeAt(i);return new Blob([u],{type:'audio/wav'})};
  const url1=URL.createObjectURL(mk(ar)),url2=URL.createObjectURL(mk(en));
  try{
    const arHint=await pipe(url1,{task:'transcribe',language:'arabic'});
    const arAuto=await pipe(url1,{task:'transcribe'});
    const enHint=await pipe(url2,{task:'transcribe',language:'english'});
    const enAuto=await pipe(url2,{task:'transcribe'});
    return{arHint,arAuto,enHint,enAuto};
  }finally{URL.revokeObjectURL(url1);URL.revokeObjectURL(url2)}
},{en,ar});
console.log('R101_BASE_RESULT',JSON.stringify(out));
await b.close();
