from pathlib import Path
import re

p=Path('worker.js')
s=p.read_text(encoding='utf-8')
pat=re.compile(r"if\(u\.pathname==='/api/ui-translate'\)\{try\{.*?\}\}\n\nif\(u\.pathname==='/api/transcribe'\)",re.S)
m=pat.search(s)
if not m:
    raise SystemExit('ui-translate route not found')
route=r'''if(u.pathname==='/api/ui-translate'){try{
 const b=await request.json(),language=clean(b.language,80),strings=Array.isArray(b.strings)?b.strings.slice(0,20).map(x=>clean(x,700)):[];
 if(!language||!strings.length||strings.some(x=>!x))return j(request,{ok:false,error:'Language and strings are required'},400);
 const raw='r32|'+language+'\u0000'+JSON.stringify(strings),dig=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)),hex=[...new Uint8Array(dig)].map(x=>x.toString(16).padStart(2,'0')).join('');
 const cache=await caches.open('seekvera-ui-translate-r32'),ck=new Request(new URL('/__sv_ui_translation_r32/'+hex,request.url).toString(),{method:'GET'}),hit=await cache.match(ck);
 if(hit){try{const cached=await hit.json();if(cached?.ok&&Array.isArray(cached.translations)&&cached.translations.length===strings.length)return j(request,{...cached,cached:true})}catch{}}
 const sys='You are SEEKVERA UI translator. LANGUAGE LOCK: translate every supplied interface string fully into '+language+'. Return ONLY one valid JSON array of exactly '+strings.length+' strings, same order. No markdown, no keys, no explanation. Preserve SEEKVERA, URLs, currency codes, model names, emojis, punctuation placeholders and numbers. Translate labels, buttons, headings, descriptions and accessibility text naturally. Never return English unless the target language is English.';
 const user=JSON.stringify(strings);
 const parse=v=>{try{let t=String(v||'').trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'');const a=t.indexOf('['),z=t.lastIndexOf(']');if(a<0||z<=a)return null;const arr=JSON.parse(t.slice(a,z+1));if(!Array.isArray(arr)||arr.length!==strings.length||arr.some((x,i)=>typeof x!=='string'||!x.trim()||(language.toLowerCase()!=='english'&&x.trim()===strings[i].trim())))return null;return arr.map(x=>String(x).trim())}catch{return null}};
 let arr=null,model='';
 if(env.AI){
  const models=[TRANSLATE,FASTCHAT,LIGHT,FALLBACK,PRIMARY];
  for(const md of models){try{const input={messages:[{role:'system',content:sys},{role:'user',content:user}],temperature:0};if(md===PRIMARY||md===FALLBACK)input.max_completion_tokens=1400;else input.max_tokens=1400;const r=await env.AI.run(md,input);arr=parse(out(r));if(arr){model=md;break}}catch(e){console.warn('UI translation model fallback',md,clean(e?.message||e,180))}}
 }
 if(!arr){
  try{const prompt=sys+'\nUSER STRINGS:\n'+user,signal=(typeof AbortSignal!=='undefined'&&AbortSignal.timeout)?AbortSignal.timeout(10000):undefined,br=await fetch('https://text.pollinations.ai/'+encodeURIComponent(prompt)+'?model=openai&private=true',{headers:{accept:'text/plain','user-agent':'SEEKVERA-R32/1.0'},...(signal?{signal}:{})});if(br.ok){arr=parse(await br.text());if(arr)model='pollinations-private-translation-backup'}}catch(e){console.warn('UI public translation fallback',clean(e?.message||e,180))}
 }
 if(!arr)return j(request,{ok:false,error:'UI translation temporarily unavailable',retryable:true,reason:'all_translation_backends_unavailable'},503);
 const payload={ok:true,language,translations:arr,model};
 try{await cache.put(ck,new Response(JSON.stringify(payload),{headers:{'content-type':'application/json; charset=utf-8','cache-control':'public, max-age=2592000'}}))}catch{}
 return j(request,payload)
 }catch(e){return j(request,{ok:false,error:'UI translation temporarily unavailable',retryable:true,reason:'translation_error'},503)}}

if(u.pathname==='/api/transcribe')'''
s=s[:m.start()]+route+s[m.end():]
p.write_text(s,encoding='utf-8')
print('R32 universal translation backend patched')
