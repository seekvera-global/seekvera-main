from pathlib import Path

p=Path('post-ad.html')
s=p.read_text()

old="const SB='https://nrdpyydfrpmqedtzmbyw.supabase.co',KEY='sb_publishable_tqqPQxqdNowIsSlJz4bW5w_kHOC905o',WORKER='https://seekvera-main.seekvera-global.workers.dev',MODERATION=SB+'/functions/v1/marketplace-moderate',REVIEW=SB+'/functions/v1/marketplace-review';const H={'apikey':KEY,'Authorization':'Bearer '+KEY};"
new="const SB='https://nrdpyydfrpmqedtzmbyw.supabase.co',KEY='sb_publishable_tqqPQxqdNowIsSlJz4bW5w_kHOC905o',WORKER='https://seekvera-main.seekvera-global.workers.dev',MODERATION=SB+'/functions/v1/marketplace-moderate',SUBMIT=SB+'/functions/v1/marketplace-submit',REVIEW=SB+'/functions/v1/marketplace-review';const H={'apikey':KEY,'Authorization':'Bearer '+KEY};"
assert old in s
s=s.replace(old,new,1)

old=""" try{\n  const r=await fetch(WORKER+'/api/moderate',{method:'POST',headers:{'content-type':'application/json'},body:payload});\n  if(r.ok){const d=await r.json();if(typeof d?.allowed==='boolean')return d}\n }catch{}\n return{allowed:false,reviewRequired:true,reason:'Safety check temporarily unavailable. Please try again.',source:'fail-closed'}"""
new=""" try{\n  const r=await fetch(WORKER+'/api/moderate',{method:'POST',headers:{'content-type':'application/json'},body:payload});\n  if(r.ok){const d=await r.json();if(typeof d?.allowed==='boolean')return d}\n }catch{}\n try{\n  const r=await fetch(MODERATION,{method:'POST',headers:{...H,'content-type':'application/json'},body:payload});\n  if(r.ok){const d=await r.json();if(typeof d?.allowed==='boolean')return d}\n }catch{}\n return{allowed:false,reviewRequired:true,reason:'Safety check temporarily unavailable. Please try again.',source:'fail-closed'}"""
assert old in s
s=s.replace(old,new,1)

old="const ad_ref=ref();const body={ad_ref,title:val('title'),description:val('description'),category:val('category'),listing_type:val('listing_type'),seller_type:val('seller_type'),seller_name:val('seller_name'),phone:val('phone')||null,whatsapp:val('whatsapp')||null,email:val('email')||null,country:val('country'),state_region:val('state_region')||null,city:val('city')||null,price:val('price')?Number(val('price')):null,currency:val('currency'),price_type:val('price_type'),item_condition:val('item_condition'),status:'pending',plan_code:'free',featured_rank:0};"
new="let ad_ref='';const body={title:val('title'),description:val('description'),category:val('category'),listing_type:val('listing_type'),seller_type:val('seller_type'),seller_name:val('seller_name'),phone:val('phone')||null,whatsapp:val('whatsapp')||null,email:val('email')||null,country:val('country'),state_region:val('state_region')||null,city:val('city')||null,price:val('price')?Number(val('price')):null,currency:val('currency'),price_type:val('price_type'),item_condition:val('item_condition'),ownership:true,consent:true,terms_accept:true};"
assert old in s
s=s.replace(old,new,1)

old="st.textContent='Submitting for review…';const r=await fetch(SB+'/rest/v1/marketplace_listings',{method:'POST',headers:{...H,'content-type':'application/json','Prefer':'return=minimal'},body:JSON.stringify(body)});if(!r.ok){const detail=await r.text();if(detail.includes('SEEKVERA_PROHIBITED_CONTENT')){st.textContent='Blocked by SEEKVERA Safety: prohibited content cannot be submitted.';return}throw new Error(detail)}for(let i=0;i<fs.length;i++){"
new="st.textContent='Submitting through secure server gate…';const r=await fetch(SUBMIT,{method:'POST',headers:{...H,'content-type':'application/json'},body:JSON.stringify(body)});const sd=await r.json().catch(()=>({}));if(!r.ok){if(sd?.blocked){st.textContent='Blocked by SEEKVERA Safety: prohibited content cannot be submitted.';return}if(sd?.rateLimited){st.textContent='Too many submissions. Please try again later.';return}throw new Error(sd?.error||'Secure submission failed')}ad_ref=sd.ad_ref;if(!ad_ref)throw new Error('Missing secure reference');for(let i=0;i<fs.length;i++){"
assert old in s
s=s.replace(old,new,1)

p.write_text(s)
print('server submission patch applied')
