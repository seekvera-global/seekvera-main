from pathlib import Path
import re

VER='20260927-r92-live-asr-repair'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",s,count=1)
old=""" const bin=atob(m[2]),audio=Array.from(bin,c=>c.charCodeAt(0));
 const base={audio,task:'transcribe',vad_filter:true,condition_on_previous_text:false,beam_size:5,no_speech_threshold:.72};
 const errors=[];
 for(const model of [ASR_PRIMARY,ASR_FALLBACK]){try{
   const r=await Promise.race([env.AI.run(model,base),new Promise((_,reject)=>setTimeout(()=>reject(Error('asr timeout')),8000))]),text=clean(r?.text||r?.result?.text||r?.result||'',5000);
   if(text){const language=messageLanguage(text,'');return json(request,{ok:true,text,language,detectedLanguage:language,model,autoLanguage:true},200)}
   errors.push(model+':empty');
 }catch(e){errors.push(model+':'+clean(e?.message||e,180))}}
 return json(request,{ok:false,error:'Voice transcription is temporarily unavailable',retryable:true,detail:errors.slice(-2).join(' | ')},503)
"""
new=""" const bin=atob(m[2]),audioBytes=Array.from(bin,c=>c.charCodeAt(0));
 const common={task:'transcribe',vad_filter:true,condition_on_previous_text:false,beam_size:5,no_speech_threshold:.72};
 // Cloudflare Whisper Large v3 Turbo accepts base64 audio; the legacy Whisper model accepts byte arrays.
 // Use the native payload for each model and keep language unset so speech language is detected automatically.
 const attempts=[
   [ASR_PRIMARY,{...common,audio:m[2]},'base64'],
   [ASR_FALLBACK,{...common,audio:audioBytes},'bytes']
 ];
 const errors=[];
 for(const [model,input,format] of attempts){try{
   const r=await Promise.race([env.AI.run(model,input),new Promise((_,reject)=>setTimeout(()=>reject(Error('asr timeout')),10000))]),text=clean(r?.text||r?.result?.text||r?.result||'',5000);
   if(text){const detected=clean(r?.language||r?.detected_language||r?.result?.language||'',24),language=languageCode(detected)||messageLanguage(text,'');return json(request,{ok:true,text,language,detectedLanguage:language,model,audioFormat:format,autoLanguage:true},200)}
   errors.push(model+'('+format+'):empty');
 }catch(e){errors.push(model+'('+format+'):'+clean(e?.message||e,180))}}
 return json(request,{ok:false,error:'Voice transcription is temporarily unavailable',retryable:true,detail:errors.join(' | ')},503)
"""
if old not in s:
    raise SystemExit('R92 transcribe block anchor missing')
s=s.replace(old,new,1)
needle="r89:true,r89Runtime:'workers-ai-whisper-byte-array-no-consent',"
if needle in s and "r92:true" not in s:
    s=s.replace(needle,"r92:true,r92Runtime:'native-asr-payload-per-model-auto-language',"+needle,1)
p.write_text(s,encoding='utf-8')
print('R92 ASR payload repair applied')
