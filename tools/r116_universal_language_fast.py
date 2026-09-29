from pathlib import Path
import re

VER='20260929-r116-universal-language-fast'

# ---------------- Worker: better language identity + language-aware ASR ----------------
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",s,count=1)

lang_fn=r'''function messageLanguage(message,suggested=''){
 const t=String(message||''),s=t.toLowerCase(),q=languageCode(suggested);
 const pick=(list,def)=>q&&list.includes(q)?q:def;
 // Script-first detection. Preserve a trustworthy model/ASR hint inside scripts shared by multiple languages.
 if(/[\u0600-\u06ff]/u.test(t))return pick(['ar','fa','ur','ps','ku'],'ar');
 if(/[\u0900-\u097f]/u.test(t))return pick(['hi','mr','ne'],'hi');
 if(/[\u0980-\u09ff]/u.test(t))return pick(['bn'],'bn');
 if(/[\u0a00-\u0a7f]/u.test(t))return pick(['pa'],'pa');
 if(/[\u0a80-\u0aff]/u.test(t))return pick(['gu'],'gu');
 if(/[\u0b80-\u0bff]/u.test(t))return pick(['ta'],'ta');
 if(/[\u0c00-\u0c7f]/u.test(t))return pick(['te'],'te');
 if(/[\u0d00-\u0d7f]/u.test(t))return pick(['ml'],'ml');
 if(/[\u0d80-\u0dff]/u.test(t))return pick(['si'],'si');
 if(/[\u0e00-\u0e7f]/u.test(t))return'th';
 if(/[\u0e80-\u0eff]/u.test(t))return'lo';
 if(/[\u1000-\u109f]/u.test(t))return'my';
 if(/[\u1200-\u137f]/u.test(t))return pick(['am','ti'],'am');
 if(/[\u1780-\u17ff]/u.test(t))return'km';
 if(/[\u10a0-\u10ff]/u.test(t))return'ka';
 if(/[\u0530-\u058f]/u.test(t))return'hy';
 if(/[\u0370-\u03ff]/u.test(t))return'el';
 if(/[\u0590-\u05ff]/u.test(t))return'he';
 if(/[\u3040-\u30ff]/u.test(t))return'ja';
 if(/[\uac00-\ud7af]/u.test(t))return'ko';
 if(/[\u4e00-\u9fff]/u.test(t))return pick(['zh','ja'],'zh');
 if(/[\u0400-\u052f]/u.test(t))return pick(['ru','uk','bg','sr','mk','be'],'ru');
 // Strong Latin-script clues. If there is no clue, use the model/ASR hint rather than guessing English.
 if(/[ğışİ]/u.test(t)||/\b(merhaba|nasılsın|nasilsin|istiyorum|arıyorum|ariyorum|otel|ülke|ulke|değiş|degis)\b/iu.test(s))return'tr';
 if(/[ăâđêôơư]/iu.test(t))return'vi';
 if(/[ąćęłńśźż]/iu.test(t))return'pl';
 if(/[őű]/iu.test(t))return'hu';
 if(/[ăîșşțţ]/iu.test(t))return'ro';
 if(/[ãõ]/iu.test(t)||/\b(olá|ola|preciso|procuro|hotel|obrigado|obrigada)\b/iu.test(s))return'pt';
 if(/[ñ¿¡]/iu.test(t)||/\b(hola|quiero|busco|necesito|gracias|país|pais|idioma)\b/iu.test(s))return'es';
 if(/[äöüß]/iu.test(t)||/\b(hallo|ich|suche|möchte|mochte|sprache|land|danke)\b/iu.test(s))return'de';
 if(/\b(bonjour|salut|merci|cherche|voudrais|besoin|langue|pays|hôtel|hotel)\b/iu.test(s))return'fr';
 if(/\b(ciao|buongiorno|grazie|cerco|voglio|bisogno|lingua|paese|albergo)\b/iu.test(s))return'it';
 if(/\b(hallo|dank|zoek|nodig|taal|land|hotel)\b/iu.test(s)&&q==='nl')return'nl';
 if(/\b(habari|asante|nataka|nahitaji|tafuta|hoteli)\b/iu.test(s))return'sw';
 if(/\b(selamat|terima kasih|saya|ingin|cari|butuh|hotel)\b/iu.test(s))return pick(['id','ms'],'id');
 return q||'en';
}'''
pat=r"function messageLanguage\(message,suggested=''\)\{.*?\n\}\nfunction aliasHit"
m=re.search(pat,s,re.S)
if not m: raise SystemExit('R116 messageLanguage anchor missing')
s=s[:m.start()]+lang_fn+'\nfunction aliasHit'+s[m.end():]

transcribe=r'''async function transcribeAudio(request,env){
 if(!env.AI)return json(request,{ok:false,error:'Speech AI unavailable'},503);
 if(Number(request.headers.get('content-length')||0)>9*1024*1024)return json(request,{ok:false,error:'Audio request too large'},413);
 let b={};try{b=await request.json()}catch{return json(request,{ok:false,error:'Invalid audio request'},400)}
 const raw=String(b.audio||''),m=raw.match(/^data:(audio\/(?:webm|mp4|mpeg|wav|ogg|x-m4a|aac|3gpp))(?:;codecs=[^;,]+)?;base64,([A-Za-z0-9+/=]+)$/i);
 if(!m)return json(request,{ok:false,error:'Valid recorded audio is required'},400);
 const approx=Math.floor(m[2].length*3/4);if(approx<80||approx>6*1024*1024)return json(request,{ok:false,error:'Audio size is invalid'},400);
 const nativeText=clean(b.nativeText,4000),nativeConfidence=Math.max(0,Math.min(1,Number(b.nativeConfidence)||0));
 const uiHint=languageCode(b.uiLanguage||''),sentHint=languageCode(b.languageHint||''),softHint=sentHint||uiHint;
 const family=t=>{t=String(t||'');if(/[\u0600-\u06ff]/u.test(t))return'arabic';if(/[\u0900-\u097f]/u.test(t))return'devanagari';if(/[\u0980-\u09ff]/u.test(t))return'bengali';if(/[\u0a00-\u0a7f]/u.test(t))return'gurmukhi';if(/[\u0a80-\u0aff]/u.test(t))return'gujarati';if(/[\u0b80-\u0bff]/u.test(t))return'tamil';if(/[\u0c00-\u0c7f]/u.test(t))return'telugu';if(/[\u0d00-\u0d7f]/u.test(t))return'malayalam';if(/[\u0d80-\u0dff]/u.test(t))return'sinhala';if(/[\u0e00-\u0e7f]/u.test(t))return'thai';if(/[\u0e80-\u0eff]/u.test(t))return'lao';if(/[\u1000-\u109f]/u.test(t))return'myanmar';if(/[\u1200-\u137f]/u.test(t))return'ethiopic';if(/[\u1780-\u17ff]/u.test(t))return'khmer';if(/[\u10a0-\u10ff]/u.test(t))return'georgian';if(/[\u0530-\u058f]/u.test(t))return'armenian';if(/[\u0370-\u03ff]/u.test(t))return'greek';if(/[\u0590-\u05ff]/u.test(t))return'hebrew';if(/[\u3040-\u30ff]/u.test(t))return'japanese';if(/[\uac00-\ud7af]/u.test(t))return'korean';if(/[\u4e00-\u9fff]/u.test(t))return'han';if(/[\u0400-\u052f]/u.test(t))return'cyrillic';if(/[A-Za-zÀ-ÖØ-öø-ÿ]/u.test(t))return'latin';return''};
 const nativeFamily=family(nativeText),nativeLang=nativeText?messageLanguage(nativeText,softHint):'';
 const strongHint=nativeFamily&&nativeFamily!=='latin'?nativeLang:(nativeText&&nativeConfidence>=.60?softHint:'');
 const common={task:'transcribe',vad_filter:true,condition_on_previous_text:false,beam_size:2,no_speech_threshold:.68,compression_ratio_threshold:2.4,log_prob_threshold:-1,hallucination_silence_threshold:1.0};
 const timed=(model,input,ms)=>Promise.race([env.AI.run(model,input),new Promise((_,reject)=>setTimeout(()=>reject(Error('asr timeout')),ms))]);
 const errors=[];
 let picked=null,pickedModel='',pickedFormat='';
 const primary={...common,audio:m[2],...(strongHint?{language:strongHint}:{} )};
 try{const r=await timed(ASR_PRIMARY,primary,4800),text=clean(r?.text||r?.transcription_info?.text||r?.result?.text||r?.result||'',5000);if(text){picked=r;pickedModel=ASR_PRIMARY;pickedFormat=strongHint?'base64-hinted':'base64-auto'}}catch(e){errors.push(ASR_PRIMARY+':'+clean(e?.message||e,140))}
 // If automatic ASR clearly conflicts with a reliable non-Latin phone transcript, the phone transcript is safer than a translation/mis-detection.
 let text=picked?clean(picked?.text||picked?.transcription_info?.text||picked?.result?.text||picked?.result||'',5000):'';
 if(text&&nativeText&&nativeFamily&&nativeFamily!=='latin'&&family(text)&&family(text)!==nativeFamily&&nativeConfidence>=.20){
   text=nativeText;pickedModel='native-script-rescue';pickedFormat='native-shadow';picked={language:nativeLang};
 }
 // If the first pass failed, use legacy Whisper bytes as a bounded fallback.
 if(!text){try{const bin=atob(m[2]),audio=Array.from(bin,c=>c.charCodeAt(0)),input={...common,audio,...(strongHint?{language:strongHint}:{})};const r=await timed(ASR_FALLBACK,input,3200),t=clean(r?.text||r?.result?.text||r?.result||'',5000);if(t){text=t;picked=r;pickedModel=ASR_FALLBACK;pickedFormat='bytes-fallback'}}catch(e){errors.push(ASR_FALLBACK+':'+clean(e?.message||e,140))}}
 if(!text&&nativeText){text=nativeText;picked={language:nativeLang};pickedModel='native-last-resort';pickedFormat='native-shadow'}
 if(text){const detected=clean(picked?.language||picked?.detected_language||picked?.result?.language||'',24),language=languageCode(detected)||messageLanguage(text,strongHint||softHint);return json(request,{ok:true,text,language,detectedLanguage:language,model:pickedModel,audioFormat:pickedFormat,autoLanguage:!strongHint,languageHintUsed:strongHint||null,nativeRescue:pickedModel.startsWith('native-')},200)}
 return json(request,{ok:false,error:'Voice transcription is temporarily unavailable',retryable:true,detail:errors.join(' | ')},503)
}'''
pat=r"async function transcribeAudio\(request,env\)\{.*?\n\}\n\nasync function degradedFallback"
m=re.search(pat,s,re.S)
if not m: raise SystemExit('R116 transcribeAudio anchor missing')
s=s[:m.start()]+transcribe+'\n\nasync function degradedFallback'+s[m.end():]

# Keep the text AI strict about preserving the latest user's language rather than country/UI language.
if 'Always identify the language of the latest user message' in s and 'Do not translate the user unless they explicitly ask for translation.' not in s:
    s=s.replace('Always identify the language of the latest user message and reply in that same language and script. ',
                'Always identify the language of the latest user message and reply in that same language and script. Do not translate the user unless they explicitly ask for translation. ',1)

p.write_text(s,encoding='utf-8')

# ---------------- Client voice: fast send + cross-script rescue + correct hinting ----------------
p=Path('voice-ai.js')
v=p.read_text(encoding='utf-8')
v=re.sub(r"window\.__seekveraVoiceMode='[^']+'",f"window.__seekveraVoiceMode='{VER}'",v,count=1)
v=v.replace('const VOICE_SILENCE_MS=3200,VOICE_MAX_MS=60000,VOICE_RMS_THRESHOLD=.012;',
            'const VOICE_SILENCE_MS=2300,VOICE_MAX_MS=60000,VOICE_RMS_THRESHOLD=.012;',1)

old="function voiceInputLocale(){try{const saved=String(localStorage.getItem('seekvera_chat_voice_lang')||'');const c=codeOf(saved);if(c&&LANGS[c])return LANGS[c]}catch{}if(lastLocale&&/^[a-z]{2,3}(?:-|$)/i.test(lastLocale))return lastLocale;const nav=String((navigator.languages&&navigator.languages[0])||navigator.language||'');return nav||'en-US'}"
new="function voiceInputLocale(){try{const saved=String(localStorage.getItem('seekvera_chat_voice_lang')||'');const c=codeOf(saved);if(c&&LANGS[c])return LANGS[c]}catch{}const selected=codeOf(selectedLang());if(selected&&LANGS[selected])return LANGS[selected];if(lastLocale&&/^[a-z]{2,3}(?:-|$)/i.test(lastLocale))return lastLocale;const nav=String((navigator.languages&&navigator.languages[0])||navigator.language||'');return nav||'en-US'}"
if old not in v: raise SystemExit('R116 voiceInputLocale anchor missing')
v=v.replace(old,new,1)
v=v.replace('const r=new SpeechRecognition();nativeShadow=r;r.lang=locale();', 'const r=new SpeechRecognition();nativeShadow=r;r.lang=voiceInputLocale();',1)

choose=r'''function chooseHybridTranscript(nativeText,nativeConfidence,whisper){
  const nt=String(nativeText||'').replace(/\s+/g,' ').trim(),wt=String(whisper?.text||'').replace(/\s+/g,' ').trim();
  const current=codeOf(selectedLang()||document.documentElement.lang||''),expected=expectedScriptFor(current),ws=transcriptScript(wt),ns=transcriptScript(nt),conf=Number(nativeConfidence||0);
  if(!nt)return whisper;
  if(!wt||transcriptPoor(wt))return{text:nt,language:languageFromTranscript(nt,current),engine:'native-quality-rescue'};
  // Strong non-Latin script evidence from the phone beats a contradictory ASR transcript. This fixes Arabic and other script-family mistranslations.
  if(!transcriptPoor(nt)&&ns&&ns!=='latin'&&ws&&ws!==ns)return{text:nt,language:languageFromTranscript(nt,current),engine:'native-script-rescue'};
  // For Latin-script languages, do not lock the user to the app language. Trust server auto-ASR unless the phone result is clearly stronger.
  const nscore=transcriptScore(nt,current)+(conf>=.60?28:0),wscore=transcriptScore(wt,whisper?.language||current);
  if(!transcriptPoor(nt)&&conf>=.72&&nscore>wscore+18)return{text:nt,language:languageFromTranscript(nt,current),engine:'native-confidence-rescue'};
  if(expected&&ns===expected&&!transcriptPoor(nt)&&transcriptPoor(wt))return{text:nt,language:current||languageFromTranscript(nt),engine:'native-current-locale'};
  return whisper
}'''
pat=r"function chooseHybridTranscript\(nativeText,nativeConfidence,whisper\)\{.*?\n\}"
m=re.search(pat,v,re.S)
if not m: raise SystemExit('R116 chooseHybridTranscript anchor missing')
v=v[:m.start()]+choose+v[m.end():]

seek=r'''async function seekveraAutoTranscribe(blob,nativeText='',nativeConfidence=0){
  const audio=await blobDataURL(blob),ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),6200);
  try{
    const native=String(nativeText||'').replace(/\s+/g,' ').trim();
    const inferred=languageFromTranscript(native,selectedLang()),hint=codeOf(inferred)||codeOf(selectedLang())||codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'');
    const payload={audio,language:'auto',languageHint:hint||'',uiLanguage:codeOf(selectedLang())||'',browserLanguage:String(navigator.language||''),nativeText:native,nativeConfidence:Number(nativeConfidence||0)};
    const res=await fetch(apiBase()+'/api/transcribe?auto=1&r116=1',{method:'POST',headers:{'content-type':'application/json','cache-control':'no-store'},body:JSON.stringify(payload),signal:ctl.signal,cache:'no-store'});
    const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.reason||d.error||'server transcription failed');
    rememberChatVoiceLanguage(d.language||d.detectedLanguage,d.text);
    return{text:String(d.text).trim(),language:String(d.language||d.detectedLanguage||'auto'),engine:String(d.model||'seekvera-whisper-r116'),nativeRescue:Boolean(d.nativeRescue)}
  }finally{clearTimeout(to)}
}'''
pat=r"async function seekveraAutoTranscribe\(blob\)\{.*?\n\}"
m=re.search(pat,v,re.S)
if not m: raise SystemExit('R116 seekveraAutoTranscribe anchor missing')
v=v[:m.start()]+seek+v[m.end():]

# Ensure automatic transcription passes the phone shadow into the server.
v=v.replace('try{return await seekveraAutoTranscribe(blob)}catch(e){serverError=e}',
            'try{return await seekveraAutoTranscribe(blob,nativeText,nativeConfidence)}catch(e){serverError=e}',1)
if 'seekveraAutoTranscribe(blob,nativeText,nativeConfidence)' not in v:
    raise SystemExit('R116 automaticMultilingualTranscribe call patch missing')

p.write_text(v,encoding='utf-8')

# ---------------- Cache bust ----------------
p=Path('index.html');h=p.read_text(encoding='utf-8')
h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
h=re.sub(r'voice-ai\.js\?v=[^"\s]+',f'voice-ai.js?v={VER}',h,count=1)
h=re.sub(r'sw\.js\?v=[^"\s]+',f'sw.js?v={VER}',h,count=1)
p.write_text(h,encoding='utf-8')

p=Path('sw.js');sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1)
p.write_text(sw,encoding='utf-8')

print('R116 universal multilingual voice patch applied')
