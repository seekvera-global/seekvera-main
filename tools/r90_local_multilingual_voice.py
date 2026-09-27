from pathlib import Path
import re
VER='20260927-r90-local-multilingual-voice'

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')

# 1) Local Whisper must fetch its multilingual model directly from Hugging Face.
old="""async function localWhisperEngine(){
  if(localWhisperPromise)return localWhisperPromise;
  localWhisperPromise=(async()=>{
    const mod=await import('/patched-transformers.js?v=20260926-r73-true-multilingual-voice');
    mod.env.remoteHost=location.origin+'/api/asr-model/';
    mod.env.remotePathTemplate='{model}/resolve/{revision}/';
    mod.env.backends.onnx.wasm.wasmPaths=location.origin+'/api/ort/';
    return await mod.pipeline('automatic-speech-recognition','Xenova/whisper-tiny',{dtype:'q8',device:'wasm'});
  })().catch(e=>{localWhisperPromise=null;throw e});
  return localWhisperPromise
}"""
new="""async function localWhisperEngine(){
  if(localWhisperPromise)return localWhisperPromise;
  localWhisperPromise=(async()=>{
    const mod=await import('/patched-transformers.js?v=20260927-r90-local-multilingual-voice');
    mod.env.allowRemoteModels=true;
    mod.env.remoteHost='https://huggingface.co/';
    mod.env.remotePathTemplate='{model}/resolve/{revision}/';
    mod.env.useBrowserCache=true;
    mod.env.backends.onnx.wasm.wasmPaths='https://cdn.jsdelivr.net/npm/onnxruntime-web@1.25.0-dev.20260212-1a71a5f46e/dist/';
    return await mod.pipeline('automatic-speech-recognition','Xenova/whisper-tiny',{dtype:'q8',device:'wasm'});
  })().catch(e=>{localWhisperPromise=null;throw e});
  return localWhisperPromise
}"""
if old in s:
    s=s.replace(old,new,1)
elif "mod.env.remoteHost='https://huggingface.co/'" not in s:
    raise SystemExit('localWhisperEngine anchor missing')

# 2) Local multilingual Whisper first. Cloud ASR is only a fallback because the free Cloudflare quota can be exhausted.
start=s.find('async function automaticMultilingualTranscribe(blob){')
end=s.find('\nfunction localeForText(',start)
if start<0 or end<0: raise SystemExit('automaticMultilingualTranscribe bounds missing')
auto="""async function automaticMultilingualTranscribe(blob){
  let localError=null;
  try{
    const timeout=new Promise((_,reject)=>setTimeout(()=>reject(Error('local multilingual ASR timeout')),45000));
    return await Promise.race([localWhisperTranscribe(blob),timeout])
  }catch(e){localError=e}
  try{return await seekveraAutoTranscribe(blob)}catch(serverError){throw localError||serverError}
}"""
s=s[:start]+auto+s[end:]

# 3) Warm the local model while the person is speaking, so first-turn wait is shorter.
anchor="async function serverVoice(targetId,button,fallbackNative=false){\n  if(recording){stopRecorder();return}"
replacement="async function serverVoice(targetId,button,fallbackNative=false){\n  if(recording){stopRecorder();return}\n  localWhisperEngine().catch(()=>{});"
if anchor in s:
    s=s.replace(anchor,replacement,1)
elif "localWhisperEngine().catch(()=>{});" not in s:
    raise SystemExit('serverVoice warmup anchor missing')

# 4) Phone/browser speech synthesis first. Server TTS remains fallback.
old="const token=++speakToken,voiceMode=localStorage.getItem('seekvera_voice_mode')==='1',mobile=/Android|iPhone|iPad|iPod/i.test(navigator.userAgent),serverFirst=force||voiceConversation||voiceMode||mobile;\n  if(serverFirst){serverSpeakSequence(chunks,lastLocale,token).then(ok=>{if(!ok&&token===speakToken&&!muted)nativeSpeak(chunks,token)}).catch(()=>{if(token===speakToken&&!muted)nativeSpeak(chunks,token)});return}\n  if(nativeSpeak(chunks,token))return;serverSpeakSequence(chunks,lastLocale,token)"
new="const token=++speakToken;\n  if(nativeSpeak(chunks,token))return;\n  serverSpeakSequence(chunks,lastLocale,token)"
if old in s:
    s=s.replace(old,new,1)
elif "if(nativeSpeak(chunks,token))return;\n  serverSpeakSequence" not in s:
    raise SystemExit('speak strategy anchor missing')

# 5) Clearer status text; never pretend the language was understood before a transcript exists.
s=s.replace("i.placeholder='Understanding speech automatically…';","i.placeholder='Transcribing your speech…';")
s=s.replace("i.placeholder='I could not understand that audio yet — tap the microphone and try again.';","i.placeholder='Voice recognition failed — tap the microphone and try again.';")

p.write_text(s,encoding='utf-8')

# Release/cache markers.
p=Path('index.html');h=p.read_text(encoding='utf-8')
h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
h=re.sub(r'voice-ai\.js\?v=[^"\s]+',f'voice-ai.js?v={VER}',h,count=1)
h=re.sub(r'sw\.js\?v=[^"\s]+',f'sw.js?v={VER}',h,count=1)
p.write_text(h,encoding='utf-8')

p=Path('sw.js');sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1)
p.write_text(sw,encoding='utf-8')
print('R90 local multilingual voice patch applied')
