from pathlib import Path
import re

VER='20260926-r61-country-chat-server-voice'
OLD='20260926-r60-chat-voice-persist'

# 1) One cache-busted runtime everywhere.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    s=p.read_text(encoding='utf-8')
    s=s.replace(OLD,VER)
    s=re.sub(r'navigation\.js(?:\?v=[^"\'<> ]*)?',f'navigation.js?v={VER}',s)
    s=re.sub(r'r24-ai-controller\.js(?:\?v=[^"\'<> ]*)?',f'r24-ai-controller.js?v={VER}',s)
    s=re.sub(r'voice-ai\.js(?:\?v=[^"\'<> ]*)?',f'voice-ai.js?v={VER}',s)
    s=re.sub(r'r31-ui-polish\.js(?:\?v=[^"\'<> ]*)?',f'r31-ui-polish.js?v={VER}',s)
    s=re.sub(r'r60-runtime-guard\.js(?:\?v=[^"\'<> ]*)?',f'r60-runtime-guard.js?v={VER}',s)
    s=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',s,count=1)
    p.write_text(s,encoding='utf-8')

# 2) Remove the legacy submit interceptor that creates repeated `🌍 Country ✓` bubbles.
p=Path('navigation.js'); s=p.read_text(encoding='utf-8')
old="function init(){stripDuplicateDepartments();buildNav();hardenAIUI();bindLocaleControls();bindAICountryControl();scheduleLocalePass()}"
new="function init(){stripDuplicateDepartments();buildNav();hardenAIUI();bindLocaleControls();scheduleLocalePass()}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('navigation init anchor missing')
p.write_text(s,encoding='utf-8')

# 3) The R24 controller is now the single worldwide language/country command authority.
p=Path('r24-ai-controller.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"const VERSION='[^']+';",f"const VERSION='{VER}';",s,count=1)
p.write_text(s,encoding='utf-8')

# 4) Persistent chat: migrate away legacy country-status bubbles and de-duplicate rows.
p=Path('r60-runtime-guard.js')
p.write_text(r'''(()=>{'use strict';
const RELEASE='20260926-r61-country-chat-server-voice';
const CHAT_KEY='seekvera_ai_chat_v1',CHAT_MAX=100;
document.documentElement.dataset.seekveraRelease=RELEASE;
function cleanVisualState(){document.documentElement.classList.remove('sv-r31-switching');try{document.body?.classList.remove('sv-r31-switching')}catch{}}
function box(){return document.querySelector('#aiMessages')}
function legacyStatus(t){return /^\s*🌍\s*.+\s*✓\s*$/u.test(String(t||''))}
function cleanRows(rows){const out=[];for(const x of Array.isArray(rows)?rows:[]){const role=x?.role==='user'?'user':'assistant',text=String(x?.text||'').trim().slice(0,4000);if(!text||legacyStatus(text))continue;const prev=out[out.length-1];if(prev&&prev.role===role&&prev.text===text)continue;out.push({role,text})}return out.slice(-CHAT_MAX)}
function safeRead(){try{return cleanRows(JSON.parse(localStorage.getItem(CHAT_KEY)||'[]'))}catch{return[]}}
function writeRows(rows){try{localStorage.setItem(CHAT_KEY,JSON.stringify(cleanRows(rows)))}catch{}}
function saveChat(){const b=box();if(!b)return;const rows=[...b.querySelectorAll('.ai-msg')].filter(n=>!n.classList.contains('thinking')).map(n=>({role:n.classList.contains('user')?'user':'assistant',text:String(n.textContent||'').trim()}));writeRows(rows)}
function restoreChat(){const b=box(),rows=safeRead();if(!b||!rows.length)return false;writeRows(rows);b.innerHTML='';for(const x of rows){const m=document.createElement('div');m.className='ai-msg '+(x.role==='user'?'user':'bot');m.dataset.persisted='1';m.textContent=x.text;b.appendChild(m)}b.scrollTop=b.scrollHeight;return true}
let saveTimer=0;function scheduleSave(){clearTimeout(saveTimer);saveTimer=setTimeout(saveChat,40)}
function watchChat(){const b=box();if(!b)return;restoreChat();new MutationObserver(scheduleSave).observe(b,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['class']});window.addEventListener('seekvera:ai-response',saveChat);window.addEventListener('seekvera:ai-control',saveChat);window.addEventListener('pagehide',saveChat)}
function enableVoiceMode(){try{localStorage.setItem('seekvera_voice_mode','1');localStorage.setItem('seekvera_voice_muted','0')}catch{}try{window.SEEKVERA_VOICE_AI?.prepareVoice?.();speechSynthesis.resume()}catch{}}
document.addEventListener('pointerdown',e=>{if(e.target.closest?.('#aiChatMic,.sv-global-compose .mic,#aiChatSpeaker,.sv-global-speaker'))enableVoiceMode()},{capture:true});
window.addEventListener('pageshow',()=>{cleanVisualState();setTimeout(()=>{if(box()&&safeRead().length)restoreChat()},0)});document.addEventListener('visibilitychange',()=>{if(!document.hidden)cleanVisualState()});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',watchChat,{once:true});else watchChat();
if('serviceWorker' in navigator){const install=()=>navigator.serviceWorker.register('/sw.js?v='+RELEASE,{updateViaCache:'none'}).then(async r=>{try{await r.update()}catch{}if(r.waiting)try{r.waiting.postMessage('SKIP_WAITING')}catch{}}).catch(()=>{});if(document.readyState==='complete')install();else window.addEventListener('load',install,{once:true})}
window.SEEKVERA_RELEASE=RELEASE;window.SEEKVERA_CHAT={save:saveChat,restore:restoreChat,clear:()=>{try{localStorage.removeItem(CHAT_KEY)}catch{}const b=box();if(b)b.innerHTML=''}};
})();
''',encoding='utf-8')

# 5) Save immediately before category navigation and after each user message.
p=Path('r31-ui-polish.js'); s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
s=s.replace("const go=()=>location.assign(routeUrl(cat,q));","const go=()=>{try{window.SEEKVERA_CHAT?.save?.()}catch{}location.assign(routeUrl(cat,q))};",1)
s=s.replace("if(input)input.value='';appendMsg('user',q);const ctl=controlResult(q);","if(input)input.value='';appendMsg('user',q);try{window.SEEKVERA_CHAT?.save?.()}catch{}const ctl=controlResult(q);",1)
p.write_text(s,encoding='utf-8')

# 6) Real Android/server audio fallback. Browser synthesis remains the free first path on non-Android.
p=Path('voice-ai.js'); s=p.read_text(encoding='utf-8')
start=s.find('function stopSpeech(){'); end=s.find('\nfunction cleanSpeech',start)
if start<0 or end<0:raise SystemExit('voice stopSpeech boundary missing')
s=s[:start]+'''let serverAudioCtx=null,serverAudioSource=null,serverAudioEl=null,serverAudioUrl='';
function prepareServerAudio(){try{const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return false;if(!serverAudioCtx||serverAudioCtx.state==='closed')serverAudioCtx=new AC();if(serverAudioCtx.state==='suspended')serverAudioCtx.resume();return true}catch(_){return false}}
function stopServerAudio(){try{serverAudioSource?.stop?.()}catch(_){}serverAudioSource=null;try{serverAudioEl?.pause?.()}catch(_){}serverAudioEl=null;if(serverAudioUrl){try{URL.revokeObjectURL(serverAudioUrl)}catch(_){}serverAudioUrl=''}}
function stopSpeech(){speakToken++;stopServerAudio();try{window.speechSynthesis?.cancel?.()}catch(_){}}'''+s[end:]

# Replace unlock function but keep a persistent, gesture-unlocked AudioContext.
start=s.find('function unlockTTS(){'); end=s.find('\nfunction enableVoiceConversation',start)
if start<0 or end<0:raise SystemExit('voice unlock boundary missing')
unlock="""function unlockTTS(){prepareServerAudio();if(!hasTTS())return;try{speechSynthesis.cancel();speechSynthesis.getVoices?.();speechSynthesis.resume();const u=new SpeechSynthesisUtterance(' ');u.volume=.01;u.rate=2;speechSynthesis.speak(u);setTimeout(()=>{try{speechSynthesis.cancel();speechSynthesis.getVoices?.();speechSynthesis.resume()}catch(_){}},90)}catch(_){}}"""
s=s[:start]+unlock+s[end:]

# Replace output engine: Android gets server MP3 first, then native fallback.
start=s.find('function speak(text,l,force=false){'); end=s.find('\nfunction setMic',start)
if start<0 or end<0:raise SystemExit('voice speak boundary missing')
new_speak=r'''async function serverSpeak(text,loc,token){const spoken=cleanSpeech(text).slice(0,1200);if(!spoken||token!==speakToken||muted)return false;try{prepareServerAudio();const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),9000),r=await fetch(apiBase()+'/api/tts',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({text:spoken,language:String(loc||'auto')}),signal:ctl.signal,cache:'no-store'}).finally(()=>clearTimeout(to));if(!r.ok)return false;const buf=await r.arrayBuffer();if(!buf.byteLength||token!==speakToken)return false;if(prepareServerAudio()&&serverAudioCtx){try{const audio=await serverAudioCtx.decodeAudioData(buf.slice(0));if(token!==speakToken)return false;serverAudioSource=serverAudioCtx.createBufferSource();serverAudioSource.buffer=audio;serverAudioSource.connect(serverAudioCtx.destination);serverAudioSource.onended=()=>{serverAudioSource=null;if(token===speakToken){voiceConversation=false;window.dispatchEvent(new CustomEvent('seekvera:tts-end',{detail:{language:loc,engine:'server'}}))}};window.dispatchEvent(new CustomEvent('seekvera:tts-start',{detail:{language:loc,engine:'server'}}));serverAudioSource.start(0);return true}catch(_){}}
const blob=new Blob([buf],{type:r.headers.get('content-type')||'audio/mpeg'});serverAudioUrl=URL.createObjectURL(blob);serverAudioEl=new Audio(serverAudioUrl);serverAudioEl.preload='auto';serverAudioEl.onplaying=()=>window.dispatchEvent(new CustomEvent('seekvera:tts-start',{detail:{language:loc,engine:'server-audio'}}));serverAudioEl.onended=()=>{if(token===speakToken){voiceConversation=false;window.dispatchEvent(new CustomEvent('seekvera:tts-end',{detail:{language:loc,engine:'server-audio'}}))}stopServerAudio()};await serverAudioEl.play();return true}catch(_){return false}}
function nativeSpeak(chunks,token){if(!hasTTS())return false;try{speechSynthesis.cancel();speechSynthesis.resume()}catch(_){}const play=(index,attempt=0)=>{if(token!==speakToken||muted)return;if(index>=chunks.length){if(token===speakToken){voiceConversation=false;window.dispatchEvent(new CustomEvent('seekvera:tts-end',{detail:{language:lastLocale,engine:'native'}}))}return}if(recognition){setTimeout(()=>play(index,attempt),150);return}try{const u=new SpeechSynthesisUtterance(chunks[index]);u.lang=lastLocale;const v=pickVoice(lastLocale);if(v)u.voice=v;u.rate=1;u.pitch=1.02;u.volume=1;let started=false,finished=false;u.onstart=()=>{started=true;window.dispatchEvent(new CustomEvent('seekvera:tts-start',{detail:{language:lastLocale,engine:'native'}}))};u.onend=()=>{finished=true;if(token===speakToken)play(index+1,0)};u.onerror=()=>{if(finished||token!==speakToken)return;if(!started&&attempt<TTS_RETRY_DELAYS.length-1)setTimeout(()=>play(index,attempt+1),TTS_RETRY_DELAYS[attempt+1]);else play(index+1,0)};speechSynthesis.resume();speechSynthesis.speak(u);setTimeout(()=>{if(finished||started||token!==speakToken)return;if(!speechSynthesis.speaking&&attempt<TTS_RETRY_DELAYS.length-1){try{speechSynthesis.cancel();speechSynthesis.resume()}catch(_){}play(index,attempt+1)}},TTS_RETRY_DELAYS[attempt]+500)}catch(_){if(attempt<TTS_RETRY_DELAYS.length-1)setTimeout(()=>play(index,attempt+1),TTS_RETRY_DELAYS[attempt+1]);else play(index+1,0)}};play(0,0);return true}
function speak(text,l,force=false){lastAnswer=typeof text==='string'?text:'';lastLocale=localeForText(lastAnswer,l);const chunks=splitSpeech(lastAnswer);if(force){muted=false;localStorage.setItem('seekvera_voice_muted','0');localStorage.setItem('seekvera_voice_mode','1');updateSpeakerButtons()}if(muted||!chunks.length){if(force)voiceConversation=false;return}const token=++speakToken,android=/Android/i.test(navigator.userAgent);if(android){serverSpeak(lastAnswer,lastLocale,token).then(ok=>{if(!ok&&token===speakToken&&!muted)nativeSpeak(chunks,token)});return}if(!nativeSpeak(chunks,token))serverSpeak(lastAnswer,lastLocale,token)}'''
s=s[:start]+new_speak+s[end:]

# Expose the real server player for diagnostics and gesture preparation.
s=s.replace("supportedLanguages:Object.keys(LANGS),resolveLocale:(text,requested)=>localeForText(text,requested)};","supportedLanguages:Object.keys(LANGS),resolveLocale:(text,requested)=>localeForText(text,requested),prepareVoice:unlockTTS,serverSpeak:(text,requested)=>{const token=++speakToken;return serverSpeak(text,localeForText(text,requested),token)}};",1)
p.write_text(s,encoding='utf-8')

# 7) Worker TTS endpoint. Cheap Cloudflare Melo first for its strong languages; Inworld covers the wider multilingual fallback.
p=Path('worker-r31.js'); s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
anchor='async function inject(resp)'
if 'async function serverTTS(' not in s:
    helper=r'''async function serverTTS(req,env){if(req.method!=='POST')return json(req,{ok:false,error:'POST required'},405);let b={};try{b=await req.json()}catch{}const text=clean(b.text,1200),lang=inputLangCode(b.language||b.lang||'en');if(!text)return json(req,{ok:false,error:'text required'},400);if(!env.AI)return json(req,{ok:false,error:'voice unavailable'},503);const audioResp=async r=>{if(!(r instanceof Response)||!r.ok)return null;const h=new Headers(r.headers);h.set('content-type',h.get('content-type')||'audio/mpeg');h.set('cache-control','no-store');const o=req.headers.get('origin')||'';if(ALLOWED.has(o))h.set('access-control-allow-origin',o);h.set('vary','Origin');h.set('x-seekvera-tts','server');return new Response(r.body,{status:200,headers:h})};const melo=new Set(['en','es','fr','zh','ja','ko']);if(melo.has(lang)){try{const r=await env.AI.run('@cf/myshell-ai/melotts',{prompt:text,lang},{returnRawResponse:true}),a=await audioResp(r);if(a)return a}catch{}}try{const x=await env.AI.run('inworld/tts-2',{output_format:'mp3',temperature:.8,text,timestamp_type:'none',voice_id:'Olivia',apply_text_normalization:true}),url=x?.result?.audio||x?.audio;if(url&&/^https:\/\//i.test(url)){const r=await fetch(url),a=await audioResp(r);if(a)return a}}catch{}try{const r=await env.AI.run('@cf/myshell-ai/melotts',{prompt:text,lang},{returnRawResponse:true}),a=await audioResp(r);if(a)return a}catch{}return json(req,{ok:false,error:'voice generation unavailable',language:lang},503)}
'''
    if anchor not in s:raise SystemExit('worker inject anchor missing')
    s=s.replace(anchor,helper+anchor,1)
old="export default{async fetch(request,env,ctx){const u=new URL(request.url);"
new="export default{async fetch(request,env,ctx){const u=new URL(request.url);if(u.pathname==='/api/tts')return serverTTS(request,env);"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('worker export anchor missing')
s=s.replace("h.set('x-seekvera-release','r60-chat-voice-persist')","h.set('x-seekvera-release','r61-country-chat-server-voice')")
p.write_text(s,encoding='utf-8')

# 8) Keep PWA registration but no fetch interception; bump release only.
p=Path('sw.js'); s=p.read_text(encoding='utf-8').replace(OLD,VER);p.write_text(s,encoding='utf-8')
print('R61 country/chat/server-voice patch complete')
