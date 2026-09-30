const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const src=fs.readFileSync('worker-r31.js','utf8');
const a=src.indexOf('const audioResp=async(r,engine,target)=>'),b=src.indexOf(';if(env.AI)',a);
const ctx={Response,Headers,Uint8Array,atob,req:{headers:new Headers()},ALLOWED:new Set(),lang:'fr'};
vm.createContext(ctx);vm.runInContext(src.slice(a,b)+';globalThis.decodeAudio=audioResp;',ctx);
(async()=>{
 const mp3=Buffer.concat([Buffer.from('ID3'),Buffer.alloc(600)]);
 for(const body of [{audio:mp3.toString('base64')},{result:{audio:mp3.toString('base64')}}]){
  const r=await ctx.decodeAudio(Response.json(body),'melo','fr');
  assert.equal(r.headers.get('content-type'),'audio/mpeg');
  assert.deepEqual(Buffer.from(await r.arrayBuffer()),mp3);
 }
 const error=await ctx.decodeAudio(Response.json({error:'unavailable'}),'melo','fr');
 assert.equal(error,null);
 const r=await ctx.decodeAudio(new Response(mp3,{headers:{'content-type':'audio/mpeg'}}),'native','fr');
 assert.deepEqual(Buffer.from(await r.arrayBuffer()),mp3);
 console.log('PASS: JSON audio envelopes decode to playable bytes; nested audio works; error envelopes are rejected; binary audio is preserved.');
})().catch(e=>{console.error(e);process.exitCode=1});
