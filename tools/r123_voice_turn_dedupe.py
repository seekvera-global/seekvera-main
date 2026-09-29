from pathlib import Path
import re

VER='20260929-r123-single-voice-turn'
VOICE_VER='20260929-r123-arabic-auto-dedupe'

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"window\.__seekveraVoiceMode='[^']+'",f"window.__seekveraVoiceMode='{VOICE_VER}'",s,count=1)

anchor="let recognition=null,nativeShadow=null,nativeShadowText='',nativeShadowConfidence=0,lastAnswer='',lastLocale='',muted=localStorage.getItem('seekvera_voice_muted')==='1',activeButton=null,voiceConversation=false,voiceReplyDeadline=0,speakToken=0,recording=false,mediaRecorder=null,mediaStream=null,recordChunks=[],recordTimer=null,speechSilenceTimer=null,speechHardTimer=null,audioCtx=null,audioAnalyser=null,audioSource=null,audioRaf=0,heardVoice=false,lastVoiceAt=0,recordStartedAt=0;\n"
helper=r"""let lastVoiceSubmitText='',lastVoiceSubmitAt=0,lastSpokenText='',lastSpokenAt=0;
function normalizedTurnText(text){return String(text||'').normalize('NFKC').replace(/\s+/g,' ').trim().toLocaleLowerCase()}
function compactVoiceTranscript(text){
  const value=String(text||'').normalize('NFKC').replace(/\s+/g,' ').trim();
  if(!value)return'';
  const words=value.split(' ');
  if(words.length>=4&&words.length%2===0){
    const half=words.length/2,a=normalizedTurnText(words.slice(0,half).join(' ')),b=normalizedTurnText(words.slice(half).join(' '));
    if(a&&a===b)return words.slice(0,half).join(' ')
  }
  return value
}
function acceptVoiceTurn(text){
  const key=normalizedTurnText(text),now=Date.now();
  if(!key)return false;
  if(key===lastVoiceSubmitText&&now-lastVoiceSubmitAt<5000)return false;
  lastVoiceSubmitText=key;lastVoiceSubmitAt=now;return true
}
"""
if helper not in s:
    if anchor not in s: raise SystemExit('R123 voice state anchor missing')
    s=s.replace(anchor,anchor+helper,1)

old="const payload={audio,language:'auto',languageHint:hint||'',uiLanguage:codeOf(selectedLang())||'',browserLanguage:String(navigator.language||''),nativeText:native,nativeConfidence:Number(nativeConfidence||0)};"
new="const payload={audio,language:'auto',languageHint:hint||'',conversationLanguage:codeOf(localStorage.getItem('seekvera_chat_voice_lang')||''),uiLanguage:codeOf(selectedLang())||'',browserLanguage:String(navigator.language||''),nativeText:native,nativeConfidence:Number(nativeConfidence||0)};"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R123 voice payload anchor missing')

old="if(i){const spoken=String(d?.text||'').trim();i.value=spoken;i.placeholder='Message SEEKVERA AI…';if(spoken){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>{if(window.SEEKVERA_R31?.submitAI)window.SEEKVERA_R31.submitAI(spoken,{fromVoice:true});else i.form?.requestSubmit?.()},35)}}"
new="if(i){const spoken=compactVoiceTranscript(d?.text||'');i.value=spoken;i.placeholder='Message SEEKVERA AI…';if(spoken&&acceptVoiceTurn(spoken)){voiceReplyDeadline=Date.now()+90000;setTimeout(()=>{if(window.SEEKVERA_R31?.submitAI)window.SEEKVERA_R31.submitAI(spoken,{fromVoice:true});else i.form?.requestSubmit?.()},35)}else{voiceConversation=false}}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R123 server voice submit anchor missing')

old="r.onend=()=>{clearSpeechTimers();setMic(false);if(recognition===r)recognition=null;const q=i?.value?.trim();if(q){voiceReplyDeadline=Date.now()+90000;if(i)i.placeholder='Message SEEKVERA AI…';setTimeout(()=>i.form?.requestSubmit?.(),25)}else{voiceConversation=false;if(i&&hadError)i.placeholder='Voice recognition failed — tap the microphone and try again.'}};"
new="r.onend=()=>{clearSpeechTimers();setMic(false);if(recognition===r)recognition=null;const q=compactVoiceTranscript(i?.value||'');if(i)i.value=q;if(q&&acceptVoiceTurn(q)){voiceReplyDeadline=Date.now()+90000;if(i)i.placeholder='Message SEEKVERA AI…';setTimeout(()=>i.form?.requestSubmit?.(),25)}else{voiceConversation=false;if(i&&hadError)i.placeholder='Voice recognition failed — tap the microphone and try again.'}};"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R123 native voice submit anchor missing')

old="window.addEventListener('seekvera:ai-response',e=>{const d=e.detail||{},voiceMode=localStorage.getItem('seekvera_voice_mode')==='1',auto=voiceConversation||Date.now()<voiceReplyDeadline||voiceMode;if(auto)voiceReplyDeadline=0;if(d.text){rememberChatVoiceLanguage(d.language,d.text);speak(d.text,d.language,auto)}});"
new="window.addEventListener('seekvera:ai-response',e=>{const d=e.detail||{},voiceMode=localStorage.getItem('seekvera_voice_mode')==='1',auto=voiceConversation||Date.now()<voiceReplyDeadline||voiceMode,text=String(d.text||'').trim(),key=normalizedTurnText(text),now=Date.now();if(auto)voiceReplyDeadline=0;if(!text)return;if(key&&key===lastSpokenText&&now-lastSpokenAt<2200)return;lastSpokenText=key;lastSpokenAt=now;rememberChatVoiceLanguage(d.language,text);speak(text,d.language,auto)});"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R123 TTS event anchor missing')

old="serverSpeak:(text,requested)=>{const token=++speakToken;return serverSpeak(text,localeForText(text,requested),token)}};"
new="serverSpeak:(text,requested)=>{const token=++speakToken;return serverSpeak(text,localeForText(text,requested),token)},compactTranscript:compactVoiceTranscript,acceptVoiceTurn};"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R123 voice API anchor missing')
p.write_text(s,encoding='utf-8')

p=Path('r31-ui-polish.js')
r=p.read_text(encoding='utf-8')
r=re.sub(r'const VERSION = "[^"]+";',f'const VERSION = "{VER}";',r,count=1)
anchor='''    if (!q || submitting) return;
    submitting = true;'''
replacement='''    if (!q || submitting) return;
    const turnKey = q.normalize("NFKC").replace(/\\s+/g, " ").trim().toLocaleLowerCase();
    const turnNow = Date.now();
    const previousTurn = window.__seekveraLastSubmittedTurn || {};
    if (turnKey && previousTurn.key === turnKey && turnNow - Number(previousTurn.at || 0) < 5000) return;
    window.__seekveraLastSubmittedTurn = { key: turnKey, at: turnNow };
    submitting = true;'''
if anchor in r:r=r.replace(anchor,replacement,1)
elif replacement not in r:raise SystemExit('R123 R31 turn guard anchor missing')
p.write_text(r,encoding='utf-8')

p=Path('worker-r76.js')
w=p.read_text(encoding='utf-8')
w=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",w,count=1)
old="const uiHint=languageCode(b.uiLanguage||''),sentHint=languageCode(b.languageHint||''),softHint=sentHint||uiHint;"
new="const uiHint=languageCode(b.uiLanguage||''),sentHint=languageCode(b.languageHint||''),conversationHint=languageCode(b.conversationLanguage||''),softHint=sentHint||conversationHint||uiHint;"
if old in w:w=w.replace(old,new,1)
elif new not in w:raise SystemExit('R123 backend hint anchor missing')
old="const strongHint=nativeFamily&&nativeFamily!=='latin'?nativeLang:'';"
new="const strongHint=nativeFamily&&nativeFamily!=='latin'?nativeLang:conversationHint;"
if old in w:w=w.replace(old,new,1)
elif new not in w:raise SystemExit('R123 backend strong hint anchor missing')
old="// A stale phone recognizer can turn Arabic into Icelandic-looking Latin text. When the active voice hint is Arabic, retry the audio with an explicit Arabic prompt before accepting that mismatch.\n if(text&&strongHint==='ar'&&pickedLanguage==='is'){"
new="// Arabic speech is sometimes labelled as a rare Latin language on mobile. Retry only that suspicious mismatch, or a known Arabic conversation, before accepting it.\n const rareLatinArabicConfusion=new Set(['is','cy','ga','mt']);\n if(text&&((strongHint==='ar'&&pickedLanguage!=='ar')||(rareLatinArabicConfusion.has(pickedLanguage)&&softHint!=='is'&&softHint!=='cy'&&softHint!=='ga'&&softHint!=='mt'))){"
if old in w:w=w.replace(old,new,1)
elif "const rareLatinArabicConfusion=new Set(['is','cy','ga','mt']);" not in w:raise SystemExit('R123 Arabic rescue anchor missing')
old="return json(request,{...d,release:RELEASE,r122:true"
new="return json(request,{...d,release:RELEASE,r123:true,r123Runtime:'single-voice-turn-arabic-auto-rescue',r122:true"
if old in w:w=w.replace(old,new,1)
elif "r123Runtime:'single-voice-turn-arabic-auto-rescue'" not in w:raise SystemExit('R123 health anchor missing')
p.write_text(w,encoding='utf-8')

for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    h=p.read_text(encoding='utf-8')
    n=re.sub(r'r31-ui-polish\.js(?:\?v=[^"\\'<> ]*)?',f'r31-ui-polish.js?v={VER}',h)
    n=re.sub(r'voice-ai\.js(?:\?v=[^"\\'<> ]*)?',f'voice-ai.js?v={VOICE_VER}',n)
    if n!=h:p.write_text(n,encoding='utf-8')

p=Path('sw.js')
sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const CACHE='[^']+';",f"const CACHE='seekvera-r123-single-voice-turn';",sw,count=1)
p.write_text(sw,encoding='utf-8')
print('R123 voice language rescue and single-turn dedupe patched')
