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
 const raw='r33d|'+language+'\u0000'+JSON.stringify(strings),dig=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)),hex=[...new Uint8Array(dig)].map(x=>x.toString(16).padStart(2,'0')).join('');
 const cache=await caches.open('seekvera-ui-translate-r33d'),ck=new Request(new URL('/__sv_ui_translation_r33d/'+hex,request.url).toString(),{method:'GET'}),hit=await cache.match(ck);
 if(hit){try{const cached=await hit.json();if(cached?.ok&&Array.isArray(cached.translations)&&cached.translations.length===strings.length)return j(request,{...cached,cached:true})}catch{}}
 const sys='You are SEEKVERA UI translator. LANGUAGE LOCK: translate every supplied interface string fully into '+language+'. Return ONLY one valid JSON array of exactly '+strings.length+' strings, same order. No markdown, no keys, no explanation. Preserve SEEKVERA, URLs, currency codes, model names, emojis, punctuation placeholders and numbers. Translate labels, buttons, headings, descriptions and accessibility text naturally. Never return English unless the target language is English.';
 const user=JSON.stringify(strings),backendErrors=[];
 const parse=v=>{try{let t=String(v||'').trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'');const a=t.indexOf('['),z=t.lastIndexOf(']');if(a<0||z<=a)return null;const arr=JSON.parse(t.slice(a,z+1));if(!Array.isArray(arr)||arr.length!==strings.length||arr.some((x,i)=>typeof x!=='string'||!x.trim()||(language.toLowerCase()!=='english'&&x.trim()===strings[i].trim())))return null;return arr.map(x=>String(x).trim())}catch{return null}};
 let arr=null,model='';
 if(env.AI){
  const models=[TRANSLATE,FASTCHAT,LIGHT,FALLBACK,PRIMARY];
  for(const md of models){try{const input={messages:[{role:'system',content:sys},{role:'user',content:user}],temperature:0};if(md===PRIMARY||md===FALLBACK)input.max_completion_tokens=1400;else input.max_tokens=1400;const r=await env.AI.run(md,input);arr=parse(out(r));if(arr){model=md;break}backendErrors.push('workers-ai:'+md+':unparseable')}catch(e){backendErrors.push('workers-ai:'+md+':'+clean(e?.message||e,120))}}
 }
 if(!arr){
  try{const prompt=sys+'\nUSER STRINGS:\n'+user,signal=(typeof AbortSignal!=='undefined'&&AbortSignal.timeout)?AbortSignal.timeout(10000):undefined,br=await fetch('https://text.pollinations.ai/'+encodeURIComponent(prompt)+'?model=openai&private=true',{headers:{accept:'text/plain','user-agent':'SEEKVERA-R33/1.0'},...(signal?{signal}:{})});if(br.ok){arr=parse(await br.text());if(arr)model='pollinations-private-translation-backup';else backendErrors.push('pollinations:unparseable')}else backendErrors.push('pollinations:http-'+br.status)}catch(e){backendErrors.push('pollinations:'+clean(e?.message||e,120))}
 }
 if(!arr){
  const names={arabic:'ar',french:'fr',german:'de',spanish:'es',chinese:'zh',japanese:'ja',korean:'ko',hindi:'hi',portuguese:'pt',russian:'ru',italian:'it',turkish:'tr',dutch:'nl',polish:'pl',ukrainian:'uk',romanian:'ro',greek:'el',czech:'cs',slovak:'sk',hungarian:'hu',swedish:'sv',norwegian:'no',danish:'da',finnish:'fi',bulgarian:'bg',croatian:'hr',serbian:'sr',slovenian:'sl',lithuanian:'lt',latvian:'lv',estonian:'et',catalan:'ca',basque:'eu',galician:'gl',icelandic:'is',albanian:'sq',macedonian:'mk',georgian:'ka',armenian:'hy',azerbaijani:'az',kazakh:'kk',uzbek:'uz',nepali:'ne',sinhala:'si',tamil:'ta',telugu:'te',malayalam:'ml',marathi:'mr',gujarati:'gu',punjabi:'pa',bengali:'bn',urdu:'ur',persian:'fa',hebrew:'he',indonesian:'id',malay:'ms',thai:'th',vietnamese:'vi',filipino:'tl',tagalog:'tl',swahili:'sw',hausa:'ha',yoruba:'yo',igbo:'ig',amharic:'am',somali:'so',afrikaans:'af',zulu:'zu',xhosa:'xh',tswana:'tn',romansh:'rm',maltese:'mt',irish:'ga',welsh:'cy',kurdish:'ku'};
  const key=language.toLowerCase().replace(/\s*\([^)]*\)\s*$/,'').trim(),tl=/^[a-z]{2,3}(?:-[a-z]{2})?$/i.test(key)?key.split('-')[0]:names[key];
  if(tl&&tl!=='en'&&strings.every(x=>new TextEncoder().encode(x).length<=480)){
   try{
    const vals=await Promise.all(strings.map(async x=>{const signal=(typeof AbortSignal!=='undefined'&&AbortSignal.timeout)?AbortSignal.timeout(8000):undefined,r=await fetch('https://api.mymemory.translated.net/get?q='+encodeURIComponent(x)+'&langpair=en%7C'+encodeURIComponent(tl),{headers:{accept:'application/json','user-agent':'SEEKVERA-R33/1.0'},...(signal?{signal}:{})});if(!r.ok)throw new Error('HTTP '+r.status);const d=await r.json(),t=clean(d?.responseData?.translatedText,900);if(!t||t.trim()===x.trim())throw new Error('untranslated:'+x.slice(0,40));return t}));
    if(vals.length===strings.length){arr=vals;model='mymemory-free-r33'}else backendErrors.push('mymemory:length-mismatch')
   }catch(e){backendErrors.push('mymemory:'+clean(e?.message||e,120))}
  }else backendErrors.push('mymemory:unsupported-language-or-size')
 }
 if(!arr)return j(request,{ok:false,error:'UI translation temporarily unavailable',retryable:true,reason:'all_translation_backends_unavailable',backendErrors:backendErrors.slice(-8)},503);
 const payload={ok:true,language,translations:arr,model};
 try{await cache.put(ck,new Response(JSON.stringify(payload),{headers:{'content-type':'application/json; charset=utf-8','cache-control':'public, max-age=2592000'}}))}catch{}
 return j(request,payload)
 }catch(e){return j(request,{ok:false,error:'UI translation temporarily unavailable',retryable:true,reason:'translation_error',detail:clean(e?.message||e,120)},503)}}

if(u.pathname==='/api/transcribe')'''
s=s[:m.start()]+route+s[m.end():]
p.write_text(s,encoding='utf-8')
print('R33d universal translation backend patched with safe backend diagnostics')