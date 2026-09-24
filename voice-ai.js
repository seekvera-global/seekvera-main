(()=>{
'use strict';
if(window.__seekveraVoiceAI)return;window.__seekveraVoiceAI=true;
const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
const LANGS={en:'en-US',ar:'ar-SA',fr:'fr-FR',zh:'zh-CN',es:'es-ES',hi:'hi-IN',pt:'pt-BR',de:'de-DE',ja:'ja-JP',ko:'ko-KR',id:'id-ID',tr:'tr-TR',ru:'ru-RU',ur:'ur-PK',bn:'bn-BD',vi:'vi-VN',it:'it-IT',sw:'sw-KE',th:'th-TH',fa:'fa-IR',pl:'pl-PL',nl:'nl-NL',ms:'ms-MY',fil:'fil-PH',ha:'ha-NG',yo:'yo-NG',ig:'ig-NG',am:'am-ET',he:'he-IL',el:'el-GR',uk:'uk-UA',ro:'ro-RO',cs:'cs-CZ',sk:'sk-SK',hu:'hu-HU',sv:'sv-SE',no:'nb-NO',da:'da-DK',fi:'fi-FI',bg:'bg-BG',hr:'hr-HR',sr:'sr-RS',sl:'sl-SI',lt:'lt-LT',lv:'lv-LV',et:'et-EE',ca:'ca-ES',eu:'eu-ES',gl:'gl-ES',is:'is-IS',sq:'sq-AL',mk:'mk-MK',ka:'ka-GE',hy:'hy-AM',az:'az-AZ',kk:'kk-KZ',uz:'uz-UZ',ky:'ky-KG',tg:'tg-TJ',tk:'tk-TM',ne:'ne-NP',si:'si-LK',ta:'ta-IN',te:'te-IN',ml:'ml-IN',mr:'mr-IN',gu:'gu-IN',pa:'pa-IN',km:'km-KH',lo:'lo-LA',my:'my-MM',mn:'mn-MN',zu:'zu-ZA',af:'af-ZA',be:'be-BY',bs:'bs-BA',dz:'dz-BT',ti:'ti-ET',fo:'fo-FO',kl:'kl-GL',rw:'rw-RW',sm:'sm-WS',to:'to-TO',so:'so-SO',ps:'ps-AF',dv:'dv-MV',mt:'mt-MT',mg:'mg-MG',ga:'ga-IE',cy:'cy-GB',mi:'mi-NZ',fy:'fy-NL',lb:'lb-LU',rm:'rm-CH',ku:'ku-TR',xh:'xh-ZA',st:'st-ZA',tn:'tn-BW'};
const NAME_CODE={english:'en',arabic:'ar',french:'fr',chinese:'zh',mandarin:'zh',spanish:'es',hindi:'hi',portuguese:'pt',german:'de',japanese:'ja',korean:'ko',indonesian:'id',turkish:'tr',russian:'ru',urdu:'ur',bengali:'bn',vietnamese:'vi',italian:'it',swahili:'sw',thai:'th',persian:'fa',farsi:'fa',polish:'pl',dutch:'nl',malay:'ms',filipino:'fil',tagalog:'fil',hausa:'ha',yoruba:'yo',igbo:'ig',amharic:'am',hebrew:'he',greek:'el',ukrainian:'uk',romanian:'ro',czech:'cs',slovak:'sk',hungarian:'hu',swedish:'sv',norwegian:'no',danish:'da',finnish:'fi',bulgarian:'bg',croatian:'hr',serbian:'sr',slovenian:'sl',lithuanian:'lt',latvian:'lv',estonian:'et',catalan:'ca',basque:'eu',galician:'gl',icelandic:'is',albanian:'sq',macedonian:'mk',georgian:'ka',armenian:'hy',azerbaijani:'az',kazakh:'kk',uzbek:'uz',kyrgyz:'ky',tajik:'tg',turkmen:'tk',nepali:'ne',sinhala:'si',tamil:'ta',telugu:'te',malayalam:'ml',marathi:'mr',gujarati:'gu',punjabi:'pa',khmer:'km',lao:'lo',burmese:'my',mongolian:'mn',zulu:'zu',afrikaans:'af',belarusian:'be',bosnian:'bs',dzongkha:'dz',tigrinya:'ti',faroese:'fo',greenlandic:'kl',kalaallisut:'kl',kinyarwanda:'rw',samoan:'sm',tongan:'to',somali:'so',pashto:'ps',dhivehi:'dv',maldivian:'dv',maltese:'mt',malagasy:'mg',irish:'ga',welsh:'cy',maori:'mi',frisian:'fy',luxembourgish:'lb',romansh:'rm',kurdish:'ku',xhosa:'xh',sesotho:'st','southern sotho':'st',tswana:'tn',setswana:'tn'};
const FEMALE_HINTS=/aria|jenny|zira|samantha|victoria|karen|moira|tessa|ava|allison|susan|hazel|fiona|serena|veena|heera|lekha|monica|amelie|audrey|julie|celine|hortense|laila|layla|salma|hoda|farah|mariam|maryam|amira|zahra|female|woman/i;
const MALE_HINTS=/david|mark|george|daniel|fred|ralph|bruce|hammad|hamed|majed|maged|male|man/i;
const QUALITY_HINTS=/neural|natural|enhanced|premium|online|google|microsoft|siri/i;
const TTS_RETRY_DELAYS=[240,650,1200];
const VOICE_SILENCE_MS=3200,VOICE_MAX_MS=90000,VOICE_RMS_THRESHOLD=.018;
let recognition=null,lastAnswer='',lastLocale='',muted=localStorage.getItem('seekvera_voice_muted')==='1',activeButton=null,voiceConversation=false,speakToken=0,recording=false,mediaRecorder=null,mediaStream=null,recordChunks=[],recordTimer=null,speechSilenceTimer=null,speechHardTimer=null,audioCtx=null,audioAnalyser=null,audioSource=null,audioRaf=0,heardVoice=false,lastVoiceAt=0,recordStartedAt=0;
function codeOf(v){let s=String(v||'').toLowerCase().trim();if(NAME_CODE[s])return NAME_CODE[s];s=s.split(/[-_ ]/)[0];if(NAME_CODE[s])return NAME_CODE[s];return /^[a-z]{2,3}$/.test(s)?s:''}
function locale(){const e=document.getElementById('lang');let code=(e?.value||localStorage.getItem('seekvera_lang')||navigator.language||'en').toLowerCase();const label=e?.options?.[e.selectedIndex]?.textContent||'';if(code==='auto'||/auto|تلقائي|autom/i.test(label))return navigator.language||'en-US';code=codeOf(code)||code.split(/[-_]/)[0];return LANGS[code]||code||navigator.language||'en-US'}
function localeForText(t,requested){t=typeof t==='string'?t:'';const r=codeOf(requested);if(r)return LANGS[r]||r;if(/[\u0600-\u06ff]/.test(t))return 'ar-SA';if(/[\u4e00-\u9fff]/.test(t))return 'zh-CN';if(/[\u3040-\u30ff]/.test(t))return 'ja-JP';if(/[\uac00-\ud7af]/.test(t))return 'ko-KR';if(/[\u0900-\u097f]/.test(t))return 'hi-IN';if(/[\u0980-\u09ff]/.test(t))return 'bn-BD';if(/[\u0400-\u04ff]/.test(t))return 'ru-RU';if(/[\u0590-\u05ff]/.test(t))return 'he-IL';if(/[\u0370-\u03ff]/.test(t))return 'el-GR';if(/[\u0e00-\u0e7f]/.test(t))return 'th-TH';if(/[\u1200-\u137f]/.test(t))return 'am-ET';return locale()}
function voices(){try{return window.speechSynthesis?.getVoices?.()||[]}catch(_){return []}}
function pickVoice(l){const vs=voices();if(!vs.length)return null;const w=String(l||'').toLowerCase(),b=w.split('-')[0];let c=vs.filter(v=>String(v.lang||'').toLowerCase().startsWith(b));if(!c.length)return null;const sc=v=>{const n=(v.name||'')+' '+(v.voiceURI||''),vl=String(v.lang||'').toLowerCase();let x=0;if(vl===w)x+=120;else if(vl.startsWith(b))x+=75;if(QUALITY_HINTS.test(n))x+=40;if(FEMALE_HINTS.test(n))x+=48;if(MALE_HINTS.test(n))x-=60;if(v.default)x+=8;return x};return [...c].sort((a,b)=>sc(b)-sc(a))[0]||null}
function hasTTS(){return 'speechSynthesis'in window&&'SpeechSynthesisUtterance'in window}
function updateSpeakerButtons(){document.querySelectorAll('#aiChatSpeaker,.sv-global-speaker').forEach(b=>{b.textContent=muted?'🔇':'🔊';b.setAttribute('aria-label',muted?'Turn voice replies on':'Turn voice replies off');b.setAttribute('aria-pressed',muted?'false':'true')})}
function stopSpeech(){speakToken++;try{window.speechSynthesis?.cancel?.()}catch(_){}}
function cleanSpeech(t){return(typeof t==='string'?t:'').replace(/```[\s\S]*?```/g,' ').replace(/https?:\/\/\S+/g,' ').replace(/[*_#>`~|]/g,' ').replace(/\s+/g,' ').trim()}
function splitSpeech(t){const s=cleanSpeech(t);if(!s)return[];const parts=s.match(/[^.!?。！？؛،,:;]{1,170}(?:[.!?。！？؛،,:;]+|$)/g)||[];const out=[];for(const p0 of parts){let p=p0.trim();while(p.length>190){let cut=p.lastIndexOf(' ',180);if(cut<80)cut=180;out.push(p.slice(0,cut).trim());p=p.slice(cut).trim()}if(p)out.push(p)}return out.length?out:[s.slice(0,190)]}
function unlockTTS(){if(!hasTTS())return;try{speechSynthesis.getVoices?.();speechSynthesis.resume();const u=new SpeechSynthesisUtterance(' ');u.volume=0;u.rate=1;speechSynthesis.speak(u);setTimeout(()=>{try{speechSynthesis.getVoices?.();speechSynthesis.resume()}catch(_){}},60)}catch(_){}}
function enableVoiceConversation(){voiceConversation=true;muted=false;localStorage.setItem('seekvera_voice_muted','0');updateSpeakerButtons();unlockTTS()}
function speak(text,l,force=false){lastAnswer=typeof text==='string'?text:'';lastLocale=localeForText(lastAnswer,l);const chunks=splitSpeech(lastAnswer);if(force){muted=false;localStorage.setItem('seekvera_voice_muted','0');updateSpeakerButtons()}if(muted||!chunks.length||!hasTTS()){if(force)voiceConversation=false;return}const token=++speakToken;try{speechSynthesis.cancel();speechSynthesis.resume()}catch(_){}const play=(index,attempt=0)=>{if(token!==speakToken||muted)return;if(index>=chunks.length){if(token===speakToken)voiceConversation=false;return}if(recognition){setTimeout(()=>play(index,attempt),150);return}try{const u=new SpeechSynthesisUtterance(chunks[index]);u.lang=lastLocale;const v=pickVoice(lastLocale);if(v)u.voice=v;u.rate=1.01;u.pitch=1.05;u.volume=1;let started=false,finished=false;u.onstart=()=>{started=true};u.onend=()=>{finished=true;if(token===speakToken)play(index+1,0)};u.onerror=()=>{if(finished||token!==speakToken)return;if(!started&&attempt<TTS_RETRY_DELAYS.length-1)setTimeout(()=>play(index,attempt+1),TTS_RETRY_DELAYS[attempt+1]);else if(token===speakToken)play(index+1,0)};speechSynthesis.resume();speechSynthesis.speak(u);setTimeout(()=>{if(finished||started||token!==speakToken)return;try{speechSynthesis.resume()}catch(_){}if(!speechSynthesis.speaking&&attempt<TTS_RETRY_DELAYS.length-1)play(index,attempt+1)},TTS_RETRY_DELAYS[attempt]+500)}catch(_){if(attempt<TTS_RETRY_DELAYS.length-1)setTimeout(()=>play(index,attempt+1),TTS_RETRY_DELAYS[attempt+1]);else play(index+1,0)}};setTimeout(()=>play(0,0),force?0:50)}
function setMic(on){if(!activeButton)return;activeButton.classList.toggle('listening',on);activeButton.textContent=on?'■':'🎤';activeButton.setAttribute('aria-label',on?'Stop listening':'Speak to SEEKVERA AI')}
function apiBase(){return /(^|\.)seekveraglobal\.com$/i.test(location.hostname)||location.hostname.endsWith('.workers.dev')?'':'https://seekvera-main.seekvera-global.workers.dev'}
function selectedLang(){const e=document.getElementById('lang');const c=String(e?.value||localStorage.getItem('seekvera_lang')||'auto').toLowerCase();return c==='auto'?'':c.split(/[-_]/)[0]}
function blobDataURL(blob){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result||''));r.onerror=()=>reject(r.error||Error('audio read failed'));r.readAsDataURL(blob)})}
function stopAudioMonitor(){if(audioRaf){cancelAnimationFrame(audioRaf);audioRaf=0}try{audioSource?.disconnect?.()}catch(_){}audioSource=null;audioAnalyser=null;try{audioCtx?.close?.()}catch(_){}audioCtx=null;heardVoice=false;lastVoiceAt=0;recordStartedAt=0}
function clearSpeechTimers(){if(speechSilenceTimer){clearTimeout(speechSilenceTimer);speechSilenceTimer=null}if(speechHardTimer){clearTimeout(speechHardTimer);speechHardTimer=null}}
function releaseStream(){if(recordTimer){clearTimeout(recordTimer);recordTimer=null}clearSpeechTimers();stopAudioMonitor();try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false)}
function startAudioMonitor(stream,onSilence){try{const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;audioCtx=new AC();audioSource=audioCtx.createMediaStreamSource(stream);audioAnalyser=audioCtx.createAnalyser();audioAnalyser.fftSize=1024;audioAnalyser.smoothingTimeConstant=.25;audioSource.connect(audioAnalyser);const data=new Float32Array(audioAnalyser.fftSize);recordStartedAt=performance.now();const tick=()=>{if(!audioAnalyser||!recording)return;audioAnalyser.getFloatTimeDomainData(data);let sum=0;for(let i=0;i<data.length;i++)sum+=data[i]*data[i];const rms=Math.sqrt(sum/data.length),now=performance.now();if(rms>VOICE_RMS_THRESHOLD){heardVoice=true;lastVoiceAt=now}if(heardVoice&&lastVoiceAt&&now-lastVoiceAt>=VOICE_SILENCE_MS&&now-recordStartedAt>700){onSilence();return}audioRaf=requestAnimationFrame(tick)};audioRaf=requestAnimationFrame(tick)}catch(_){stopAudioMonitor()}}
async function serverVoice(targetId,button){
  activeButton=button||document.getElementById('aiChatMic')||document.querySelector('.sv-global-compose .mic');
  const i=document.getElementById(targetId||'aiChatInput');
  if(recording){try{mediaRecorder?.stop()}catch(_){releaseStream()}return}
  if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){voiceConversation=false;if(i)i.placeholder='Voice input is unavailable on this browser — please type your message.';return}
  try{
    stopSpeech();enableVoiceConversation();
    mediaStream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true}});
    recordChunks=[];let opts={};
    for(const mt of ['audio/webm;codecs=opus','audio/mp4','audio/webm','audio/ogg;codecs=opus']){try{if(MediaRecorder.isTypeSupported?.(mt)){opts={mimeType:mt};break}}catch(_){} }
    mediaRecorder=new MediaRecorder(mediaStream,opts);recording=true;
    mediaRecorder.ondataavailable=e=>{if(e.data?.size)recordChunks.push(e.data)};
    mediaRecorder.onerror=()=>{if(i)i.placeholder='Microphone recording failed — please type your message.';voiceConversation=false;releaseStream()};
    mediaRecorder.onstop=async()=>{
      const chunks=[...recordChunks],type=mediaRecorder?.mimeType||chunks[0]?.type||'audio/webm';
      if(recordTimer){clearTimeout(recordTimer);recordTimer=null}stopAudioMonitor();
      try{mediaStream?.getTracks?.().forEach(x=>x.stop())}catch(_){}mediaStream=null;mediaRecorder=null;recording=false;recordChunks=[];setMic(false);
      if(!chunks.length){voiceConversation=false;if(i)i.placeholder='No speech recorded — tap the microphone and try again.';return}
      try{
        if(i)i.placeholder='Transcribing your voice…';
        const blob=new Blob(chunks,{type}),audio=await blobDataURL(blob);
        const res=await fetch(apiBase()+'/api/transcribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({audio,language:selectedLang()||'auto'})});
        const d=await res.json().catch(()=>({}));if(!res.ok||!d.text)throw Error(d.error||'transcription failed');
        if(i){i.value=String(d.text).trim();i.placeholder='Message SEEKVERA AI…';if(i.value)setTimeout(()=>i.form?.requestSubmit?.(),80)}
      }catch(e){voiceConversation=false;if(i)i.placeholder='Voice could not be transcribed — please type or try again.'}
    };
    mediaRecorder.start(250);setMic(true);if(i)i.placeholder='Listening… I will send after you finish speaking';
    startAudioMonitor(mediaStream,()=>{if(recording&&mediaRecorder?.state==='recording')mediaRecorder.stop()});
    recordTimer=setTimeout(()=>{if(recording&&mediaRecorder?.state==='recording')mediaRecorder.stop()},VOICE_MAX_MS);
  }catch(e){voiceConversation=false;releaseStream();if(i)i.placeholder=e?.name==='NotAllowedError'?'Microphone permission was not allowed — please enable it or type your message.':'Microphone is unavailable — please type your message.'}
}

function start(targetId,button){
  if(recording){try{mediaRecorder?.stop()}catch(_){releaseStream()}return}
  if(recognition){try{recognition.stop()}catch(_){}return}
  stopSpeech();enableVoiceConversation();clearSpeechTimers();
  activeButton=button||document.getElementById('aiChatMic')||document.querySelector('.sv-global-compose .mic');
  const i=document.getElementById(targetId||'aiChatInput');
  if(!SpeechRecognition||/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)){serverVoice(targetId,activeButton);return}
  const r=new SpeechRecognition();recognition=r;r.lang=locale();r.interimResults=true;r.continuous=true;r.maxAlternatives=1;
  let final='',hadError=false,heardAny=false;
  const scheduleSilence=()=>{if(speechSilenceTimer)clearTimeout(speechSilenceTimer);speechSilenceTimer=setTimeout(()=>{try{if(recognition===r)r.stop()}catch(_){}},VOICE_SILENCE_MS)};
  r.onstart=()=>{setMic(true);speechHardTimer=setTimeout(()=>{try{if(recognition===r)r.stop()}catch(_){}},VOICE_MAX_MS)};
  r.onresult=e=>{let interim='';heardAny=true;for(let x=e.resultIndex;x<e.results.length;x++){const t=e.results[x][0].transcript;if(e.results[x].isFinal)final+=(final?' ':'')+t;else interim+=t}if(i)i.value=(final+(interim?((final?' ':'')+interim):'')).trim();scheduleSilence()};
  r.onerror=e=>{if(!['no-speech','aborted'].includes(e?.error))hadError=true;if(e?.error==='no-speech'&&!heardAny)voiceConversation=false};
  r.onend=()=>{clearSpeechTimers();setMic(false);if(recognition===r)recognition=null;const q=i?.value?.trim();if(q&&!hadError)setTimeout(()=>i.form?.requestSubmit?.(),90);else if(!q)voiceConversation=false};
  try{r.start()}catch(_){recognition=null;voiceConversation=false;clearSpeechTimers();setMic(false);serverVoice(targetId,activeButton)}
}
function toggleMute(btn){muted=!muted;voiceConversation=false;localStorage.setItem('seekvera_voice_muted',muted?'1':'0');updateSpeakerButtons();if(muted)stopSpeech();else{unlockTTS();if(lastAnswer)speak(lastAnswer,lastLocale,true)}if(btn)btn.textContent=muted?'🔇':'🔊'}
window.addEventListener('seekvera:voice',e=>start(e.detail?.targetId,e.detail?.button));
window.addEventListener('seekvera:ai-response',e=>speak(e.detail?.text,e.detail?.language,voiceConversation));
document.addEventListener('click',e=>{const mic=e.target.closest('#aiChatMic,.sv-global-compose .mic');if(mic){e.preventDefault();const input=mic.closest('form')?.querySelector('input[type="text"],input:not([type])');start(input?.id,mic)}const sp=e.target.closest('#aiChatSpeaker,.sv-global-speaker');if(sp){e.preventDefault();toggleMute(sp)}});
if(window.speechSynthesis){try{speechSynthesis.addEventListener?.('voiceschanged',()=>voices())}catch(_){}}
document.addEventListener('DOMContentLoaded',updateSpeakerButtons,{once:true});
})();