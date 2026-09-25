from pathlib import Path

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')

old="if(navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){serverVoice(targetId,activeButton);return}if(!SpeechRecognition){voiceConversation=false;if(i)i.placeholder='Voice recognition is unavailable here — please type your message.';return}"
new="if(!SpeechRecognition){serverVoice(targetId,activeButton);return}"
if old not in s and new not in s:
    raise SystemExit('R57 native-first anchor missing')
s=s.replace(old,new,1)

old="const r=new SpeechRecognition();recognition=r;r.lang=locale();r.interimResults=true;r.continuous=true;r.maxAlternatives=1;"
new="const r=new SpeechRecognition();recognition=r;r.lang=locale();r.interimResults=true;r.continuous=false;r.maxAlternatives=1;"
if old not in s and new not in s:
    raise SystemExit('R57 recognition config anchor missing')
s=s.replace(old,new,1)

old="r.onstart=()=>{setMic(true);speechHardTimer=setTimeout(()=>{try{if(recognition===r)r.stop()}catch(_){}},VOICE_MAX_MS)};"
new="r.onstart=()=>{setMic(true);if(i)i.placeholder='Listening…';speechHardTimer=setTimeout(()=>{try{if(recognition===r)r.stop()}catch(_){}},Math.min(VOICE_MAX_MS,30000))};"
if old not in s and new not in s:
    raise SystemExit('R57 onstart anchor missing')
s=s.replace(old,new,1)

old="r.onresult=e=>{let interim='';heardAny=true;for(let x=e.resultIndex;x<e.results.length;x++){const t=e.results[x][0].transcript;if(e.results[x].isFinal)final+=(final?' ':'')+t;else interim+=t}if(i)i.value=(final+(interim?((final?' ':'')+interim):'')).trim();scheduleSilence()};"
new="r.onresult=e=>{let interim='';heardAny=true;for(let x=e.resultIndex;x<e.results.length;x++){const t=e.results[x][0].transcript;if(e.results[x].isFinal)final+=(final?' ':'')+t;else interim+=t}if(i){i.value=(final+(interim?((final?' ':'')+interim):'')).trim();i.placeholder='Message SEEKVERA AI…'}if(final.trim()){try{if(recognition===r)r.stop()}catch(_){}}else scheduleSilence()};"
if old not in s and new not in s:
    raise SystemExit('R57 onresult anchor missing')
s=s.replace(old,new,1)

old="r.onerror=e=>{if(!['no-speech','aborted'].includes(e?.error))hadError=true;if(e?.error==='no-speech'&&!heardAny)voiceConversation=false};"
new="r.onerror=e=>{if(!['no-speech','aborted'].includes(e?.error))hadError=true;if(e?.error==='no-speech'&&!heardAny){voiceConversation=false;if(i)i.placeholder='I did not hear speech — tap the microphone and speak again.'}};"
if old not in s and new not in s:
    raise SystemExit('R57 onerror anchor missing')
s=s.replace(old,new,1)

old="r.onend=()=>{clearSpeechTimers();setMic(false);if(recognition===r)recognition=null;const q=i?.value?.trim();if(q&&!hadError){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>i.form?.requestSubmit?.(),45)}else if(!q)voiceConversation=false};"
new="r.onend=()=>{clearSpeechTimers();setMic(false);if(recognition===r)recognition=null;const q=i?.value?.trim();if(q){voiceReplyDeadline=Date.now()+90000;if(i)i.placeholder='Message SEEKVERA AI…';setTimeout(()=>i.form?.requestSubmit?.(),25)}else{voiceConversation=false;if(i&&hadError)i.placeholder='Voice recognition failed — tap the microphone and try again.'}};"
if old not in s and new not in s:
    raise SystemExit('R57 onend anchor missing')
s=s.replace(old,new,1)

old="const res=await fetch(apiBase()+'/api/transcribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({audio,language:'auto'})});"
new="const signal=(typeof AbortSignal!=='undefined'&&AbortSignal.timeout)?AbortSignal.timeout(5000):undefined;const res=await fetch(apiBase()+'/api/transcribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({audio,language:'auto'}),...(signal?{signal}:{})});"
if old not in s and new not in s:
    raise SystemExit('R57 server timeout anchor missing')
s=s.replace(old,new,1)

# Arabic dialect locale improvement for Lebanon and common regional markets while retaining all 98-language map.
old="function locale(){const e=document.getElementById('lang');let code=(e?.value||localStorage.getItem('seekvera_lang')||navigator.language||'en').toLowerCase();const label=e?.options?.[e.selectedIndex]?.textContent||'';if(code==='auto'||/auto|تلقائي|autom/i.test(label))return navigator.language||'en-US';code=codeOf(code)||code.split(/[-_]/)[0];return LANGS[code]||code||navigator.language||'en-US'}"
new="function locale(){const e=document.getElementById('lang');let code=(e?.value||localStorage.getItem('seekvera_lang')||navigator.language||'en').toLowerCase();const label=e?.options?.[e.selectedIndex]?.textContent||'';if(code==='auto'||/auto|تلقائي|autom/i.test(label))return navigator.language||'en-US';code=codeOf(code)||code.split(/[-_]/)[0];if(code==='ar'){const c=String(document.getElementById('country')?.value||localStorage.getItem('seekvera_country')||'').toUpperCase();const ar={LB:'ar-LB',EG:'ar-EG',AE:'ar-AE',SA:'ar-SA',JO:'ar-JO',IQ:'ar-IQ',KW:'ar-KW',QA:'ar-QA',BH:'ar-BH',OM:'ar-OM',MA:'ar-MA',DZ:'ar-DZ',TN:'ar-TN'};if(ar[c])return ar[c]}return LANGS[code]||code||navigator.language||'en-US'}"
if old not in s and new not in s:
    raise SystemExit('R57 locale anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

p=Path('worker-r31.js')
s=p.read_text(encoding='utf-8')
old="if(language==='Arabic')return`تمام. زر القسم المناسب موجود مباشرة تحت الرد. أعطني أهم تفصيل ناقص فقط حتى أنتقل للخطوة التالية بدل تكرار الكلام.`;return`Done. The direct section button is right below the reply. Give me only the one missing detail and I’ll move to the next step instead of repeating the same guidance.`"
new="if(language==='Arabic')return`تمام. سأنتقل بك مباشرة إلى القسم المناسب الآن. إذا بقي تفصيل ضروري واحد فقط، سأطلبه منك هناك.`;return`Done. I’m taking you directly to the right section now. If one essential detail is still missing, I’ll ask for it there.`"
if old not in s and new not in s:
    raise SystemExit('R57 fallback wording anchor missing')
s=s.replace(old,new,1)

# Force a fresh voice runtime URL in every served HTML page.
old="let text=await resp.text();text=text.replace(/2026-09-25 · R(?:20|31C|32)/g,'2026-09-25 · R35');"
new="let text=await resp.text();text=text.replace(/2026-09-25 · R(?:20|31C|32)/g,'2026-09-25 · R35');text=text.replace(/voice-ai\\.js(?:\\?[^\\\"'<> ]*)?/g,'voice-ai.js?v=20260926-r57-native-first');"
if old not in s and new not in s:
    raise SystemExit('R57 HTML cache-bust anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

p=Path('sw.js')
s=p.read_text(encoding='utf-8')
# Replace current R56 cache marker when present.
s=s.replace('seekvera-r56-global-ai-core-20260926','seekvera-r57-native-first-voice-20260926')
p.write_text(s,encoding='utf-8')
print('R57 native-first voice patch applied')
