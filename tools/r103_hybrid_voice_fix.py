from pathlib import Path
import re

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
VER='20260927-r103-hybrid-native-whisper'

# Runtime state for a parallel current-locale native recognizer while MediaRecorder keeps the multilingual safety recording.
old="let recognition=null,lastAnswer='',lastLocale='',muted=localStorage.getItem('seekvera_voice_muted')==='1',activeButton=null,voiceConversation=false,voiceReplyDeadline=0,speakToken=0,recording=false,mediaRecorder=null,mediaStream=null,recordChunks=[],recordTimer=null,speechSilenceTimer=null,speechHardTimer=null,audioCtx=null,audioAnalyser=null,audioSource=null,audioRaf=0,heardVoice=false,lastVoiceAt=0,recordStartedAt=0;"
new="let recognition=null,nativeShadow=null,nativeShadowText='',nativeShadowConfidence=0,lastAnswer='',lastLocale='',muted=localStorage.getItem('seekvera_voice_muted')==='1',activeButton=null,voiceConversation=false,voiceReplyDeadline=0,speakToken=0,recording=false,mediaRecorder=null,mediaStream=null,recordChunks=[],recordTimer=null,speechSilenceTimer=null,speechHardTimer=null,audioCtx=null,audioAnalyser=null,audioSource=null,audioRaf=0,heardVoice=false,lastVoiceAt=0,recordStartedAt=0;"
if new not in s:
    if old not in s: raise SystemExit('voice state anchor missing')
    s=s.replace(old,new,1)

# Detect common Whisper filler/hallucination text so it cannot silently win over a real native transcript.
old="  if(maxRun>=4)return true;\n  return false\n}"
new="  if(maxRun>=4)return true;\n  if(/thank(?:s| you) for watching|see you in the next video|subscribe to (?:my|the) channel|like and subscribe/i.test(t))return true;\n  return false\n}"
if new not in s:
    if old not in s: raise SystemExit('transcriptPoor anchor missing')
    s=s.replace(old,new,1)

# Resolve language from the actual transcript instead of leaking stale localStorage metadata across country switches.
anchor="function hintedVoiceCodes(){\n"
helper="""function languageFromTranscript(text,preferred=''){
  const sc=transcriptScript(text),p=codeOf(preferred||selectedLang()||document.documentElement.lang||'');
  const groups={arabic:['ar','fa','ur','ps'],devanagari:['hi','mr','ne'],bengali:['bn'],han:['zh'],japanese:['ja'],korean:['ko'],cyrillic:['ru','uk','bg','sr','be','mk'],hebrew:['he'],greek:['el'],thai:['th']};
  if(sc==='latin')return p&&LANGS[p]&&!Object.values(groups).flat().includes(p)?p:'auto';
  const g=groups[sc]||[];if(p&&g.includes(p))return p;return g[0]||'auto'
}
function expectedScriptFor(code){
  code=codeOf(code);for(const [sc,g] of Object.entries({arabic:['ar','fa','ur','ps'],devanagari:['hi','mr','ne'],bengali:['bn'],han:['zh'],japanese:['ja'],korean:['ko'],cyrillic:['ru','uk','bg','sr','be','mk'],hebrew:['he'],greek:['el'],thai:['th']}))if(g.includes(code))return sc;return code&&LANGS[code]?'latin':''
}
function chooseHybridTranscript(nativeText,nativeConfidence,whisper){
  const nt=String(nativeText||'').replace(/\\s+/g,' ').trim(),wt=String(whisper?.text||'').replace(/\\s+/g,' ').trim();
  const current=codeOf(selectedLang()||document.documentElement.lang||''),expected=expectedScriptFor(current),ws=transcriptScript(wt),ns=transcriptScript(nt);
  if(!nt)return whisper;
  if(!wt||transcriptPoor(wt))return{text:nt,language:current||languageFromTranscript(nt),engine:'native-current-locale'};
  // A clean Whisper transcript in a clearly different script is evidence the person deliberately spoke another language.
  if(expected&&ws&&ws!==expected&&ws!=='latin'&&!transcriptPoor(wt))return whisper;
  const nscore=transcriptScore(nt,current)+(Number(nativeConfidence||0)>=.35?35:0),wscore=transcriptScore(wt,current);
  if(!transcriptPoor(nt)&&(ns===expected||Number(nativeConfidence||0)>=.35||nscore>=wscore))return{text:nt,language:current||languageFromTranscript(nt),engine:'native-current-locale'};
  return whisper
}
function startNativeShadow(){
  nativeShadowText='';nativeShadowConfidence=0;if(!SpeechRecognition)return;
  try{
    const r=new SpeechRecognition();nativeShadow=r;r.lang=locale();r.interimResults=true;r.continuous=!/Android|iPhone|iPad|iPod/i.test(navigator.userAgent);r.maxAlternatives=1;
    r.onresult=e=>{let final='',interim='',best=0;for(let x=0;x<e.results.length;x++){const a=e.results[x][0],t=String(a?.transcript||'').replace(/\\s+/g,' ').trim();if(!t)continue;best=Math.max(best,Number(a?.confidence||0));if(e.results[x].isFinal)final+=(final?' ':'')+t;else interim+=(interim?' ':'')+t}nativeShadowText=(final||interim||nativeShadowText).trim();nativeShadowConfidence=Math.max(nativeShadowConfidence,best)};
    r.onerror=()=>{};r.onend=()=>{if(nativeShadow===r)nativeShadow=null};r.start()
  }catch(_){nativeShadow=null}
}
function stopNativeShadow(){const r=nativeShadow;if(r)try{r.stop()}catch(_){}nativeShadow=null}
"""
if 'function chooseHybridTranscript(' not in s:
    if anchor not in s: raise SystemExit('hintedVoiceCodes insertion anchor missing')
    s=s.replace(anchor,helper+anchor,1)

# Replace stale-language return logic in local Whisper.
old="    rememberChatVoiceLanguage(chosenHint,text);\n    return{text,language:codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'')||chosenHint||'auto',engine:chosenHint?'local-whisper-recovered':'local-whisper-auto'}"
new="    const outLang=chosenHint||languageFromTranscript(text);\n    if(outLang&&outLang!=='auto')rememberChatVoiceLanguage(outLang,text);else try{localStorage.removeItem('seekvera_chat_voice_lang')}catch(_){}\n    return{text,language:outLang||'auto',engine:chosenHint?'local-whisper-recovered':'local-whisper-auto'}"
if new not in s:
    if old not in s: raise SystemExit('Whisper language return anchor missing')
    s=s.replace(old,new,1)

# Ensure any stream cleanup stops the shadow recognizer too.
old="function releaseStream(){if(recordTimer){clearTimeout(recordTimer);recordTimer=null}clearSpeechTimers();stopAudioMonitor();try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false)}"
new="function releaseStream(){if(recordTimer){clearTimeout(recordTimer);recordTimer=null}clearSpeechTimers();stopAudioMonitor();stopNativeShadow();try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false)}"
if new not in s:
    if old not in s: raise SystemExit('releaseStream anchor missing')
    s=s.replace(old,new,1)

# Start native current-locale recognition in parallel with MediaRecorder.
old="    mediaRecorder=new MediaRecorder(mediaStream,opts);recording=true;\n    mediaRecorder.ondataavailable=e=>{if(e.data?.size)recordChunks.push(e.data)};"
new="    mediaRecorder=new MediaRecorder(mediaStream,opts);recording=true;startNativeShadow();\n    mediaRecorder.ondataavailable=e=>{if(e.data?.size)recordChunks.push(e.data)};"
if new not in s:
    if old not in s: raise SystemExit('MediaRecorder shadow start anchor missing')
    s=s.replace(old,new,1)

# At stop, retain shadow output, run multilingual Whisper, then choose the stronger result.
old="""      const chunks=[...recordChunks],type=mediaRecorder?.mimeType||chunks[0]?.type||'audio/webm';
      if(recordTimer){clearTimeout(recordTimer);recordTimer=null}stopAudioMonitor();
      try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false);
      if(!chunks.length){voiceConversation=false;if(i)i.placeholder='No speech recorded — tap the microphone and try again.';return}
      try{
        if(i)i.placeholder='Transcribing your speech…';
        const blob=new Blob(chunks,{type}),d=await automaticMultilingualTranscribe(blob);
        rememberChatVoiceLanguage(d.language,d.text);
        if(i){const spoken=String(d.text).trim();i.value=spoken;i.placeholder='Message SEEKVERA AI…';if(spoken){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>{if(window.SEEKVERA_R31?.submitAI)window.SEEKVERA_R31.submitAI(spoken,{fromVoice:true});else i.form?.requestSubmit?.()},35)}}
"""
new="""      const chunks=[...recordChunks],type=mediaRecorder?.mimeType||chunks[0]?.type||'audio/webm',shadowText=nativeShadowText,shadowConfidence=nativeShadowConfidence;
      stopNativeShadow();if(recordTimer){clearTimeout(recordTimer);recordTimer=null}stopAudioMonitor();
      try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false);
      if(!chunks.length){voiceConversation=false;if(i)i.placeholder='No speech recorded — tap the microphone and try again.';return}
      try{
        if(i)i.placeholder='Understanding your speech…';
        const blob=new Blob(chunks,{type}),whisper=await automaticMultilingualTranscribe(blob),d=chooseHybridTranscript(shadowText,shadowConfidence,whisper);
        if(d?.language&&d.language!=='auto')rememberChatVoiceLanguage(d.language,d.text);
        if(i){const spoken=String(d?.text||'').trim();i.value=spoken;i.placeholder='Message SEEKVERA AI…';if(spoken){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>{if(window.SEEKVERA_R31?.submitAI)window.SEEKVERA_R31.submitAI(spoken,{fromVoice:true});else i.form?.requestSubmit?.()},35)}}
"""
if new not in s:
    if old not in s: raise SystemExit('serverVoice stop anchor missing')
    s=s.replace(old,new,1)

# Export selector for deterministic certification.
s=s.replace("localWhisperTranscribe,automaticMultilingualTranscribe,inputLocale:voiceInputLocale", "localWhisperTranscribe,automaticMultilingualTranscribe,chooseHybridTranscript,inputLocale:voiceInputLocale",1)
s=re.sub(r"window\.__seekveraVoiceMode='[^']+';", "window.__seekveraVoiceMode='hybrid-native-whisper-r103';", s, count=1)
p.write_text(s,encoding='utf-8')

for hp in Path('.').glob('*.html'):
    h=hp.read_text(encoding='utf-8')
    h=re.sub(r'voice-ai\.js\?v=[^"\\s]+','voice-ai.js?v='+VER,h)
    if hp.name=='index.html': h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
    hp.write_text(h,encoding='utf-8')
psw=Path('sw.js');sw=psw.read_text(encoding='utf-8');sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1);psw.write_text(sw,encoding='utf-8')
print('R103_APPLIED')
