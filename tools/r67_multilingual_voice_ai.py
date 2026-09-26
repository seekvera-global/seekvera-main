from pathlib import Path
import re

OLD='20260926-r66-final-ai-command-language'
VER='20260926-r67-multilingual-voice-ai'

# 1) Voice: automatic multilingual recording. Race SEEKVERA/Cloudflare ASR with
# a browser-side Puter/xAI transcription fallback, then remember the detected
# conversation language. Native SpeechRecognition remains the last fallback.
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
anchor="async function serverVoice(targetId,button,fallbackNative=false){"
helper=r'''let puterLoader=null;
function ensurePuter(){
  if(window.puter?.ai?.speech2txt)return Promise.resolve(true);
  if(puterLoader)return puterLoader;
  puterLoader=new Promise(resolve=>{
    let done=false;const finish=v=>{if(done)return;done=true;resolve(v)};
    const existing=document.querySelector('script[data-seekvera-puter]');
    if(existing){existing.addEventListener('load',()=>finish(!!window.puter?.ai?.speech2txt),{once:true});existing.addEventListener('error',()=>finish(false),{once:true});setTimeout(()=>finish(!!window.puter?.ai?.speech2txt),5000);return}
    const sc=document.createElement('script');sc.src='https://js.puter.com/v2/';sc.async=true;sc.dataset.seekveraPuter='1';sc.onload=()=>finish(!!window.puter?.ai?.speech2txt);sc.onerror=()=>finish(false);document.head.appendChild(sc);setTimeout(()=>finish(!!window.puter?.ai?.speech2txt),5000)
  });
  return puterLoader
}
async function puterTranscribe(blob){
  if(!await ensurePuter())throw Error('puter unavailable');
  const task=window.puter.ai.speech2txt(blob,{provider:'xai'});
  const timeout=new Promise((_,reject)=>setTimeout(()=>reject(Error('puter transcription timeout')),7000));
  const r=await Promise.race([task,timeout]);
  const text=String(typeof r==='string'?r:(r?.text||r?.transcript||'')).trim();
  if(!text)throw Error('puter returned no speech');
  return{text,language:String(r?.language||'auto'),engine:'puter-xai'}
}
async function seekveraTranscribe(blob){
  const audio=await blobDataURL(blob);
  const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),3500);
  try{
    const res=await fetch(apiBase()+'/api/transcribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({audio,language:'auto'}),signal:ctl.signal,cache:'no-store'});
    const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.error||'transcription failed');
    return{text:String(d.text).trim(),language:String(d.language||'auto'),engine:'seekvera-whisper'}
  }finally{clearTimeout(to)}
}
async function multilingualTranscribe(blob){
  // Both engines auto-detect the spoken language. Promise.any returns the first
  // successful transcript, so an exhausted Cloudflare quota does not make the
  // microphone English-only or force the user to change app country/language.
  try{return await Promise.any([seekveraTranscribe(blob),puterTranscribe(blob)])}
  catch(e){throw Error('automatic multilingual transcription unavailable')}
}
'''
if 'async function multilingualTranscribe(blob)' not in s:
    if anchor not in s: raise SystemExit('voice serverVoice anchor missing')
    s=s.replace(anchor,helper+anchor,1)

old_block="""      try{\n        if(i)i.placeholder='Transcribing your voice…';\n        const blob=new Blob(chunks,{type}),audio=await blobDataURL(blob);\n        const signal=(typeof AbortSignal!=='undefined'&&AbortSignal.timeout)?AbortSignal.timeout(5000):undefined;const res=await fetch(apiBase()+'/api/transcribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({audio,language:'auto'}),...(signal?{signal}:{})});\n        const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.error||'transcription failed');\n        if(i){i.value=String(d.text).trim();i.placeholder='Message SEEKVERA AI…';if(i.value){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>i.form?.requestSubmit?.(),45)}}\n      }catch(e){voiceConversation=false;if(fallbackNative&&SpeechRecognition){if(i)i.placeholder='Switching to phone voice recognition…';setTimeout(()=>start(targetId,button,true),80)}else if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"""
new_block="""      try{\n        if(i)i.placeholder='Understanding your language…';\n        const blob=new Blob(chunks,{type}),d=await multilingualTranscribe(blob);\n        rememberChatVoiceLanguage(d.language,d.text);\n        if(i){i.value=String(d.text).trim();i.placeholder='Message SEEKVERA AI…';if(i.value){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>i.form?.requestSubmit?.(),35)}}\n      }catch(e){voiceConversation=false;if(fallbackNative&&SpeechRecognition){if(i)i.placeholder='Trying phone voice recognition…';setTimeout(()=>start(targetId,button,true),60)}else if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"""
if old_block in s:s=s.replace(old_block,new_block,1)
elif 'const blob=new Blob(chunks,{type}),d=await multilingualTranscribe(blob);' not in s:raise SystemExit('voice transcription block missing')
p.write_text(s,encoding='utf-8')

# 2) AI text: stop burning multiple Cloudflare models in parallel. A single fast
# model gets a short latency budget; public zero-cost multilingual fallback is next.
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8').replace(OLD,VER)
old="async function staggeredAI(env,messages){const first=runModel(env,FAST,messages,220);const second=(async()=>{await sleep(220);return runModel(env,LIGHT,messages,220)})();const timeout=(async()=>{await sleep(2200);throw Error('ai latency budget')})();try{return await Promise.race([Promise.any([first,second]),timeout])}catch{try{return await Promise.race([runModel(env,STRONG,messages,220),(async()=>{await sleep(850);throw Error('fallback latency budget')})()])}catch{return null}}}"
new="async function staggeredAI(env,messages){try{return await Promise.race([runModel(env,FAST,messages,220),(async()=>{await sleep(1400);throw Error('ai latency budget')})()])}catch{return null}}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('staggeredAI anchor missing')
s=s.replace('AbortSignal.timeout(6000)','AbortSignal.timeout(3500)')
s=s.replace("h.set('x-seekvera-release','r65-worldwide-chat-language')","h.set('x-seekvera-release','r67-multilingual-voice-ai')")
p.write_text(s,encoding='utf-8')

# 3) Keep runtime/cache versions aligned everywhere.
for name in ('r24-ai-controller.js','r31-ui-polish.js','superapp.js','r60-runtime-guard.js','navigation.js','r66-final-controller.js','sw.js'):
    p=Path(name)
    if p.exists():p.write_text(p.read_text(encoding='utf-8').replace(OLD,VER),encoding='utf-8')
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    p.write_text(p.read_text(encoding='utf-8').replace(OLD,VER),encoding='utf-8')

print('R67 multilingual voice AI patch applied')
