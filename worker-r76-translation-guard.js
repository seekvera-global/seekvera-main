import base from './worker-r31.js';

const MODELS=['@cf/zai-org/glm-4.7-flash','@cf/mistralai/mistral-small-3.1-24b-instruct'];
const LANGS={sr:'Serbian',kl:'Greenlandic',rm:'Romansh'};
const clean=v=>String(v??'').trim().replace(/^```(?:text)?\s*/i,'').replace(/```$/,'').trim().replace(/^(["'])([\s\S]*)\1$/,'$2').trim();
const reply=(d,s=200)=>new Response(JSON.stringify(d),{status:s,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff'}});

async function aiTranslate(env,code,text){
  const language=LANGS[code];
  const prompt=`Translate this SEEKVERA user-interface text from English into ${language}. Return ONLY the translated text. Preserve meaning, numbers, punctuation, URLs, placeholders, emoji and SEEKVERA. Do not explain.\n\n${text}`;
  const errors=[];
  for(const model of MODELS){
    try{
      const r=await env.AI.run(model,{messages:[{role:'system',content:'You are a precise professional translator. Return translation only.'},{role:'user',content:prompt}],max_tokens:1000,temperature:0.05});
      const out=clean(r?.response??r?.result?.response??r?.result??r);
      if(out&&out.toLowerCase()!==text.toLowerCase()&&out.length<=Math.max(9000,text.length*6+500))return {out,model};
      errors.push(model+':empty-or-unchanged');
    }catch(e){errors.push(model+':'+String(e?.message||e).slice(0,180));}
  }
  throw new Error(errors.join(' | '));
}

export default {
  async fetch(request, env, ctx) {
    const ua=request.headers.get('user-agent')||'';
    const u=new URL(request.url);
    if(ua.includes('SEEKVERA-R76-TRANSLATE'))return reply({ok:false,error:'translation-build-fallback-disabled'},503);

    if(u.pathname==='/api/__r76_translate_builder'&&request.method==='POST'){
      if(!ua.includes('SEEKVERA-R76-HYBRID'))return reply({ok:false,error:'not-found'},404);
      try{
        const b=await request.json();const text=clean(b?.text).slice(0,4500);const code=clean(b?.target).toLowerCase();
        if(!text||!LANGS[code])return reply({ok:false,error:'bad-request'},400);
        const x=await aiTranslate(env,code,text);
        return reply({ok:true,target:code,translation:x.out,model:x.model});
      }catch(e){return reply({ok:false,error:String(e?.message||e).slice(0,900)},502)}
    }
    return base.fetch(request,env,ctx);
  }
};
