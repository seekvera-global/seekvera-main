from pathlib import Path
import re

VER='20260927-r88-live-voice-speaker-final'

# ---------------- voice-ai.js ----------------
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')

# Script of the actual reply must win over stale/wrong metadata when choosing TTS language.
start=s.find('function localeForText(t,requested){')
end=s.find('\nfunction voices()',start)
if start<0 or end<0:
    raise SystemExit('localeForText block missing')
locale_block=r'''function localeForText(t,requested){
  t=typeof t==='string'?t:'';
  if(/[\u0600-\u06ff]/.test(t))return 'ar-SA';
  if(/[\u4e00-\u9fff]/.test(t))return 'zh-CN';
  if(/[\u3040-\u30ff]/.test(t))return 'ja-JP';
  if(/[\uac00-\ud7af]/.test(t))return 'ko-KR';
  if(/[\u0900-\u097f]/.test(t))return 'hi-IN';
  if(/[\u0980-\u09ff]/.test(t))return 'bn-BD';
  if(/[\u0400-\u04ff]/.test(t))return 'ru-RU';
  if(/[\u0590-\u05ff]/.test(t))return 'he-IL';
  if(/[\u0370-\u03ff]/.test(t))return 'el-GR';
  if(/[\u0e00-\u0e7f]/.test(t))return 'th-TH';
  if(/[\u1200-\u137f]/.test(t))return 'am-ET';
  const r=codeOf(requested);if(r)return LANGS[r]||r;
  return locale()
}'''
s=s[:start]+locale_block+s[end:]

# Fast browser-side multilingual fallback. This is independent from app/UI language.
if 'async function puterAutoTranscribe(blob)' not in s:
    anchor='async function seekveraAutoTranscribe(blob){'
    i=s.find(anchor)
    if i<0: raise SystemExit('seekveraAutoTranscribe anchor missing')
    helper=r'''let puterLoaderR88=null;
function ensurePuterR88(){
  if(window.puter?.ai?.speech2txt)return Promise.resolve(true);
  if(puterLoaderR88)return puterLoaderR88;
  puterLoaderR88=new Promise(resolve=>{
    let done=false;const finish=v=>{if(done)return;done=true;resolve(!!v)};
    const existing=document.querySelector('script[data-seekvera-puter]');
    if(existing){existing.addEventListener('load',()=>finish(window.puter?.ai?.speech2txt),{once:true});existing.addEventListener('error',()=>finish(false),{once:true});setTimeout(()=>finish(window.puter?.ai?.speech2txt),4500);return}
    const sc=document.createElement('script');sc.src='https://js.puter.com/v2/';sc.async=true;sc.dataset.seekveraPuter='1';sc.onload=()=>finish(window.puter?.ai?.speech2txt);sc.onerror=()=>finish(false);document.head.appendChild(sc);setTimeout(()=>finish(window.puter?.ai?.speech2txt),4500)
  });
  return puterLoaderR88
}
async function puterAutoTranscribe(blob){
  if(!await ensurePuterR88())throw Error('browser multilingual ASR unavailable');
  const task=window.puter.ai.speech2txt(blob,{provider:'xai'}),timeout=new Promise((_,reject)=>setTimeout(()=>reject(Error('browser ASR timeout')),11000));
  const r=await Promise.race([task,timeout]),text=String(typeof r==='string'?r:(r?.text||r?.transcript||'')).trim();
  if(!text)throw Error('browser multilingual ASR returned no text');
  const language=String(r?.language||'auto');rememberChatVoiceLanguage(language,text);return{text,language,engine:'puter-xai-auto'}
}
'''
    s=s[:i]+helper+s[i:]

# Replace the slow 30s + 36s serial ASR loop and local-WASM hang with a quick race.
start=s.find('async function seekveraAutoTranscribe(blob){')
end=s.find('\nfunction localeForText(',start)
if start<0 or end<0:
    raise SystemExit('ASR block boundary missing')
asr=r'''async function seekveraAutoTranscribe(blob){
  const audio=await blobDataURL(blob),ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),14000);
  try{
    const res=await fetch(apiBase()+'/api/transcribe?auto=1&r88=1',{method:'POST',headers:{'content-type':'application/json','cache-control':'no-store'},body:JSON.stringify({audio,language:'auto'}),signal:ctl.signal,cache:'no-store'});
    const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.reason||d.error||'server transcription failed');
    rememberChatVoiceLanguage(d.language||d.detectedLanguage,d.text);
    return{text:String(d.text).trim(),language:String(d.language||d.detectedLanguage||'auto'),engine:'seekvera-whisper-auto'}
  }finally{clearTimeout(to)}
}
async function automaticMultilingualTranscribe(blob){
  try{return await Promise.any([seekveraAutoTranscribe(blob),puterAutoTranscribe(blob)])}
  catch(_){throw Error('automatic multilingual transcription unavailable')}
}'''
s=s[:start]+asr+s[end:]

# On a voice turn / manual speaker tap, use server MP3 first (reliable on Android),
# then native speech as fallback. Speak every chunk, not only the first 190 chars.
old="function speak(text,l,force=false){lastAnswer=typeof text==='string'?text:'';lastLocale=localeForText(lastAnswer,l);const chunks=splitSpeech(lastAnswer);if(force){muted=false;localStorage.setItem('seekvera_voice_muted','0');localStorage.setItem('seekvera_voice_mode','1');updateSpeakerButtons()}if(muted||!chunks.length){if(force)voiceConversation=false;return}const token=++speakToken;if(nativeSpeak(chunks,token))return;serverSpeak(lastAnswer,lastLocale,token,true)}"
new=r'''async function serverSpeakSequence(chunks,loc,token){
  for(let i=0;i<chunks.length;i++){
    if(token!==speakToken||muted)return false;
    const ok=await serverSpeak(chunks[i],loc,token,i===chunks.length-1);if(!ok)return false
  }
  return true
}
function speak(text,l,force=false){
  lastAnswer=typeof text==='string'?text:'';lastLocale=localeForText(lastAnswer,l);const chunks=splitSpeech(lastAnswer);
  if(force){muted=false;localStorage.setItem('seekvera_voice_muted','0');localStorage.setItem('seekvera_voice_mode','1');updateSpeakerButtons()}
  if(muted||!chunks.length){if(force)voiceConversation=false;return}
  const token=++speakToken,voiceMode=localStorage.getItem('seekvera_voice_mode')==='1',mobile=/Android|iPhone|iPad|iPod/i.test(navigator.userAgent),serverFirst=force||voiceConversation||voiceMode||mobile;
  if(serverFirst){serverSpeakSequence(chunks,lastLocale,token).then(ok=>{if(!ok&&token===speakToken&&!muted)nativeSpeak(chunks,token)}).catch(()=>{if(token===speakToken&&!muted)nativeSpeak(chunks,token)});return}
  if(nativeSpeak(chunks,token))return;serverSpeakSequence(chunks,lastLocale,token)
}'''
if old not in s:
    raise SystemExit('speak function anchor missing')
s=s.replace(old,new,1)

# Send a successful transcript straight into the unified chat controller as a voice turn.
old="if(i){i.value=String(d.text).trim();i.placeholder='Message SEEKVERA AI…';if(i.value){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>i.form?.requestSubmit?.(),35)}}"
new="if(i){const spoken=String(d.text).trim();i.value=spoken;i.placeholder='Message SEEKVERA AI…';if(spoken){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>{if(window.SEEKVERA_R31?.submitAI)window.SEEKVERA_R31.submitAI(spoken,{fromVoice:true});else i.form?.requestSubmit?.()},35)}}"
if old not in s:
    raise SystemExit('voice submit anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

# ---------------- worker-r76.js ----------------
p=Path('worker-r76.js')
w=p.read_text(encoding='utf-8')
w=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",w,count=1)

# Bound each server ASR attempt so a quota/capacity problem cannot hold the UI for a minute.
old="for(const model of [ASR_PRIMARY,ASR_PRIMARY,ASR_FALLBACK]){try{\n   const r=await env.AI.run(model,base),text=clean(r?.text||r?.result?.text||r?.result||'',5000);"
new="for(const model of [ASR_PRIMARY,ASR_FALLBACK]){try{\n   const r=await Promise.race([env.AI.run(model,base),new Promise((_,reject)=>setTimeout(()=>reject(Error('asr timeout')),8000))]),text=clean(r?.text||r?.result?.text||r?.result||'',5000);"
if old not in w:
    raise SystemExit('worker ASR loop anchor missing')
w=w.replace(old,new,1)

# If the public conversational fallback returns useful plain text instead of JSON,
# keep the natural answer rather than dropping to a canned "I understand your language" template.
old="if(br.ok){const obj=parseJSON(await br.text());if(obj&&clean(obj.reply,5000)){"
new="if(br.ok){const raw=await br.text(),obj=parseJSON(raw);if(obj&&clean(obj.reply,5000)){"
if old not in w:
    raise SystemExit('R87 pollinations JSON anchor missing')
w=w.replace(old,new,1)
anchor="       return{ok:true,response:reply,language,category:cat,route:ROUTES[cat]||ROUTES.general,countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'pollinations-private-conversation-fallback',fastPath:'r87-real-ai-fallback',liveData:false};\n     }}"
replace=anchor+"\n     const plain=clean(raw,5000);if(plain){const language=messageLanguage(message,''),meta=metaConversation(message),cat=(conversationOnly(message)||meta)?'general':(category(message)==='jobs'&&!employmentIntent(message)?'general':category(message));return{ok:true,response:plain,language,category:cat,route:ROUTES[cat]||ROUTES.general,countryAction:null,languageAction:null,model:'pollinations-private-conversation-plain',fastPath:'r88-natural-plain-fallback',liveData:false}}"
if anchor not in w:
    raise SystemExit('R87 pollinations return anchor missing')
w=w.replace(anchor,replace,1)

# Health marker.
needle="r87:true,r87Runtime:'latest-message-language-plus-real-ai-fallback',"
if needle not in w:
    raise SystemExit('R87 health marker missing')
w=w.replace(needle,"r88:true,r88Runtime:'fast-auto-asr-server-first-tts-natural-fallback',"+needle,1)
p.write_text(w,encoding='utf-8')

# ---------------- cache bust ----------------
p=Path('index.html')
h=p.read_text(encoding='utf-8')
h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
h=re.sub(r'voice-ai\.js\?v=[^"\s]+',f'voice-ai.js?v={VER}',h,count=1)
h=re.sub(r'r31-ui-polish\.js\?v=[^"\s]+',f'r31-ui-polish.js?v={VER}',h,count=1)
h=re.sub(r'sw\.js\?v=[^"\s]+',f'sw.js?v={VER}',h,count=1)
p.write_text(h,encoding='utf-8')

p=Path('sw.js')
sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1)
p.write_text(sw,encoding='utf-8')

print('R88 voice/speaker patch applied')
