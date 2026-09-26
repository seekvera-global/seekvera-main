const MODEL='@cf/qwen/qwen3-30b-a3b-fp8';
const LANGS={sr:'Serbian',kl:'Greenlandic',rm:'Romansh'};

const clean=v=>String(v??'').trim().replace(/^```(?:text)?\s*/i,'').replace(/```$/,'').trim().replace(/^(["'])([\s\S]*)\1$/,'$2').trim();
const json=(d,s=200)=>new Response(JSON.stringify(d),{status:s,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});

export default {
  async fetch(req,env){
    const u=new URL(req.url);
    if(u.pathname==='/health')return json({ok:true,service:'seekvera-r76-builder',model:MODEL});
    if(req.method!=='POST'||u.pathname!=='/translate')return json({ok:false,error:'not-found'},404);
    try{
      const b=await req.json();
      const text=clean(b?.text).slice(0,4500);const code=clean(b?.target).toLowerCase();
      const language=LANGS[code];
      if(!text||!language)return json({ok:false,error:'bad-request'},400);
      const prompt=`Translate the following SEEKVERA user-interface text from English into ${language} (${code}). Return ONLY the translated text. Preserve the exact meaning, numbers, punctuation, URLs, placeholders, emoji and the brand name SEEKVERA. Do not explain, add labels, or quote the answer.\n\n${text}`;
      let r=await env.AI.run(MODEL,{messages:[{role:'system',content:'You are a precise professional UI translator. Output only the translation.'},{role:'user',content:prompt}],max_tokens:900,temperature:0.05});
      let out=clean(r?.response??r?.result?.response??r?.result??r);
      if(!out||out.length>Math.max(9000,text.length*5+500))return json({ok:false,error:'bad-model-output'},502);
      return json({ok:true,target:code,translation:out,model:MODEL});
    }catch(e){return json({ok:false,error:String(e?.message||e).slice(0,500)},500)}
  }
};
