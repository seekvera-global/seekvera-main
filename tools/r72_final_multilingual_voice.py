from pathlib import Path
import re

OLD='20260926-r66-final-ai-command-language'
VER='20260926-r72-true-multilingual-voice'

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)

# Remember the language of prior typed chat so native Android recognition never
# blindly falls back to English for a returning Arabic/French/etc conversation.
anchor="function localeForText(t,requested){"
seed=r'''function seedVoiceLanguageFromConversation(){
  try{
    const saved=codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'');if(saved&&LANGS[saved])return saved;
    const rows=JSON.parse(localStorage.getItem('seekvera_ai_chat_v1')||'[]');
    if(Array.isArray(rows))for(let n=rows.length-1;n>=0;n--){const x=rows[n];if(x?.role!=='user')continue;rememberChatVoiceLanguage('',x?.text||x?.content||'');const c=codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'');if(c&&LANGS[c])return c}
    const msgs=[...document.querySelectorAll('#aiMessages .ai-msg.user,.sv-chat-messages .ai-msg.user')];
    for(let n=msgs.length-1;n>=0;n--){rememberChatVoiceLanguage('',msgs[n].textContent||'');const c=codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'');if(c&&LANGS[c])return c}
  }catch(_){}
  return''
}
let localWhisperPromise=null;
async function localWhisperEngine(){
  if(localWhisperPromise)return localWhisperPromise;
  localWhisperPromise=(async()=>{
    const mod=await import('/patched-transformers.js?v=20260926-r72-true-multilingual-voice');
    mod.env.remoteHost=location.origin+'/api/asr-model/';
    mod.env.remotePathTemplate='{model}/resolve/{revision}/';
    mod.env.backends.onnx.wasm.wasmPaths=location.origin+'/api/ort/';
    return await mod.pipeline('automatic-speech-recognition','Xenova/whisper-tiny',{dtype:'q8',device:'wasm'});
  })().catch(e=>{localWhisperPromise=null;throw e});
  return localWhisperPromise
}
async function localWhisperTranscribe(blob){
  const engine=await localWhisperEngine(),url=URL.createObjectURL(blob);
  try{
    const r=await engine(url,{task:'transcribe'}),text=String(r?.text||'').trim();
    if(!text)throw Error('local multilingual transcription returned no text');
    rememberChatVoiceLanguage('',text);
    return{text,language:codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'')||'auto',engine:'local-whisper-auto'}
  }finally{try{URL.revokeObjectURL(url)}catch(_){}}
}
async function seekveraAutoTranscribe(blob){
  const audio=await blobDataURL(blob),ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),3500);
  try{
    const res=await fetch(apiBase()+'/api/transcribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({audio,language:'auto'}),signal:ctl.signal,cache:'no-store'});
    const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.reason||d.error||'server transcription failed');
    rememberChatVoiceLanguage(d.language,d.text);
    return{text:String(d.text).trim(),language:String(d.language||'auto'),engine:'seekvera-whisper-auto'}
  }finally{clearTimeout(to)}
}
async function automaticMultilingualTranscribe(blob){
  try{return await seekveraAutoTranscribe(blob)}catch(serverError){return await localWhisperTranscribe(blob)}
}
'''
if 'async function automaticMultilingualTranscribe(blob)' not in s:
    if anchor not in s: raise SystemExit('localeForText anchor missing')
    s=s.replace(anchor,seed+anchor,1)

old_block="""      try{\n        if(i)i.placeholder='Transcribing your voice…';\n        const blob=new Blob(chunks,{type}),audio=await blobDataURL(blob);\n        const signal=(typeof AbortSignal!=='undefined'&&AbortSignal.timeout)?AbortSignal.timeout(5000):undefined;const res=await fetch(apiBase()+'/api/transcribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({audio,language:'auto'}),...(signal?{signal}:{})});\n        const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.error||'transcription failed');\n        if(i){i.value=String(d.text).trim();i.placeholder='Message SEEKVERA AI…';if(i.value){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>i.form?.requestSubmit?.(),45)}}\n      }catch(e){voiceConversation=false;if(fallbackNative&&SpeechRecognition){if(i)i.placeholder='Switching to phone voice recognition…';setTimeout(()=>start(targetId,button,true),80)}else if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"""
new_block="""      try{\n        if(i)i.placeholder='Understanding your language…';\n        const blob=new Blob(chunks,{type}),d=await automaticMultilingualTranscribe(blob);\n        rememberChatVoiceLanguage(d.language,d.text);\n        if(i){i.value=String(d.text).trim();i.placeholder='Message SEEKVERA AI…';if(i.value){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>i.form?.requestSubmit?.(),35)}}\n      }catch(e){voiceConversation=false;seedVoiceLanguageFromConversation();if(fallbackNative&&SpeechRecognition){if(i)i.placeholder='Trying phone voice recognition…';setTimeout(()=>start(targetId,button,true),60)}else if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"""
if old_block in s:s=s.replace(old_block,new_block,1)
elif 'automaticMultilingualTranscribe(blob)' not in s: raise SystemExit('voice transcription block missing')

# Seed prior conversation before deciding native recognition locale.
s=s.replace("  let explicitVoice=false,rememberedVoice=false;try{explicitVoice=localStorage.getItem('seekvera_language_explicit')==='1';rememberedVoice=!!localStorage.getItem('seekvera_chat_voice_lang')}catch{}",
            "  seedVoiceLanguageFromConversation();let explicitVoice=false,rememberedVoice=false;try{explicitVoice=localStorage.getItem('seekvera_language_explicit')==='1';rememberedVoice=!!localStorage.getItem('seekvera_chat_voice_lang')}catch{}",1)

# Expose only diagnostic-safe methods used by acceptance testing.
if 'localWhisperTranscribe' not in s.split('window.SEEKVERA_VOICE_AI=',1)[-1]:
    s=s.replace('supportedLanguages:Object.keys(LANGS)', 'localWhisperTranscribe,automaticMultilingualTranscribe,inputLocale:voiceInputLocale,seedLanguage:seedVoiceLanguageFromConversation,supportedLanguages:Object.keys(LANGS)',1)
p.write_text(s,encoding='utf-8')

# Text AI: one Cloudflare model attempt only, then multilingual zero-cost fallback.
p=Path('worker-r31.js');w=p.read_text(encoding='utf-8').replace(OLD,VER)
old="async function staggeredAI(env,messages){const first=runModel(env,FAST,messages,220);const second=(async()=>{await sleep(220);return runModel(env,LIGHT,messages,220)})();const timeout=(async()=>{await sleep(2200);throw Error('ai latency budget')})();try{return await Promise.race([Promise.any([first,second]),timeout])}catch{try{return await Promise.race([runModel(env,STRONG,messages,220),(async()=>{await sleep(850);throw Error('fallback latency budget')})()])}catch{return null}}}"
new="async function staggeredAI(env,messages){try{return await Promise.race([runModel(env,FAST,messages,220),(async()=>{await sleep(1400);throw Error('ai latency budget')})()])}catch{return null}}"
if old in w:w=w.replace(old,new,1)
elif new not in w:raise SystemExit('worker staggeredAI anchor missing')
w=w.replace('AbortSignal.timeout(6000)','AbortSignal.timeout(3500)')
w=w.replace("h.set('x-seekvera-release','r65-worldwide-chat-language')","h.set('x-seekvera-release','r69-true-multilingual-voice')")
p.write_text(w,encoding='utf-8')

# Align release/cache markers across runtime and pages.
for name in ('r24-ai-controller.js','r31-ui-polish.js','superapp.js','r60-runtime-guard.js','navigation.js','r66-final-controller.js','sw.js'):
    p=Path(name)
    if p.exists():p.write_text(p.read_text(encoding='utf-8').replace(OLD,VER),encoding='utf-8')
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    p.write_text(p.read_text(encoding='utf-8').replace(OLD,VER),encoding='utf-8')

print('R69 true multilingual voice patch applied')
