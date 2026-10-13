const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('voice-ai.js','utf8');const start=source.indexOf('async function serverSpeakSequence('),end=source.indexOf('\nfunction speak(',start);
const calls=[];const context={speakToken:1,muted:false,serverSpeak:async(text,loc,token,last)=>{calls.push({text,last});return text!=='second'}};vm.createContext(context);vm.runInContext(source.slice(start,end),context);
(async()=>{
 const result=await context.serverSpeakSequence(['first','second','third'],'ar-LB',1);
 assert.equal(result.ok,false);assert.equal(result.nextIndex,1);assert.deepEqual(calls.map(c=>c.text),['first','second']);
 const remaining=['first','second','third'].slice(result.nextIndex);assert.deepEqual(remaining,['second','third']);
 context.serverSpeak=async(text,loc,token,last)=>{calls.push({text,last});return true};calls.length=0;
 const success=await context.serverSpeakSequence(remaining,'ar-LB',1);assert.equal(success.ok,true);assert.deepEqual(calls.map(c=>c.last),[false,true]);
 calls.length=0;context.speakToken=2;const cancelled=await context.serverSpeakSequence(remaining,'ar-LB',1);assert.equal(cancelled.ok,false);assert.equal(calls.length,0);
 assert(source.includes("mod.env.remoteHost=apiBase()+'/api/asr-model/'"));
 assert(source.includes("mod.env.backends.onnx.wasm.wasmPaths=apiBase()+'/api/ort/'"));
 assert(source.includes('nativeSpeak(chunks.slice(result.nextIndex),token)'));assert(!source.includes('serverSpeak(lastAnswer,lastLocale,token,true)'));
 console.log('PASS: a failed audio chunk resumes at that chunk; already spoken sentences are not replayed; completion occurs once; cancelled turns do not play.');
})().catch(e=>{console.error(e);process.exitCode=1});
