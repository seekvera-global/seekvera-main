const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('worker-r76.js','utf8');
const context={Response,Headers,URL,atob,setTimeout:()=>0,clearTimeout,console};
vm.createContext(context);vm.runInContext(source.slice(source.indexOf('const RELEASE='),source.indexOf('export default')),context);
for(const [message,expression,locale] of [['بدي أسافر',/عم بفتحلك/,'ar-LB'],['عايز فندق',/هفتحلك/,'ar-EG'],['أبغى فندق',/أبشر/,'ar-SA'],['بغيت فندق',/واخا/,'ar-MA'],['أريد فندقاً',/بالتأكيد/,'ar']]){
 const result=context.fastActionResult(message,{language:'auto'});
 assert.equal(result?.category,'travel',message);assert.match(result.response,expression,message);assert.equal(result.speechLocale,locale,message);
}
const saved=context.fastActionResult('افتح فندق',{language:'auto',history:[{role:'user',content:'احكي معي لبناني'}]});assert.match(saved.response,/عم بفتحلك/);
const voice=fs.readFileSync('voice-ai.js','utf8');
assert.ok(voice.includes('whisper?.needsReview'),'server uncertainty must reach review path');
context.json=(_,data,status)=>({data,status});
const audio='data:audio/mpeg;base64,'+Buffer.alloc(100).toString('base64');
const request=body=>({headers:{get:()=>null},json:async()=>body});
(async()=>{
 let calls=[];const recovery=await context.transcribeAudio(request({audio,language:'auto',conversationLanguage:'ar'}),{AI:{run:async(model,input)=>{calls.push(input);return input.language==='ar'?{text:'بدي سيارة',language:'ar',segments:[{avg_logprob:-.2,no_speech_prob:.01}]}:{text:'Halið á að leita',language:'is',segments:[{avg_logprob:-.8,no_speech_prob:.1}]}}}});
 assert.equal(calls[0].language,undefined);assert.equal(calls[1].language,'ar');assert.equal(recovery.data.text,'بدي سيارة');assert.equal(recovery.data.needsReview,false);
 const uncertain=await context.transcribeAudio(request({audio,language:'auto',conversationLanguage:'ar'}),{AI:{run:async()=>({text:'Halið á að leita',language:'is',segments:[{avg_logprob:-.8,no_speech_prob:.1}]})}});assert.equal(uncertain.data.needsReview,true);
 calls=[];const french=await context.transcribeAudio(request({audio,language:'auto',conversationLanguage:'ar'}),{AI:{run:async(model,input)=>{calls.push(input);return{text:'Bonjour, je cherche un hôtel',language:'fr',segments:[{avg_logprob:-.2,no_speech_prob:.01}]}}}});assert.equal(french.data.language,'fr');assert.equal(french.data.needsReview,false);assert.equal(calls.length,1,'confident new language must remain automatic');
 const missing=await context.transcribeAudio(request({audio,language:'auto'}),{AI:{run:async()=>({text:'Amdáir ala sigil bíó Tælland.',language:'is'})}});assert.equal(missing.data.needsReview,true,'missing confidence cannot authorize automatic sending');
 console.log('PASS: five Arabic registers, user dialect continuity, uncertain audio recovery/review, confident French switch unaffected.');
})().catch(e=>{console.error(e);process.exitCode=1});
