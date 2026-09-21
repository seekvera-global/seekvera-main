from pathlib import Path
import re

p = Path('post-ad.html')
text = p.read_text(encoding='utf-8')

old_const = "const SB='https://nrdpyydfrpmqedtzmbyw.supabase.co',KEY='sb_publishable_tqqPQxqdNowIsSlJz4bW5w_kHOC905o',WORKER='https://seekvera-main.seekvera-global.workers.dev';const H={'apikey':KEY,'Authorization':'Bearer '+KEY};"
new_const = "const SB='https://nrdpyydfrpmqedtzmbyw.supabase.co',KEY='sb_publishable_tqqPQxqdNowIsSlJz4bW5w_kHOC905o',WORKER='https://seekvera-main.seekvera-global.workers.dev',MODERATION=SB+'/functions/v1/marketplace-moderate';const H={'apikey':KEY,'Authorization':'Bearer '+KEY};"
if old_const in text:
    text = text.replace(old_const, new_const, 1)
elif "MODERATION=SB+'/functions/v1/marketplace-moderate'" not in text:
    raise SystemExit('Could not find SEEKVERA constants block')

new_moderate = r'''async function moderate(body){
 const text=[body.title,body.description,body.category,body.listing_type,body.country,body.city].filter(Boolean).join(' ');
 const local=localSafetyReason(text);if(local)return{allowed:false,reviewRequired:true,reason:local,source:'local-rules'};
 const payload=JSON.stringify({title:body.title,description:body.description,category:body.category,listing_type:body.listing_type,text});
 try{
  const r=await fetch(MODERATION,{method:'POST',headers:{...H,'content-type':'application/json'},body:payload});
  if(r.ok){const d=await r.json();if(typeof d?.allowed==='boolean')return d}
 }catch{}
 try{
  const r=await fetch(WORKER+'/api/moderate',{method:'POST',headers:{'content-type':'application/json'},body:payload});
  if(r.ok){const d=await r.json();if(typeof d?.allowed==='boolean')return d}
 }catch{}
 return{allowed:false,reviewRequired:true,reason:'Safety check temporarily unavailable. Please try again.',source:'fail-closed'}
}
async function uploadFile'''

pattern = re.compile(r"async function moderate\(body\)\{.*?\}\nasync function uploadFile", re.S)
if pattern.search(text):
    text = pattern.sub(new_moderate, text, count=1)
elif "source:'fail-closed'" not in text:
    raise SystemExit('Could not find moderation function')

p.write_text(text, encoding='utf-8')
print('Patched post-ad.html with fail-closed Supabase moderation fallback.')
