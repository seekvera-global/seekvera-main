from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')

text = text.replace(
    "connect-src 'self' https://seekvera-main.seekvera-global.workers.dev https://text.pollinations.ai;",
    "connect-src 'self' https://seekvera-main.seekvera-global.workers.dev https://text.pollinations.ai https://nrdpyydfrpmqedtzmbyw.supabase.co;"
)

start = text.index('document.getElementById("requestForm").addEventListener("submit",async e=>{')
end = text.index('\n});', start) + len('\n});')

new = '''document.getElementById("requestForm").addEventListener("submit",async e=>{
 e.preventDefault();
 const reference=`SV-${new Date().toISOString().slice(0,10).replaceAll("-","")}-${crypto.getRandomValues(new Uint32Array(1))[0].toString(16).toUpperCase().padStart(8,"0")}`;
 const request={reference,country:requestCountry.value.trim(),city:requestCity.value.trim(),request_type:requestType.value,budget:requestBudget.value.trim(),needed_date:requestDate.value||null,contact:requestContact.value.trim(),description:requestDescription.value.trim(),source:"seekvera-web"};
 localStorage.setItem("seekvera_last_request",JSON.stringify(request));
 const success=document.getElementById("requestSuccess");
 const submit=e.currentTarget.querySelector("button[type=submit],button.primary");
 const oldLabel=submit.textContent;submit.disabled=true;submit.textContent="Saving...";
 try{
  const endpoint="https://nrdpyydfrpmqedtzmbyw.supabase.co/rest/v1/seekvera_requests";
  const key="sb_publishable_tqqPQxqdNowIsSlJz4bW5w_kHOC905o";
  const res=await fetch(endpoint,{method:"POST",headers:{"content-type":"application/json","apikey":key,"Authorization":`Bearer ${key}`,"Prefer":"return=minimal"},body:JSON.stringify(request)});
  if(!res.ok){const detail=await res.text();throw new Error(detail||`HTTP ${res.status}`)}
  success.textContent=`Request saved securely. Reference: ${reference}`;
  success.classList.add("show");
  e.currentTarget.reset();
 }catch(err){
  console.error("SEEKVERA request save failed",err);
  success.textContent="We could not save this request right now. Please try again.";
  success.classList.add("show");
 }finally{
  submit.disabled=false;submit.textContent=oldLabel;
 }
});'''

text = text[:start] + new + text[end:]
text = text.replace(
    'No payment is required. SEEKVERA will save the request when secure storage is connected; email fallback remains available.',
    'No payment is required. Your request is saved securely and receives a reference number.'
)
p.write_text(text, encoding='utf-8')
