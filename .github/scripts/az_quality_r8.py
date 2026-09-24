from pathlib import Path
import re

VER='20260924-az-r8'


def must_replace(s, old, new, label):
    if old not in s:
        if new in s:
            return s
        raise SystemExit(f'{label}: anchor not found')
    return s.replace(old, new, 1)

# -----------------------------------------------------------------------------
# 1) Voice: natural end-of-speech, no 12-second cut-off, 90-second hard ceiling.
# -----------------------------------------------------------------------------
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=must_replace(
    s,
    "let recognition=null,lastAnswer='',lastLocale='',muted=localStorage.getItem('seekvera_voice_muted')==='1',activeButton=null,voiceConversation=false,speakToken=0,recording=false,mediaRecorder=null,mediaStream=null,recordChunks=[],recordTimer=null;",
    "const VOICE_SILENCE_MS=2100,VOICE_MAX_MS=90000,VOICE_RMS_THRESHOLD=.018;\nlet recognition=null,lastAnswer='',lastLocale='',muted=localStorage.getItem('seekvera_voice_muted')==='1',activeButton=null,voiceConversation=false,speakToken=0,recording=false,mediaRecorder=null,mediaStream=null,recordChunks=[],recordTimer=null,speechSilenceTimer=null,speechHardTimer=null,audioCtx=null,audioAnalyser=null,audioSource=null,audioRaf=0,heardVoice=false,lastVoiceAt=0,recordStartedAt=0;",
    'voice state')

old="function releaseStream(){if(recordTimer){clearTimeout(recordTimer);recordTimer=null}try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false)}"
new="""function stopAudioMonitor(){if(audioRaf){cancelAnimationFrame(audioRaf);audioRaf=0}try{audioSource?.disconnect?.()}catch(_){}audioSource=null;audioAnalyser=null;try{audioCtx?.close?.()}catch(_){}audioCtx=null;heardVoice=false;lastVoiceAt=0;recordStartedAt=0}
function clearSpeechTimers(){if(speechSilenceTimer){clearTimeout(speechSilenceTimer);speechSilenceTimer=null}if(speechHardTimer){clearTimeout(speechHardTimer);speechHardTimer=null}}
function releaseStream(){if(recordTimer){clearTimeout(recordTimer);recordTimer=null}clearSpeechTimers();stopAudioMonitor();try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false)}
function startAudioMonitor(stream,onSilence){try{const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;audioCtx=new AC();audioSource=audioCtx.createMediaStreamSource(stream);audioAnalyser=audioCtx.createAnalyser();audioAnalyser.fftSize=1024;audioAnalyser.smoothingTimeConstant=.25;audioSource.connect(audioAnalyser);const data=new Float32Array(audioAnalyser.fftSize);recordStartedAt=performance.now();const tick=()=>{if(!audioAnalyser||!recording)return;audioAnalyser.getFloatTimeDomainData(data);let sum=0;for(let i=0;i<data.length;i++)sum+=data[i]*data[i];const rms=Math.sqrt(sum/data.length),now=performance.now();if(rms>VOICE_RMS_THRESHOLD){heardVoice=true;lastVoiceAt=now}if(heardVoice&&lastVoiceAt&&now-lastVoiceAt>=VOICE_SILENCE_MS&&now-recordStartedAt>700){onSilence();return}audioRaf=requestAnimationFrame(tick)};audioRaf=requestAnimationFrame(tick)}catch(_){stopAudioMonitor()}}"""
s=must_replace(s,old,new,'voice release/monitor')

m=re.search(r"async function serverVoice\(targetId,button\)\{.*?\}\n\nfunction start\(targetId,button\)\{.*?\}\nfunction toggleMute",s,re.S)
if not m:
    raise SystemExit('voice server/start block not found')
replacement=r'''async function serverVoice(targetId,button){
  activeButton=button||document.getElementById('aiChatMic')||document.querySelector('.sv-global-compose .mic');
  const i=document.getElementById(targetId||'aiChatInput');
  if(recording){try{mediaRecorder?.stop()}catch(_){releaseStream()}return}
  if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){voiceConversation=false;if(i)i.placeholder='Voice input is unavailable on this browser — please type your message.';return}
  try{
    stopSpeech();enableVoiceConversation();
    mediaStream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true}});
    recordChunks=[];let opts={};
    for(const mt of ['audio/webm;codecs=opus','audio/mp4','audio/webm','audio/ogg;codecs=opus']){try{if(MediaRecorder.isTypeSupported?.(mt)){opts={mimeType:mt};break}}catch(_){}}
    mediaRecorder=new MediaRecorder(mediaStream,opts);recording=true;
    mediaRecorder.ondataavailable=e=>{if(e.data?.size)recordChunks.push(e.data)};
    mediaRecorder.onerror=()=>{if(i)i.placeholder='Microphone recording failed — please type your message.';voiceConversation=false;releaseStream()};
    mediaRecorder.onstop=async()=>{
      const chunks=[...recordChunks],type=mediaRecorder?.mimeType||chunks[0]?.type||'audio/webm';
      if(recordTimer){clearTimeout(recordTimer);recordTimer=null}stopAudioMonitor();
      try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false);
      if(!chunks.length){voiceConversation=false;if(i)i.placeholder='No speech recorded — tap the microphone and try again.';return}
      try{
        if(i)i.placeholder='Transcribing your voice…';
        const blob=new Blob(chunks,{type}),audio=await blobDataURL(blob);
        const res=await fetch(apiBase()+'/api/transcribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({audio,language:selectedLang()||'auto'})});
        const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.error||'transcription failed');
        if(i){i.value=String(d.text).trim();i.placeholder='Message SEEKVERA AI…';if(i.value)setTimeout(()=>i.form?.requestSubmit?.(),80)}
      }catch(e){voiceConversation=false;if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}
    };
    mediaRecorder.start(250);setMic(true);if(i)i.placeholder='Listening… I will send after you finish speaking';
    startAudioMonitor(mediaStream,()=>{if(recording&&mediaRecorder?.state==='recording')mediaRecorder.stop()});
    recordTimer=setTimeout(()=>{if(recording&&mediaRecorder?.state==='recording')mediaRecorder.stop()},VOICE_MAX_MS);
  }catch(e){voiceConversation=false;releaseStream();if(i)i.placeholder=e?.name==='NotAllowedError'?'Microphone permission was not allowed — please enable it or type your message.':'Microphone is unavailable — please type your message.'}
}

function start(targetId,button){
  if(recording){try{mediaRecorder?.stop()}catch(_){releaseStream()}return}
  if(recognition){try{recognition.stop()}catch(_){}return}
  stopSpeech();enableVoiceConversation();clearSpeechTimers();
  activeButton=button||document.getElementById('aiChatMic')||document.querySelector('.sv-global-compose .mic');
  const i=document.getElementById(targetId||'aiChatInput');
  if(!SpeechRecognition){serverVoice(targetId,activeButton);return}
  const r=new SpeechRecognition();recognition=r;r.lang=locale();r.interimResults=true;r.continuous=true;r.maxAlternatives=1;
  let final='',hadError=false,heardAny=false;
  const scheduleSilence=()=>{if(speechSilenceTimer)clearTimeout(speechSilenceTimer);speechSilenceTimer=setTimeout(()=>{try{if(recognition===r)r.stop()}catch(_){}},VOICE_SILENCE_MS)};
  r.onstart=()=>{setMic(true);speechHardTimer=setTimeout(()=>{try{if(recognition===r)r.stop()}catch(_){}},VOICE_MAX_MS)};
  r.onresult=e=>{let interim='';heardAny=true;for(let x=e.resultIndex;x<e.results.length;x++){const t=e.results[x][0].transcript;if(e.results[x].isFinal)final+=(final?' ':'')+t;else interim+=t}if(i)i.value=(final+(interim?((final?' ':'')+interim):'')).trim();scheduleSilence()};
  r.onerror=e=>{if(!['no-speech','aborted'].includes(e?.error))hadError=true;if(e?.error==='no-speech'&&!heardAny)voiceConversation=false};
  r.onend=()=>{clearSpeechTimers();setMic(false);if(recognition===r)recognition=null;const q=i?.value?.trim();if(q&&!hadError)setTimeout(()=>i.form?.requestSubmit?.(),90);else if(!q)voiceConversation=false};
  try{r.start()}catch(_){recognition=null;voiceConversation=false;clearSpeechTimers();setMic(false);serverVoice(targetId,activeButton)}
}
function toggleMute'''
s=s[:m.start()]+replacement+s[m.end()-len('function toggleMute'):]
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 2) AI: keep short conversation history, infer intent from prior turns, do not repeat.
#    Add a dedicated UI translation endpoint so translation is not routed like chat.
# -----------------------------------------------------------------------------
p=Path('worker.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,1)

post_guard="if(request.method!=='POST')return j(request,{ok:false,error:'Method not allowed'},405);"
ui_route=r'''if(u.pathname==='/api/ui-translate'){try{if(!env.AI)return j(request,{ok:false,error:'AI binding unavailable'},503);const b=await request.json(),language=clean(b.language,80),strings=Array.isArray(b.strings)?b.strings.slice(0,12).map(x=>clean(x,700)):[];if(!language||!strings.length||strings.some(x=>!x))return j(request,{ok:false,error:'Language and strings are required'},400);const sys='You are SEEKVERA UI translator. LANGUAGE LOCK: translate every supplied interface string fully into '+language+'. Return ONLY one valid JSON array of exactly '+strings.length+' strings, same order. No markdown, no keys, no explanation. Preserve SEEKVERA, URLs, currency codes, model names, emojis, punctuation placeholders and numbers. Translate labels, buttons, headings, descriptions and accessibility text naturally; never concatenate all items into one string.';let text='';try{text=out(await env.AI.run(PRIMARY,{messages:[{role:'system',content:sys},{role:'user',content:JSON.stringify(strings)}],temperature:0,max_completion_tokens:1200}))}catch(e){const rr=await ai(env,[{role:'system',content:sys},{role:'user',content:JSON.stringify(strings)}],1200,0);text=rr.response}const a=text.indexOf('['),z=text.lastIndexOf(']');if(a<0||z<=a)return j(request,{ok:false,error:'Translation format error',retryable:true},502);const arr=JSON.parse(text.slice(a,z+1));if(!Array.isArray(arr)||arr.length!==strings.length||arr.some(x=>typeof x!=='string'||!x.trim()))return j(request,{ok:false,error:'Translation count mismatch',retryable:true},502);return j(request,{ok:true,language,translations:arr.map(x=>String(x).trim())})}catch(e){return j(request,{ok:false,error:'UI translation temporarily unavailable',retryable:true},503)}}
'''
if "u.pathname==='/api/ui-translate'" not in s:
    s=must_replace(s,post_guard,post_guard+'\n'+ui_route,'ui translate route')

old="if(u.pathname==='/api/ai'){try{const b=await request.json(),m=clean(b.message??b.prompt,3500);if(!m)return j(request,{ok:false,error:'Message is required'},400);"
new="if(u.pathname==='/api/ai'){try{const b=await request.json(),m=clean(b.message??b.prompt,3500);if(!m)return j(request,{ok:false,error:'Message is required'},400);const hist=Array.isArray(b.history)?b.history.slice(-12).map(x=>({role:x?.role==='assistant'?'assistant':'user',content:clean(x?.content,1800)})).filter(x=>x.content):[];const contextText=(hist.map(x=>x.content).join(' ')+' '+m).trim();"
s=must_replace(s,old,new,'ai history parse')
s=must_replace(s,"const detected=await detectedLanguage(env,m,b.language),c=category(m),p=","const detected=await detectedLanguage(env,m,b.language),c=category(contextText),p=",'ai history category')
s=s.replace('Do not repeat a question or fact the user has already answered. Ask at most one useful follow-up question only when an essential detail is truly missing.', 'Use the supplied conversation history as memory for the current exchange. Do not repeat a question or fact the user has already answered. If the latest message is a short answer such as a job title, product type, city or budget, combine it with the prior turns instead of treating it as a new unrelated request. Ask at most one useful follow-up question only when an essential detail is truly missing.',1)
old="const r=await ai(env,[{role:'system',content:p},{role:'system',content:lock},{role:'user',content:m}],480,.16);"
new="const appctx='APP CONTEXT: selected country/market = '+clean(b.country,120)+'. Search scope = '+clean(b.scope,40)+'. Use this context when relevant; do not ask for it again if already known.';const r=await ai(env,[{role:'system',content:p},{role:'system',content:lock},{role:'system',content:appctx},...hist,{role:'user',content:m}],520,.14);"
s=must_replace(s,old,new,'ai history messages')
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 3) Home AI and global dock AI send the last turns to the server.
# -----------------------------------------------------------------------------
p=Path('superapp.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",s,1)
anchor="function chatAdd(role,text,extra=''){const msgs=$('#aiMessages');if(!msgs)return null;const m=document.createElement('div');m.className=`ai-msg ${role}${extra?' '+extra:''}`;m.textContent=String(text||'');msgs.appendChild(m);msgs.scrollTop=msgs.scrollHeight;return m}"
extra=anchor+"\nfunction chatHistory(){const msgs=$('#aiMessages');if(!msgs)return[];return[...msgs.querySelectorAll('.ai-msg')].filter(x=>!x.classList.contains('thinking')).slice(-12).map(x=>({role:x.classList.contains('user')?'user':'assistant',content:clean(x.textContent,1800)})).filter(x=>x.content)}"
if 'function chatHistory()' not in s:
    s=must_replace(s,anchor,extra,'home chat history helper')
s=must_replace(s,"async function askAI(q){q=clean(q,1800);if(!q)return;const ans=$('#aiAnswer'),actions=$('#aiActions');if(actions)actions.innerHTML='';chatAdd('user',q);","async function askAI(q){q=clean(q,1800);if(!q)return;const history=chatHistory(),ans=$('#aiAnswer'),actions=$('#aiActions');if(actions)actions.innerHTML='';chatAdd('user',q);",'home ask history capture')
s=must_replace(s,"body:JSON.stringify({message:q,country,language:languageName(),scope:scope(),fast:true})","body:JSON.stringify({message:q,country,language:languageName(),scope:scope(),fast:true,history})",'home ask history send')
p.write_text(s,encoding='utf-8')

p=Path('global-ui.js')
s=p.read_text(encoding='utf-8')
anchor="function addMsg(box,role,text,thinking=false){const d=document.createElement('div');d.className=`sv-global-msg ${role}${thinking?' thinking':''}`;d.textContent=plain(text)||tx('SEEKVERA AI is temporarily unavailable. Please try again.');box.appendChild(d);box.scrollTop=box.scrollHeight;return d}"
extra=anchor+"\nfunction globalHistory(box){return[...box.querySelectorAll('.sv-global-msg')].filter(x=>!x.classList.contains('thinking')).slice(-12).map(x=>({role:x.classList.contains('user')?'user':'assistant',content:String(x.textContent||'').trim().slice(0,1800)})).filter(x=>x.content)}"
if 'function globalHistory(' not in s:
    s=must_replace(s,anchor,extra,'global history helper')
s=must_replace(s,"async function ask(box,input){const q=String(input.value||'').trim();if(!q)return;input.value='';addMsg(box,'user',q);","async function ask(box,input){const q=String(input.value||'').trim();if(!q)return;const history=globalHistory(box);input.value='';addMsg(box,'user',q);",'global history capture')
s=must_replace(s,"body:JSON.stringify({message:q,country:country(),language:aiLanguageName(),scope:'worldwide',fast:true})","body:JSON.stringify({message:q,country:country(),language:aiLanguageName(),scope:'worldwide',fast:true,history})",'global history send')
s=s.replace("function assistantIntro(){return AI_INTRO[langCode()]||AI_INTRO.en}","function assistantIntro(){return AI_INTRO[langCode()]||tx(AI_INTRO.en)}",1)
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 4) i18n: dedicated translation API + arbitrary country language coverage.
# -----------------------------------------------------------------------------
p=Path('i18n-ui.js')
s=p.read_text(encoding='utf-8')
s=s.replace('sv_i18n_r7_','sv_i18n_r8_')
s=s.replace("const v=UI[l]||UI.en,c=document.getElementById('country')","const base=UI.en,v=UI[l]||base.map(src=>local(l,src)||cached(l,src)||src),c=document.getElementById('country')",1)
s=s.replace("else if(SUPPORTED.includes(o.value)){try{o.textContent=dn?.of(o.value)||LANG_NAME[o.value]||o.textContent}catch{}}","else if(o.value&&o.value!=='auto'){try{o.textContent=dn?.of(o.value)||LANG_NAME[o.value]||o.textContent}catch{}}",1)
pat=r"async function translateBatch\(l,batch\)\{.*?\}\nasync function aiTranslate"
new=r'''async function translateBatch(l,batch){let name=LANG_NAME[l]||l;try{name=LANG_NAME[l]||new Intl.DisplayNames(['en'],{type:'language'}).of(l)||l}catch{};try{const r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:name,strings:batch})});const d=await r.json().catch(()=>null);if(!r.ok||!Array.isArray(d?.translations)||d.translations.length!==batch.length)return null;const arr=d.translations.map(x=>validTranslation(x));return arr.every(Boolean)?arr:null}catch{return null}}
async function aiTranslate'''
s2,n=re.subn(pat,new,s,count=1,flags=re.S)
if n!=1:
    if '/api/ui-translate' not in s:
        raise SystemExit('translateBatch block not found')
else:
    s=s2
s=s.replace('i+=6){const batch=unique.slice(i,i+6)','i+=8){const batch=unique.slice(i,i+8)',1)
s=s.replace('sw.js?v=20260924-country-sync-r7',f'sw.js?v={VER}')
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 5) Complete, horizontally scrollable department line + complete category grid.
# -----------------------------------------------------------------------------
DEPTS=[
('✨','AI & Search','index.html'),('🛒','Marketplace','marketplace.html'),('✈️','Travel','travel.html'),('🛫','Flights','travel.html?q=flights'),('🏨','Hotels','travel.html?q=hotels'),('🗺️','Tourism','tourism.html'),('🏠','Property','property.html'),('🚘','Cars & Auto','cars-auto.html'),('💼','Jobs','jobs.html'),('🛍️','Shopping','shopping.html'),('🍽️','Restaurants & Food','restaurants-food.html'),('🧰','Local Services','local-services.html'),('🏗️','Equipment & Machinery','marketplace.html?q=equipment'),('⛵','Boats & Marine','marketplace.html?q=boats'),('🚢','Import & Export','import-export.html'),('📦','Shipping & Logistics','shipping-logistics.html'),('💻','Business Software','business-software.html'),('🧩','Software','software.html'),('🌐','Websites & Hosting','web-hosting.html'),('☀️','Solar & Energy','solar.html'),('🎓','Education','education.html'),('🏥','Health','health.html'),('💳','Money & Insurance','money-insurance.html'),('🎬','Entertainment','entertainment.html'),('📰','News & Media','media.html'),('🎮','Games','games.html'),('📶','Connectivity','connectivity.html'),('📡','Free Wi‑Fi','wifi.html'),('🤝','AI Deal Agent','deal-agent.html'),('📍','Everyday','everyday.html'),('📲','Scan / QR','scan.html'),('＋','Post Ad','post-ad.html'),('🚀','Promote / Business','seller-plans.html')]

def dept_links(cls='r8-dept-link'):
    return ''.join(f'<a class="{cls}" href="{href}"><span>{icon}</span>{name}</a>' for icon,name,href in DEPTS)

p=Path('index.html')
s=p.read_text(encoding='utf-8')
strip='<nav class="r8-department-strip" aria-label="All SEEKVERA departments" data-r8-departments="complete">'+dept_links()+'</nav>'
if 'data-r8-departments="complete"' not in s:
    s=must_replace(s,'</header>','</header>\n'+strip,'department strip')
nav_start=s.find('<nav class="r5-category-list">')
if nav_start<0: raise SystemExit('sidebar nav start missing')
nav_end=s.find('</nav>',nav_start)
if nav_end<0: raise SystemExit('sidebar nav end missing')
sidebar='<nav class="r5-category-list" data-r8-sidebar="complete">'+dept_links('r5-dept-link')+'</nav>'
s=s[:nav_start]+sidebar+s[nav_end+6:]
cat_start=s.find('<section class="r5-section" id="categories">')
if cat_start<0: raise SystemExit('categories section missing')
grid_start=s.find('<div class="r5-grid">',cat_start)
grid_end=s.find('</div>\n      </section>',grid_start)
if grid_start<0 or grid_end<0: raise SystemExit('category grid bounds missing')
tiles=[]
for icon,name,href in DEPTS:
    if name in ('AI & Search','Post Ad','Promote / Business'):
        continue
    desc={
      'Marketplace':'Buy, sell and compare worldwide','Travel':'Trips, transport and stays','Flights':'Search flight routes','Hotels':'Search stays worldwide','Tourism':'Places and experiences','Property':'Homes, land and rentals','Cars & Auto':'Vehicles, parts and auto','Jobs':'Local and global careers','Shopping':'Products and deals','Restaurants & Food':'Food, cafes and dining','Local Services':'Everyday skilled help','Equipment & Machinery':'Machines and equipment','Boats & Marine':'Boats and marine listings','Import & Export':'Factories and suppliers','Shipping & Logistics':'Freight, cargo and delivery','Business Software':'POS, accounting and SaaS','Software':'Apps and digital tools','Websites & Hosting':'Domains, hosting and websites','Solar & Energy':'Power and energy solutions','Education':'Schools, courses and skills','Health':'Clinics, labs and pharmacies','Money & Insurance':'Licensed provider discovery','Entertainment':'Movies, music and family','News & Media':'Trusted media and official sources','Games':'Play inside SEEKVERA','Connectivity':'Internet, SIM and eSIM','Free Wi‑Fi':'Public Wi‑Fi discovery','AI Deal Agent':'Sourcing and business missions','Everyday':'Nearby daily needs','Scan / QR':'Share and install SEEKVERA'
    }.get(name,'Explore worldwide')
    tiles.append(f'<a class="r5-tile" href="{href}"><div class="r5-thumb">{icon}</div><div class="r5-tile-body"><b>{name}</b><small>{desc}</small></div></a>')
newgrid='<div class="r5-grid" data-r8-grid="complete">'+''.join(tiles)+'</div>'
s=s[:grid_start]+newgrid+s[grid_end+6:]
p.write_text(s,encoding='utf-8')

# Hub gets one complete A-Z department directory near the top.
p=Path('hub.html')
s=p.read_text(encoding='utf-8')
if 'data-r8-hub-departments="complete"' not in s:
    cards=''.join(f'<a class="card" href="{href}"><span class="icon">{icon}</span><b>{name}</b><small>Open this SEEKVERA department.</small></a>' for icon,name,href in DEPTS)
    block='<h2>All departments A–Z</h2><section class="grid" data-r8-hub-departments="complete">'+cards+'</section>'
    s=must_replace(s,'<h2 id="mainTitle">',block+'<h2 id="mainTitle">','hub department directory')
p.write_text(s,encoding='utf-8')

# Department strip style.
p=Path('home-marketplace-r5.css')
s=p.read_text(encoding='utf-8')
if 'SEEKVERA R8 COMPLETE DEPARTMENT STRIP' not in s:
    s+='''\n/* SEEKVERA R8 COMPLETE DEPARTMENT STRIP */\n.r8-department-strip{position:sticky;top:60px;z-index:39;display:flex;gap:7px;overflow-x:auto;overscroll-behavior-inline:contain;padding:8px max(10px,calc((100vw - 1440px)/2));background:rgba(255,255,255,.96);border-bottom:1px solid #e4e8ed;scrollbar-width:thin}.r8-dept-link{display:inline-flex;align-items:center;gap:5px;flex:0 0 auto;white-space:nowrap;border:1px solid #dfe5eb;background:#fff;border-radius:999px;padding:7px 10px;font-size:.78rem;font-weight:800;color:#162238}.r8-dept-link:hover{border-color:#7db6a0;background:#f5fff9}.r5-category-list .r5-dept-link{display:flex;align-items:center;gap:7px}.r5-category-list .r5-dept-link span{min-width:20px;text-align:center}@media(max-width:760px){.r8-department-strip{top:0;padding:6px 8px}.r8-dept-link{font-size:.72rem;padding:6px 9px}.r5-category-list{max-height:52vh;overflow:auto}}\n'''
p.write_text(s,encoding='utf-8')

# -----------------------------------------------------------------------------
# 6) Cache bust every public page and PWA runtime.
# -----------------------------------------------------------------------------
for hp in Path('.').glob('*.html'):
    if hp.name.lower().startswith('google'):
        continue
    t=hp.read_text(encoding='utf-8')
    t=t.replace('20260924-country-sync-r7',VER)
    hp.write_text(t,encoding='utf-8')
for fn in ['sw.js','manifest.webmanifest']:
    q=Path(fn)
    if q.exists():
        t=q.read_text(encoding='utf-8').replace('20260924-country-sync-r7',VER)
        q.write_text(t,encoding='utf-8')

print('R8 A-Z quality upgrade applied.')
