import base from './worker-r31.js';

const MODEL='@cf/qwen/qwen3-30b-a3b-fp8';
const LANGS={sr:'Serbian',kl:'Greenlandic',rm:'Romansh'};
const clean=v=>String(v??'').trim().replace(/^```(?:text)?\s*/i,'').replace(/```$/,'').trim().replace(/^(["'])([\s\S]*)\1$/,'$2').trim();
const reply=(d,s=200)=>new Response(JSON.stringify(d),{status:s,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff'}});

async function googleTranslate(code,text){
  const qs=new URLSearchParams({client:'gtx',sl:'en',tl:code,dt:'t',q:text});
  const r=await fetch('https://translate.googleapis.com/translate_a/single?'+qs.toString(),{headers:{'user-agent':'Mozilla/5.0 (compatible; SEEKVERA-R76/1.0)','accept':'application/json,text/plain,*/*'}});
  if(!r.ok)throw new Error('google-edge-'+r.status);
  const d=await r.json();
  const out=Array.isArray(d?.[0])?d[0].map(x=>Array.isArray(x)?String(x[0]||''):'').join(''):'';
  if(!clean(out))throw new Error('google-edge-empty');
  return clean(out);
}

export default {
  async fetch(request, env, ctx) {
    const ua=request.headers.get('user-agent')||'';
    const u=new URL(request.url);

    if(ua.includes('SEEKVERA-R76-TRANSLATE')){
      return reply({ok:false,error:'translation-build-fallback-disabled'},503);
    }

    // Hidden build-only route. Ordinary customer traffic never uses this path/UA.
    // Runs Google Translate from Cloudflare's edge so GitHub runner rate limits do
    // not block the final static language-pack build.
    if(u.pathname==='/api/__r76_google_translate'&&request.method==='POST'){
      if(!ua.includes('SEEKVERA-R76-HYBRID'))return reply({ok:false,error:'not-found'},404);
      try{
        const b=await request.json();const text=clean(b?.text).slice(0,4500);const code=clean(b?.target).toLowerCase();
        if(!text||!LANGS[code])return reply({ok:false,error:'bad-request'},400);
        const out=await googleTranslate(code,text);
        return reply({ok:true,target:code,translation:out,provider:'google-edge'});
      }catch(e){return reply({ok:false,error:String(e?.message||e).slice(0,500)},502)}
    }

    // Older AI bridge kept as a secondary diagnostic fallback only.
    if(u.pathname==='/api/__r76_translate_builder'&&request.method==='POST'){
      if(!ua.includes('SEEKVERA-R76-HYBRID'))return reply({ok:false,error:'not-found'},404);
      try{
        const b=await request.json();const text=clean(b?.text).slice(0,4500);const code=clean(b?.target).toLowerCase();const language=LANGS[code];
        if(!text||!language)return reply({ok:false,error:'bad-request'},400);
        const prompt=`Translate the following SEEKVERA user-interface text from English into ${language} (${code}). Return ONLY the translated text. Preserve exact meaning, numbers, punctuation, URLs, placeholders, emoji, and the brand name SEEKVERA. Do not explain or quote the answer.\n\n${text}`;
        const r=await env.AI.run(MODEL,{messages:[{role:'system',content:'You are a precise professional UI translator. Output only the translation.'},{role:'user',content:prompt}],max_tokens:900,temperature:0.05});
        const out=clean(r?.response??r?.result?.response??r?.result??r);
        if(!out||out.length>Math.max(9000,text.length*5+500))return reply({ok:false,error:'bad-model-output'},502);
        return reply({ok:true,target:code,translation:out,model:MODEL});
      }catch(e){return reply({ok:false,error:String(e?.message||e).slice(0,500)},500)}
    }
    return base.fetch(request,env,ctx);
  }
};
