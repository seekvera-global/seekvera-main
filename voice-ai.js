(()=>{
'use strict';
if(window.__seekveraVoiceAI)return;window.__seekveraVoiceAI=true;

const API_BASE=location.hostname.endsWith('workers.dev')?'':'https://seekvera-main.seekvera-global.workers.dev';
const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
const LANGS={en:'en-US',ar:'ar-SA',fr:'fr-FR',zh:'zh-CN',es:'es-ES',hi:'hi-IN',pt:'pt-BR',de:'de-DE',ja:'ja-JP',ko:'ko-KR',id:'id-ID',tr:'tr-TR',ru:'ru-RU',ur:'ur-PK',bn:'bn-BD',vi:'vi-VN',it:'it-IT',sw:'sw-KE',th:'th-TH',fa:'fa-IR',pl:'pl-PL',nl:'nl-NL',ms:'ms-MY',fil:'fil-PH',ha:'ha-NG',yo:'yo-NG',ig:'ig-NG',am:'am-ET'};
const RTL=/^(ar|fa|ur)(-|$)/i;
let recognition=null,listenTimer=null,lastAnswer='',lastLang='',muted=localStorage.getItem('seekvera_voice_muted')==='1';

function currentLocale(){
  const sel=document.getElementById('lang');
  let code=(sel?.value||localStorage.getItem('seekvera_lang')||document.documentElement.lang||navigator.language||'en').toLowerCase();
  const label=sel?.options?.[sel.selectedIndex]?.textContent||'';
  if(/auto/i.test(label))return navigator.language||'en-US';
  code=code.split('_')[0];
  return LANGS[code]||navigator.language||'en-US';
}
function currentCountry(){
  const c=document.getElementById('country');
  return c?.options?.[c.selectedIndex]?.textContent?.trim()||'';
}
function languageName(){
  const l=document.getElementById('lang');
  return l?.options?.[l.selectedIndex]?.textContent?.trim()||currentLocale();
}
function detectSpeechLocale(text){
  const t=String(text||'');
  const selected=currentLocale();
  if(/[\u0600-\u06FF]/.test(t)){const b=selected.split('-')[0].toLowerCase();return ['ar','fa','ur'].includes(b)?selected:'ar-SA';}
  if(/[\u4E00-\u9FFF]/.test(t))return 'zh-CN';
  if(/[\u3040-\u30FF]/.test(t))return 'ja-JP';
  if(/[\uAC00-\uD7AF]/.test(t))return 'ko-KR';
  if(/[\u0900-\u097F]/.test(t))return 'hi-IN';
  if(/[\u0980-\u09FF]/.test(t))return 'bn-BD';
  if(/[\u0E00-\u0E7F]/.test(t))return 'th-TH';
  if(/[\u1200-\u137F]/.test(t))return 'am-ET';
  if(/[\u0400-\u04FF]/.test(t))return 'ru-RU';
  return currentLocale();
}
function escText(v){return String(v??'').replace(/[\u0000-\u001F\u007F]/g,' ').trim().slice(0,1800)}
function stopSpeech(){try{speechSynthesis.cancel()}catch(_){}}
function pickVoice(locale){
  const voices=speechSynthesis.getVoices?.()||[]; if(!voices.length)return null;
  const exact=voices.find(v=>v.lang?.toLowerCase()===locale.toLowerCase()); if(exact)return exact;
  const base=locale.split('-')[0].toLowerCase(); return voices.find(v=>v.lang?.toLowerCase().startsWith(base))||null;
}
function spokenText(text){return String(text||'').replace(/```[\s\S]*?```/g,' ').replace(/https?:\/\/\S+/g,' ').replace(/[*_#>`~|]/g,' ').replace(/(?:^|\s)[•▪◦◆◇▶►]+/g,' ').replace(/\s+/g,' ').trim()}
function speechChunks(text,max=220){const s=spokenText(text);if(!s)return[];const parts=s.split(/(?<=[.!?؟。！？])\s+/);const out=[];let cur='';for(const part of parts){if((cur+' '+part).trim().length<=max)cur=(cur+' '+part).trim();else{if(cur)out.push(cur);if(part.length<=max)cur=part;else{for(let i=0;i<part.length;i+=max)out.push(part.slice(i,i+max));cur=''}}}if(cur)out.push(cur);return out}
function speak(text,locale){
  lastAnswer=String(text||''); lastLang=locale||detectSpeechLocale(text); if(muted||!lastAnswer||!('speechSynthesis'in window))return;
  stopSpeech();
  const chunks=speechChunks(lastAnswer).slice(0,12);let i=0;
  const next=()=>{if(muted||i>=chunks.length)return;const u=new SpeechSynthesisUtterance(chunks[i++]);u.lang=lastLang;const v=pickVoice(lastLang);if(v)u.voice=v;u.rate=/^(ar|fa|ur)(-|$)/i.test(lastLang)?.90:.94;u.pitch=1;u.onend=next;u.onerror=()=>{};speechSynthesis.speak(u)};
  next();
}
function setState(state,msg){
  const btn=document.getElementById('svVoiceFab'),status=document.getElementById('svVoiceStatus');
  if(btn){btn.classList.toggle('listening',state==='listening');btn.classList.toggle('thinking',state==='thinking');btn.textContent=state==='listening'?'■':state==='thinking'?'…':'🎤';}
  if(status)status.textContent=msg||'';
}
function showPanel(open=true){document.getElementById('svVoicePanel')?.classList.toggle('open',open)}
function setTranscript(text){const e=document.getElementById('svVoiceHeard');if(e)e.textContent=text||'—'}
function setAnswer(text){const e=document.getElementById('svVoiceAnswer');if(e)e.textContent=text||'—'}
function toast(text){showPanel(true);setState('idle',text)}

async function askAI(text){
  const clean=escText(text); if(!clean)return;
  showPanel(true);setTranscript(clean);setAnswer('…');setState('thinking','SEEKVERA AI…');
  try{
    let data=null,lastError='AI unavailable';
    for(let attempt=1;attempt<=3;attempt++){
      try{
        const res=await fetch(`${API_BASE}/api/ai`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({message:clean,country:currentCountry(),language:languageName(),voice:true})});
        data=await res.json().catch(()=>({}));
        if(res.ok&&data?.response)break;
        lastError=data?.error||('AI HTTP '+res.status);
      }catch(e){lastError=e?.message||'AI unavailable'}
      if(attempt<3)await new Promise(r=>setTimeout(r,700*attempt));
    }
    if(!data?.response)throw new Error(lastError);
    const answer=String(data.response).trim(); setAnswer(answer);setState('idle','');
    const locale=detectSpeechLocale(answer); speak(answer,locale);
    try{
      const msgs=document.getElementById('aiMessages');
      if(msgs){
        const u=document.createElement('div');u.className='ai-msg user';u.textContent=clean;msgs.appendChild(u);
        const b=document.createElement('div');b.className='ai-msg bot';b.textContent=answer;msgs.appendChild(b);msgs.scrollTop=msgs.scrollHeight;
      }
    }catch(_){ }
  }catch(err){setAnswer('SEEKVERA AI is temporarily unavailable. Please try again.');setState('idle','');}
}

function stopListening(){
  if(listenTimer){clearTimeout(listenTimer);listenTimer=null}
  if(recognition){try{recognition.stop()}catch(_){ }recognition=null}
  setState('idle','');
}
function startListening(){
  stopSpeech();
  if(recognition){stopListening();return}
  showPanel(true);
  if(!SpeechRecognition){toast('Voice recognition is not available in this browser. Use Chrome/Android or type your request.');return}
  const r=new SpeechRecognition();recognition=r;r.lang=currentLocale();r.interimResults=true;r.continuous=false;r.maxAlternatives=1;
  let finalText='';
  r.onstart=()=>{setState('listening','Listening…');setTranscript('…');setAnswer('—')};
  r.onresult=e=>{let interim='';for(let i=e.resultIndex;i<e.results.length;i++){const s=e.results[i][0].transcript;if(e.results[i].isFinal)finalText+=(finalText?' ':'')+s;else interim+=s}setTranscript((finalText||interim).trim()||'…')};
  r.onerror=e=>{if(e.error==='not-allowed'||e.error==='service-not-allowed')toast('Microphone permission is blocked. Allow microphone access for SEEKVERA, then tap 🎤 again.');else if(e.error!=='aborted'&&e.error!=='no-speech')toast('I could not hear you clearly. Tap 🎤 and try again.')};
  r.onend=()=>{if(listenTimer){clearTimeout(listenTimer);listenTimer=null}recognition=null;setState('idle','');const text=finalText.trim()||document.getElementById('svVoiceHeard')?.textContent?.trim();if(text&&text!=='…'&&text!=='—')askAI(text)};
  try{r.start();listenTimer=setTimeout(()=>{try{r.stop()}catch(_){ }},20000)}catch(_){recognition=null;toast('Voice could not start. Tap 🎤 and try again.')}
}

function build(){
  const old=document.getElementById('voiceFloat'); if(old&&location.pathname.endsWith('/app.html'))old.style.display='none';
  if(location.pathname.endsWith('/app.html'))return;
  if(document.getElementById('svVoiceFab'))return;
  const style=document.createElement('style');style.id='svVoiceStyle';style.textContent=`
#svVoiceFab{position:fixed;right:18px;bottom:88px;z-index:2147483000;width:54px;height:54px;border:0;border-radius:50%;display:grid;place-items:center;background:#152a45;color:#fff;font-size:23px;box-shadow:0 10px 30px rgba(0,0,0,.28);cursor:pointer}#svVoiceFab.listening{background:#d92d20;animation:svp .9s infinite}#svVoiceFab.thinking{background:#20ad74}@keyframes svp{50%{transform:scale(1.08)}}
#svVoicePanel{position:fixed;right:14px;bottom:154px;z-index:2147482999;width:min(360px,calc(100vw - 28px));max-height:62vh;overflow:auto;background:#fff;color:#142033;border:1px solid #dfe5eb;border-radius:17px;box-shadow:0 18px 50px rgba(0,0,0,.23);padding:14px;display:none;font-family:Arial,Helvetica,sans-serif;text-align:left}#svVoicePanel.open{display:block}#svVoicePanel[dir=rtl]{text-align:right}.svh{display:flex;align-items:center;gap:8px;margin-bottom:9px}.svh b{flex:1}.svx,.svc{border:1px solid #dfe5eb;background:#f7f9fb;color:#142033;border-radius:9px;padding:7px 9px;cursor:pointer}.svbox{background:#f7f9fb;border-radius:11px;padding:10px;margin-top:8px;white-space:pre-wrap;word-break:break-word}.svlab{font-size:11px;color:#667085;font-weight:800;text-transform:uppercase}.svstatus{font-size:12px;color:#087a4f;min-height:18px;margin-top:7px}.svfoot{display:flex;gap:7px;margin-top:10px;flex-wrap:wrap}.svfoot button{border:0;border-radius:9px;padding:8px 10px;font-weight:800;cursor:pointer}.svprimary{background:#20ad74;color:#fff}.svsecondary{background:#eef2f6;color:#142033}.svnote{font-size:10px;color:#7a8699;margin-top:8px}
@media(max-width:560px){#svVoiceFab{right:12px;bottom:78px;width:52px;height:52px}#svVoicePanel{right:8px;bottom:140px;width:calc(100vw - 16px)}}`;
  document.head.appendChild(style);
  const panel=document.createElement('section');panel.id='svVoicePanel';panel.setAttribute('aria-label','SEEKVERA Voice AI');panel.setAttribute('aria-live','polite');panel.dir=RTL.test(currentLocale())?'rtl':'ltr';panel.innerHTML=`<div class="svh"><span>✨</span><b>SEEKVERA Voice AI</b><button class="svc" id="svMute" type="button" aria-label="Mute voice">${muted?'🔇':'🔊'}</button><button class="svx" id="svVoiceClose" type="button" aria-label="Close">×</button></div><div class="svlab">You said</div><div class="svbox" id="svVoiceHeard">—</div><div class="svlab" style="margin-top:9px">SEEKVERA</div><div class="svbox" id="svVoiceAnswer">Tap 🎤 and speak in your language.</div><div class="svstatus" id="svVoiceStatus"></div><div class="svfoot"><button class="svprimary" id="svTalkAgain" type="button">🎤 Speak</button><button class="svsecondary" id="svReplay" type="button">↻ Replay</button></div><div class="svnote">Mic turns off after you finish speaking. Do not say passwords, card details or other sensitive information.</div>`;
  const fab=document.createElement('button');fab.id='svVoiceFab';fab.type='button';fab.textContent='🎤';fab.title='Speak to SEEKVERA AI';fab.setAttribute('aria-label','Speak to SEEKVERA AI');
  document.body.append(panel,fab);
  fab.addEventListener('click',()=>{if(speechSynthesis?.speaking)stopSpeech();startListening()});
  document.getElementById('svTalkAgain').addEventListener('click',startListening);
  document.getElementById('svVoiceClose').addEventListener('click',()=>{stopListening();stopSpeech();showPanel(false)});
  document.getElementById('svReplay').addEventListener('click',()=>{if(lastAnswer)speak(lastAnswer,lastLang||detectSpeechLocale(lastAnswer))});
  document.getElementById('svMute').addEventListener('click',e=>{muted=!muted;localStorage.setItem('seekvera_voice_muted',muted?'1':'0');e.currentTarget.textContent=muted?'🔇':'🔊';if(muted)stopSpeech();else if(lastAnswer)speak(lastAnswer,lastLang)});
}

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',build,{once:true});else build();
})();
