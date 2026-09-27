import {chromium} from 'playwright';import fs from 'node:fs';
const ar=fs.readFileSync('/tmp/r102-ar.wav').toString('base64');
const en=fs.readFileSync('/tmp/r102-en.wav').toString('base64');
const b=await chromium.launch({headless:true});const p=await b.newPage();
p.on('console',m=>console.log('BROWSER',m.type(),m.text()));
await p.goto('https://seekveraglobal.com/?r102='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
const out=await p.evaluate(async({ar,en})=>{
 const mod=await import('/patched-transformers.js?r102='+Date.now());
 mod.env.allowRemoteModels=true;mod.env.remoteHost='https://huggingface.co/';mod.env.remotePathTemplate='{model}/resolve/{revision}/';mod.env.useBrowserCache=true;mod.env.backends.onnx.wasm.wasmPaths='https://cdn.jsdelivr.net/npm/onnxruntime-web@1.25.0-dev.20260212-1a71a5f46e/dist/';
 const pipe=await mod.pipeline('automatic-speech-recognition','Xenova/whisper-small',{dtype:'q8',device:'wasm'});
 const mk=b64=>{const x=atob(b64),u=new Uint8Array(x.length);for(let i=0;i<x.length;i++)u[i]=x.charCodeAt(i);return new Blob([u],{type:'audio/wav'})};
 const ua=URL.createObjectURL(mk(ar)),ue=URL.createObjectURL(mk(en));
 try{return{ar:await pipe(ua,{task:'transcribe',language:'arabic'}),en:await pipe(ue,{task:'transcribe',language:'english'})}}finally{URL.revokeObjectURL(ua);URL.revokeObjectURL(ue)}
},{ar,en});
console.log('R102_SMALL_RESULT',JSON.stringify(out));await b.close();
