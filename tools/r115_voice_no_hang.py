from pathlib import Path
import re

VER='20260929-r115-fast-voice'
OLD='20260929-r114-fast-strong-ai'
p=Path('voice-ai.js'); s=p.read_text(encoding='utf-8')
if VER in s:
    print('R115 already applied')
    raise SystemExit(0)

s=s.replace(f"window.__seekveraVoiceMode='{OLD}'",f"window.__seekveraVoiceMode='{VER}'")
s=s.replace("const audio=await blobDataURL(blob),ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),14000);","const audio=await blobDataURL(blob),ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),7000);")

old=re.search(r"async function automaticMultilingualTranscribe\(blob\)\{.*?\n\}",s,re.S)
if not old:
    raise SystemExit('automaticMultilingualTranscribe block missing')
new=r'''async function automaticMultilingualTranscribe(blob,nativeText='',nativeConfidence=0){
  let serverError=null;
  try{return await seekveraAutoTranscribe(blob)}catch(e){serverError=e}
  const nt=String(nativeText||'').replace(/\s+/g,' ').trim();
  if(nt&&!transcriptPoor(nt)){
    const language=languageFromTranscript(nt,selectedLang());
    if(language&&language!=='auto')rememberChatVoiceLanguage(language,nt);
    return{text:nt,language:language||'auto',engine:'native-shadow-fast-fallback',confidence:Number(nativeConfidence||0)}
  }
  try{
    const timeout=new Promise((_,reject)=>setTimeout(()=>reject(Error('local multilingual ASR timeout')),9000));
    return await Promise.race([localWhisperTranscribe(blob),timeout])
  }catch(localError){throw serverError||localError}
}'''
s=s[:old.start()]+new+s[old.end():]

s=s.replace("  localWhisperEngine().catch(()=>{});\n  const i=document.getElementById(targetId||'aiChatInput');","  const i=document.getElementById(targetId||'aiChatInput');",1)
s=s.replace("const blob=new Blob(chunks,{type}),whisper=await automaticMultilingualTranscribe(blob),d=chooseHybridTranscript(shadowText,shadowConfidence,whisper);","const blob=new Blob(chunks,{type}),whisper=await automaticMultilingualTranscribe(blob,shadowText,shadowConfidence),d=chooseHybridTranscript(shadowText,shadowConfidence,whisper);",1)

anchor="  lastAnswer=typeof text==='string'?text:'';lastLocale=localeForText(lastAnswer,l);const chunks=splitSpeech(lastAnswer);\n"
if anchor not in s: raise SystemExit('speak anchor missing')
s=s.replace(anchor,anchor+"  window.dispatchEvent(new CustomEvent('seekvera:tts-request',{detail:{text:lastAnswer,language:lastLocale,force:Boolean(force)}}));\n",1)
p.write_text(s,encoding='utf-8')

p=Path('index.html'); h=p.read_text(encoding='utf-8'); h=h.replace(f'voice-ai.js?v={OLD}',f'voice-ai.js?v={VER}'); h=h.replace(f'sw.js?v={OLD}',f'sw.js?v={VER}'); p.write_text(h,encoding='utf-8')
p=Path('sw.js'); w=p.read_text(encoding='utf-8'); w=w.replace(OLD,VER); p.write_text(w,encoding='utf-8')
print('R115 patched')
