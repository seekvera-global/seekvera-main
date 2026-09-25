from pathlib import Path

# Browser real-chat resilience. The Cloudflare free AI pool may hit its daily limit;
# the app then replaces the route-only emergency response with a real private text AI
# response in the browser while preserving server safety and local app controls.
p=Path('r24-ai-controller.js')
s=p.read_text(encoding='utf-8')
if 'pollinations-browser-private-backup' not in s:
    old="const nativeFetch=window.fetch.bind(window);\nwindow.fetch=async function(input,init){let controls={};let raw=init?.body;try{if(raw==null&&typeof Request!=='undefined'&&input instanceof Request)raw=await input.clone().text();const b=typeof raw==='string'?JSON.parse(raw):{};controls=detectControls(b?.message||b?.prompt||'')}catch{}const res=await nativeFetch(input,init);if(!sameApi(input))return res;let data=null;try{data=await res.clone().json()}catch{return res}const server={country:data?.countryAction?.code||'',language:data?.languageAction?.code||''};const merged={country:String(server.country||controls.country||'').toUpperCase(),language:String(server.language||controls.language||'').toLowerCase()};if(merged.country||merged.language)applyControls(merged);if(!merged.country&&!merged.language)return res;const payload={...data,...actionPayload(merged),controlVersion:VERSION};return new Response(JSON.stringify(payload),{status:res.status,headers:new Headers(res.headers)})};"
    new="""const nativeFetch=window.fetch.bind(window);
async function browserAiBackup(body={},base={}){const message=String(body?.message||body?.prompt||'').trim();if(!message||base?.blocked||base?.reviewRequired)return null;const history=Array.isArray(body?.history)?body.history.slice(-8).map(x=>String(x?.role||'user')+': '+String(x?.content||'')).join('\\n'):'';const prompt=['You are SEEKVERA AI, the helpful assistant inside a worldwide discovery and marketplace app.','Understand the latest user message in any language and reply naturally in that SAME language and script unless the user explicitly requests another language.','Be concise, practical and conversational. Help the user find the correct SEEKVERA section when relevant. Never invent live prices, availability, bookings, jobs, company replies or guarantees. Never request passwords, OTP, PIN or CVV.','Selected market: '+String(body?.country||'Worldwide')+'.','Conversation context: '+history.slice(-1800),'Latest user message: '+message.slice(0,1200)].join('\\n');const u='https://text.pollinations.ai/'+encodeURIComponent(prompt)+'?model=openai&private=true';const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),16000);try{const r=await nativeFetch(u,{method:'GET',headers:{accept:'text/plain'},signal:ctl.signal,cache:'no-store'});if(!r.ok)return null;const text=String(await r.text()).trim().slice(0,5000);if(!text)return null;return{...base,ok:true,response:text,model:'pollinations-browser-private-backup',degraded:false,providerAvailable:true,retryable:false,browserBackup:true}}catch{return null}finally{clearTimeout(to)}}
window.fetch=async function(input,init){let controls={},body={};let raw=init?.body;try{if(raw==null&&typeof Request!=='undefined'&&input instanceof Request)raw=await input.clone().text();body=typeof raw==='string'?JSON.parse(raw):{};controls=detectControls(body?.message||body?.prompt||'')}catch{}const res=await nativeFetch(input,init);if(!sameApi(input))return res;let data=null;try{data=await res.clone().json()}catch{return res}let usedBackup=false;if(!data?.blocked&&!data?.reviewRequired&&(res.status===503||data?.degraded===true||data?.model==='seekvera-local-router')){const backup=await browserAiBackup(body,data);if(backup){data=backup;usedBackup=true}}const server={country:data?.countryAction?.code||'',language:data?.languageAction?.code||''};const merged={country:String(server.country||controls.country||'').toUpperCase(),language:String(server.language||controls.language||'').toLowerCase()};if(merged.country||merged.language)applyControls(merged);if(!usedBackup&&!merged.country&&!merged.language)return res;const payload={...data,...actionPayload(merged),controlVersion:VERSION};const headers=new Headers(res.headers);headers.set('content-type','application/json; charset=utf-8');headers.set('cache-control','no-store');if(usedBackup)headers.set('x-seekvera-ai-mode','browser-private-backup');return new Response(JSON.stringify(payload),{status:usedBackup?200:res.status,headers})};"""
    if old not in s: raise SystemExit('R26 fetch wrapper anchor missing')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# Browser translation resilience for all 98 supported UI languages. Native browser
# Translator is preferred, server translation is second, and the private public text
# provider is used only when both are unavailable. Cached translations remain local.
p=Path('i18n-ui.js')
s=p.read_text(encoding='utf-8')
if 'svBrowserTranslate' not in s:
    old="""async function batchTranslate(l,arr){
 if(!arr.length)return new Map();
 const out=await nativeBatch(l,arr);
 const requestBatch=async(batch)=>{if(!batch.length)return;try{const r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:langName(l),strings:batch})});const d=await r.json().catch(()=>null);if(r.ok&&Array.isArray(d?.translations)&&d.translations.length===batch.length){batch.forEach((src,j)=>{const v=String(d.translations[j]||'').trim();if(v&&v!==src){put(l,src,v);out.set(src,v)}})}}catch{}};
 let remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 for(let i=0;i<remaining.length;i+=12)await requestBatch(remaining.slice(i,i+12));
 remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 for(let i=0;i<remaining.length;i+=4)await requestBatch(remaining.slice(i,i+4));
 return out
}"""
    new="""async function batchTranslate(l,arr){
 if(!arr.length)return new Map();
 const out=await nativeBatch(l,arr);
 const svBrowserTranslate=async(batch)=>{if(!batch.length)return false;const prompt=['Translate the following user-interface strings from English into '+langName(l)+'.','Keep brand names such as SEEKVERA unchanged. Keep numbers, currency codes and URLs intact.','Return ONLY a JSON array with exactly '+batch.length+' translated strings in the same order. No markdown and no explanation.',JSON.stringify(batch)].join('\\n');const u='https://text.pollinations.ai/'+encodeURIComponent(prompt)+'?model=openai&private=true';const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),16000);try{const r=await fetch(u,{headers:{accept:'text/plain'},signal:ctl.signal,cache:'no-store'});if(!r.ok)return false;let raw=String(await r.text()).trim().replace(/^```(?:json)?\\s*/i,'').replace(/\\s*```$/,'');const a=raw.indexOf('['),b=raw.lastIndexOf(']');if(a>=0&&b>a)raw=raw.slice(a,b+1);const vals=JSON.parse(raw);if(!Array.isArray(vals)||vals.length!==batch.length)return false;let n=0;batch.forEach((src,j)=>{const v=String(vals[j]||'').trim();if(v&&v!==src){put(l,src,v);out.set(src,v);n++}});return n>0}catch{return false}finally{clearTimeout(to)}};
 const requestBatch=async(batch)=>{if(!batch.length)return;let done=false;try{const r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:langName(l),strings:batch})});const d=await r.json().catch(()=>null);if(r.ok&&Array.isArray(d?.translations)&&d.translations.length===batch.length){batch.forEach((src,j)=>{const v=String(d.translations[j]||'').trim();if(v&&v!==src){put(l,src,v);out.set(src,v)}});done=batch.every(src=>out.has(src)||cached(l,src))}}catch{}if(!done)await svBrowserTranslate(batch.filter(src=>!out.has(src)&&!cached(l,src)))};
 let remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 for(let i=0;i<remaining.length;i+=12)await requestBatch(remaining.slice(i,i+12));
 remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 for(let i=0;i<remaining.length;i+=4)await requestBatch(remaining.slice(i,i+4));
 return out
}"""
    if old not in s: raise SystemExit('R26 i18n batch anchor missing')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

c=Path('r24-ai-controller.js').read_text(encoding='utf-8')
i=Path('i18n-ui.js').read_text(encoding='utf-8')
assert 'pollinations-browser-private-backup' in c
assert "res.status===503||data?.degraded===true||data?.model==='seekvera-local-router'" in c
assert "if(!message||base?.blocked||base?.reviewRequired)return null" in c
assert 'svBrowserTranslate' in i
assert "Return ONLY a JSON array" in i
print('R26 browser AI + 98-language translation resilience PASS')
