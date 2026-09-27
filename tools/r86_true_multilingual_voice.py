from pathlib import Path
import re

VER='20260927-r86-true-multilingual-conversation-voice'

# Worker: robust AUTO-language ASR endpoint and conversation-first assistant.
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const RELEASE='20260927-r84-natural-chat-guard';",f"const RELEASE='{VER}';",1)
if "const ASR_PRIMARY='@cf/openai/whisper-large-v3-turbo'" not in s:
    anchor="const FALLBACK='@cf/qwen/qwen3-30b-a3b-fp8';\n"
    if anchor not in s: raise SystemExit('worker model anchor missing')
    s=s.replace(anchor,anchor+"const ASR_PRIMARY='@cf/openai/whisper-large-v3-turbo',ASR_FALLBACK='@cf/openai/whisper';\n",1)
s=s.replace("return h.slice(-10).map", "return h.slice(-18).map",1)
s=s.replace(".join('\\n').slice(-6500)", ".join('\\n').slice(-10000)",1)

if 'async function transcribeAudio(request,env)' not in s:
    anchor='async function degradedFallback(request,env,ctx,body,message){\n'
    helper=r'''async function transcribeAudio(request,env){
 if(!env.AI)return json(request,{ok:false,error:'Speech AI unavailable'},503);
 if(Number(request.headers.get('content-length')||0)>9*1024*1024)return json(request,{ok:false,error:'Audio request too large'},413);
 let b={};try{b=await request.json()}catch{return json(request,{ok:false,error:'Invalid audio request'},400)}
 const raw=String(b.audio||''),m=raw.match(/^data:(audio\/(?:webm|mp4|mpeg|wav|ogg|x-m4a|aac|3gpp))(?:;codecs=[^;,]+)?;base64,([A-Za-z0-9+/=]+)$/i);
 if(!m)return json(request,{ok:false,error:'Valid recorded audio is required'},400);
 const approx=Math.floor(m[2].length*3/4);if(approx<80||approx>6*1024*1024)return json(request,{ok:false,error:'Audio size is invalid'},400);
 const base={audio:m[2],task:'transcribe',vad_filter:true,condition_on_previous_text:false,beam_size:5,no_speech_threshold:.72};
 const errors=[];
 for(const model of [ASR_PRIMARY,ASR_PRIMARY,ASR_FALLBACK]){try{
   const r=await env.AI.run(model,base),text=clean(r?.text||r?.result?.text||r?.result||'',5000);
   if(text){const language=messageLanguage(text,'');return json(request,{ok:true,text,language,detectedLanguage:language,model,autoLanguage:true},200)}
   errors.push(model+':empty');
 }catch(e){errors.push(model+':'+clean(e?.message||e,180))}}
 return json(request,{ok:false,error:'Voice transcription is temporarily unavailable',retryable:true,detail:errors.slice(-2).join(' | ')},503)
}

'''
    if anchor not in s: raise SystemExit('degradedFallback anchor missing')
    s=s.replace(anchor,helper+anchor,1)

old="- reply: talk naturally like a capable conversational assistant, not a fixed template. Use the recent conversation to understand follow-ups. Answer what you can first. If the request is too vague to choose useful results, ask ONE short, relevant clarification (for example location, type, budget or date). Never ask again for information already present in the conversation.\\\n"
new="- reply: behave like a real conversational AI assistant. Hold a normal back-and-forth conversation, answer questions directly, understand corrections and follow-ups, and use the recent conversation as memory. Do NOT rush the user into a marketplace section. If the user has not yet clearly said what they want, keep talking naturally. When the user does want something, ask only the minimum useful follow-up questions needed (such as country/city, dates, budget, type, quantity or preferences), one concise question at a time. Never ask again for information already present in the conversation. Once the goal is clear, help with it and choose the correct category.\\\n"
if old in s: s=s.replace(old,new,1)
old="- category: exactly one of ${[...CATS].join(', ')}. Choose general for greetings, small talk, casual conversation, meta questions, incomplete or vague requests, and clarification turns. Choose a section only when the latest user message clearly asks to find, search, book, buy, sell, apply for, compare, or use something in that section. Never classify casual uses of work/عمل/شغل as Jobs unless the person is actually seeking employment.\\\n"
new="- category: exactly one of ${[...CATS].join(', ')}. Conversation-first rule: use general for greetings, small talk, questions, explanations, language/voice talk, corrections, incomplete requests, and every clarification turn. Choose a marketplace category only when the user's current goal is genuinely actionable and belongs there (find/search/book/buy/sell/apply/compare/use). Never route merely because a keyword appears. Never classify casual uses of work/عمل/شغل as Jobs unless the person is actually seeking employment.\\\n"
if old in s: s=s.replace(old,new,1)
s=s.replace("temperature:.1,max_tokens:520", "temperature:.2,max_tokens:760",1)

health_old="return json(request,{...d,r81:true,r81Runtime:'natural-multilingual-conversation',r81Routing:'explicit-intent-only',r81Voice:'server-auto-asr-first',r81Fallback:'natural-conversation-and-deterministic-actions'});"
health_new="return json(request,{...d,r86:true,r86Runtime:'conversation-first-multilingual-ai',r86Routing:'goal-aware-not-keyword-first',r86Voice:'whisper-auto-language-independent-of-ui',r86Asr:ASR_PRIMARY,r81:true,r81Runtime:'natural-multilingual-conversation',r81Routing:'explicit-intent-only',r81Voice:'server-auto-asr-first',r81Fallback:'natural-conversation-and-deterministic-actions'});"
if health_old not in s and 'r86Runtime' not in s: raise SystemExit('health anchor missing')
s=s.replace(health_old,health_new,1)
ai_anchor=" if(u.pathname==='/api/ai'&&request.method==='POST'){\n"
if "u.pathname==='/api/transcribe'&&request.method==='POST'" not in s:
    if ai_anchor not in s: raise SystemExit('api ai anchor missing')
    s=s.replace(ai_anchor," if(u.pathname==='/api/transcribe'&&request.method==='POST')return transcribeAudio(request,env);\n"+ai_anchor,1)
p.write_text(s,encoding='utf-8')

# Voice client: speech understanding independent of selected interface language.
p=Path('voice-ai.js')
v=p.read_text(encoding='utf-8')
v=v.replace('const VOICE_SILENCE_MS=3200,VOICE_MAX_MS=30000,VOICE_RMS_THRESHOLD=.016;','const VOICE_SILENCE_MS=3600,VOICE_MAX_MS=45000,VOICE_RMS_THRESHOLD=.014;',1)
start=v.find('function voiceInputLocale(){')
end=v.find('function rememberChatVoiceLanguage',start)
if start<0 or end<0: raise SystemExit('voiceInputLocale block missing')
v=v[:start]+"function voiceInputLocale(){try{const saved=String(localStorage.getItem('seekvera_chat_voice_lang')||'');const c=codeOf(saved);if(c&&LANGS[c])return LANGS[c]}catch{}if(lastLocale&&/^[a-z]{2,3}(?:-|$)/i.test(lastLocale))return lastLocale;const nav=String((navigator.languages&&navigator.languages[0])||navigator.language||'');return nav||'en-US'}\n"+v[end:]
start=v.find('async function seekveraAutoTranscribe(blob){')
end=v.find('async function automaticMultilingualTranscribe(blob){',start)
if start<0 or end<0: raise SystemExit('seekveraAutoTranscribe block missing')
block=r'''async function seekveraAutoTranscribe(blob){
  const audio=await blobDataURL(blob);let lastErr=null;
  for(let attempt=0;attempt<2;attempt++){
    const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),attempt?36000:30000);
    try{
      const res=await fetch(apiBase()+'/api/transcribe?auto=1&attempt='+(attempt+1),{method:'POST',headers:{'content-type':'application/json','cache-control':'no-store'},body:JSON.stringify({audio,language:'auto'}),signal:ctl.signal,cache:'no-store'});
      const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.reason||d.error||'server transcription failed');
      rememberChatVoiceLanguage(d.language||d.detectedLanguage,d.text);
      return{text:String(d.text).trim(),language:String(d.language||d.detectedLanguage||'auto'),engine:'seekvera-whisper-auto'}
    }catch(e){lastErr=e}finally{clearTimeout(to)}
  }
  throw lastErr||Error('server transcription failed')
}
'''
v=v[:start]+block+v[end:]
old="}catch(e){voiceConversation=false;seedVoiceLanguageFromConversation();if(fallbackNative&&SpeechRecognition){if(i)i.placeholder='Trying phone voice recognition…';setTimeout(()=>start(targetId,button,true),60)}else if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}"
new="}catch(e){voiceConversation=false;seedVoiceLanguageFromConversation();if(i)i.placeholder='I could not understand that audio yet — tap the microphone and try again.'}"
if old not in v and 'Trying phone voice recognition' in v: raise SystemExit('serverVoice fallback anchor mismatch')
v=v.replace(old,new,1)
v=v.replace('serverVoice(targetId,activeButton,true);return','serverVoice(targetId,activeButton,false);return',1)
p.write_text(v,encoding='utf-8')

# Cache bust new voice client.
p=Path('index.html')
h=p.read_text(encoding='utf-8')
h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
h=re.sub(r'voice-ai\.js\?v=[^"\s]+',f'voice-ai.js?v={VER}',h,count=1)
h=re.sub(r'sw\.js\?v=[^"\s]+',f'sw.js?v={VER}',h,count=1)
p.write_text(h,encoding='utf-8')

p=Path('sw.js')
sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1)
p.write_text(sw,encoding='utf-8')
