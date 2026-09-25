(()=>{'use strict';
if(window.__SEEKVERA_R31)return;window.__SEEKVERA_R31=true;
const VERSION='20260925-r31b';
const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
const ROUTES={travel:'travel.html',property:'property.html',cars:'cars-auto.html',jobs:'jobs.html',shopping:'shopping.html',business:'import-export.html',health:'health.html',restaurants:'restaurants-food.html',connectivity:'connectivity.html',media:'media.html',general:'marketplace.html'};
const ICONS=[[/marketplace/,'🛒'],[/travel\.html(?!\?q=)/,'✈️'],[/flights/,'🛫'],[/hotels/,'🏨'],[/tourism/,'🗺️'],[/property/,'🏠'],[/cars-auto/,'🚘'],[/jobs/,'💼'],[/shopping/,'🛍️'],[/restaurants-food/,'🍽️'],[/local-services/,'🧰'],[/equipment/,'🏗️'],[/boats/,'⛵'],[/import-export/,'🚢'],[/shipping-logistics/,'📦'],[/business-software/,'💻'],[/software/,'🧩'],[/web-hosting/,'🌐'],[/solar/,'☀️'],[/education/,'🎓'],[/health/,'🏥'],[/money-insurance/,'💳'],[/entertainment/,'🎬'],[/media/,'📰'],[/games/,'🎮'],[/connectivity/,'📶'],[/wifi/,'📡'],[/deal-agent/,'🤝'],[/everyday/,'📍'],[/scan/,'📲'],[/seller-plans/,'🚀']];
const LOCALES={ar:'ar-SA',en:'en-US',fr:'fr-FR',zh:'zh-CN',es:'es-ES',hi:'hi-IN',pt:'pt-PT',de:'de-DE',ja:'ja-JP',ko:'ko-KR',id:'id-ID',tr:'tr-TR',ru:'ru-RU',ur:'ur-PK',bn:'bn-BD',vi:'vi-VN',it:'it-IT',sw:'sw-KE',th:'th-TH',fa:'fa-IR',pl:'pl-PL',nl:'nl-NL',ms:'ms-MY',fil:'fil-PH',ha:'ha-NG',yo:'yo-NG',ig:'ig-NG',am:'am-ET',he:'he-IL'};
const RTL=new Set(['ar','fa','ur','he','ps','dv']);
const FALLBACK_CURRENCY_AR={USD:'دولار أمريكي',EUR:'يورو',GBP:'جنيه إسترليني',LBP:'ليرة لبنانية',SYP:'ليرة سورية',SAR:'ريال سعودي',AED:'درهم إماراتي',NGN:'نايرا نيجيرية',EGP:'جنيه مصري',TRY:'ليرة تركية',CNY:'يوان صيني',JPY:'ين ياباني',KRW:'وون كوري جنوبي',INR:'روبية هندية',CAD:'دولار كندي',AUD:'دولار أسترالي',CHF:'فرنك سويسري',JOD:'دينار أردني',IQD:'دينار عراقي',KWD:'دينار كويتي',QAR:'ريال قطري',BHD:'دينار بحريني',OMR:'ريال عماني',MAD:'درهم مغربي',DZD:'دينار جزائري',TND:'دينار تونسي',LYD:'دينار ليبي'};
let switching=0,recognition=null,voiceTurn=false,voiceSeq=0,submitting=false,observerTimer=0;
function lang(){return String(document.querySelector('#lang')?.value||document.documentElement.lang||localStorage.getItem('seekvera_lang')||'en').toLowerCase().split(/[-_]/)[0]||'en'}
function locale(){const l=lang();return LOCALES[l]||l||navigator.language||'en-US'}
function country(){return String(document.querySelector('#country')?.value||localStorage.getItem('seekvera_country')||'WW').toUpperCase()}
function countryName(){const e=document.querySelector('#country');return e?.options?.[e.selectedIndex]?.textContent||'Worldwide'}
function currencyLabel(code,l=lang()){
 code=String(code||'').toUpperCase();if(!code)return'';
 if(l==='ar'&&FALLBACK_CURRENCY_AR[code])return FALLBACK_CURRENCY_AR[code];
 try{const x=new Intl.DisplayNames([l],{type:'currency'}).of(code);if(x&&x!==code)return x}catch{}
 try{const x=new Intl.DisplayNames([navigator.language||'en'],{type:'currency'}).of(code);if(x&&x!==code)return x}catch{}
 return code;
}
function localizeCurrencies(){
 const el=document.querySelector('#currency');if(!el)return;
 const profiles=window.SEEKVERA_LOCALE_R15?.profiles||{};const codes=new Set([...el.options].map(o=>String(o.value||o.textContent||'').trim().toUpperCase()).filter(x=>/^[A-Z]{3}$/.test(x)));
 Object.values(profiles).forEach(p=>{if(p?.currency)codes.add(String(p.currency).toUpperCase())});
 for(const code of [...codes].sort()){
  let o=[...el.options].find(x=>String(x.value||'').toUpperCase()===code);if(!o){o=document.createElement('option');o.value=code;el.appendChild(o)}const label=currencyLabel(code);if(o.textContent!==label)o.textContent=label;
 }
 const p=profiles[country()];if(p?.currency&&[...el.options].some(o=>o.value===p.currency)&&el.value!==p.currency)el.value=p.currency;
 const aria=lang()==='ar'?'العملة':'Currency';if(el.getAttribute('aria-label')!==aria)el.setAttribute('aria-label',aria);
}
function repairCategoryIcons(){
 document.querySelectorAll('.r5-tile').forEach(a=>{const box=a.querySelector('.r5-thumb');if(!box)return;const key=(a.getAttribute('href')||'')+' '+(a.querySelector('b')?.textContent||'');let icon='';for(const [re,v] of ICONS){if(re.test(key)){icon=v;break}}if(icon&&box.textContent.trim()!==icon)box.textContent=icon;if(box.getAttribute('aria-hidden')!=='true')box.setAttribute('aria-hidden','true')});
}
function markDirection(){const l=lang();if(document.documentElement.lang!==l)document.documentElement.lang=l;const d=RTL.has(l)?'rtl':'ltr';if(document.documentElement.dir!==d)document.documentElement.dir=d}
async function atomicLocale(){
 const my=++switching;document.documentElement.classList.add('sv-r31-switching');markDirection();localizeCurrencies();repairCategoryIcons();
 try{window.SEEKVERA_I18N?.apply?.()}catch{}try{window.SEEKVERA_R14_CATEGORIES?.apply?.()}catch{}try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)}catch{}try{await Promise.resolve(window.SEEKVERA_LOCALE_GUARD_R9?.apply?.())}catch{}
 localizeCurrencies();repairCategoryIcons();if(my===switching)document.documentElement.classList.remove('sv-r31-switching');
 setTimeout(()=>{if(my===switching){try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)}catch{}localizeCurrencies();repairCategoryIcons();document.documentElement.classList.remove('sv-r31-switching')}},650);
}
function installAtomicCSS(){if(document.getElementById('sv-r31-css'))return;const s=document.createElement('style');s.id='sv-r31-css';s.textContent='.sv-r31-switching .r5-center,.sv-r31-switching .r5-left,.sv-r31-switching .r5-right{opacity:.12;transition:opacity .12s ease}.r5-center,.r5-left,.r5-right{transition:opacity .12s ease}.r5-thumb{overflow:hidden}.r5-thumb img{display:none!important}';document.head.appendChild(s)}
function resetMic(btn){if(!btn)return;btn.classList.remove('listening');btn.textContent='🎤';btn.setAttribute('aria-label',lang()==='ar'?'تحدث مع ذكاء SEEKVERA':'Speak to SEEKVERA AI')}
function cancelRecognition(discard=true){const r=recognition;recognition=null;if(r){try{discard?r.abort():r.stop()}catch{}}resetMic(document.querySelector('#aiChatMic'));if(discard)voiceTurn=false}
function speak(text){if(!voiceTurn||!window.speechSynthesis||!window.SpeechSynthesisUtterance)return;voiceTurn=false;try{speechSynthesis.cancel()}catch{}const clean=String(text||'').replace(/https?:\/\/\S+/g,' ').replace(/[*_#>`~|]/g,' ').replace(/\s+/g,' ').trim();if(!clean)return;const parts=clean.match(/[^.!?。！？؛]{1,130}(?:[.!?。！？؛]+|$)/g)||[clean.slice(0,130)];const token=++voiceSeq;const play=i=>{if(token!==voiceSeq||i>=parts.length)return;const u=new SpeechSynthesisUtterance(parts[i].trim());u.lang=locale();u.rate=1.04;u.pitch=1.02;u.onend=()=>setTimeout(()=>play(i+1),70);u.onerror=()=>setTimeout(()=>play(i+1),30);speechSynthesis.speak(u)};play(0)}
function appendMsg(role,text,extra=''){const box=document.querySelector('#aiMessages');if(!box)return null;const d=document.createElement('div');d.className='ai-msg '+role+(extra?' '+extra:'');d.textContent=text;box.appendChild(d);box.scrollTop=box.scrollHeight;return d}
function history(){return[...document.querySelectorAll('#aiMessages .ai-msg')].filter(x=>!x.classList.contains('thinking')).slice(-8).map(x=>({role:x.classList.contains('user')?'user':'assistant',content:String(x.textContent||'').trim().slice(0,1200)})).filter(x=>x.content)}
function thinkingText(){const l=lang();return l==='ar'?'لحظة…':l==='fr'?'Un instant…':l==='zh'?'请稍候…':l==='hi'?'एक क्षण…':'One moment…'}
function failText(){const l=lang();return l==='ar'?'تعذّر الاتصال للحظة. حاول مرة أخرى.':l==='fr'?'Connexion momentanément indisponible. Réessayez.':l==='zh'?'暂时无法连接，请重试。':l==='hi'?'अभी कनेक्ट नहीं हो सका। फिर कोशिश करें।':'Could not connect for a moment. Please try again.'}
async function fetchAI(payload){const urls=[location.origin+'/api/ai','https://seekvera-main.seekvera-global.workers.dev/api/ai'];let err='AI unavailable';for(const url of [...new Set(urls)]){const c=new AbortController(),t=setTimeout(()=>c.abort(),6500);try{const r=await fetch(url,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload),signal:c.signal});const d=await r.json().catch(()=>({}));clearTimeout(t);if(r.ok&&d?.response)return d;err=d?.error||('HTTP '+r.status)}catch(e){clearTimeout(t);err=e?.message||err}}throw Error(err)}
function showRoute(d,q){const box=document.querySelector('#aiActions');if(!box)return;box.innerHTML='';const route=d?.route||ROUTES[d?.category]||'';if(!route)return;const a=document.createElement('a');a.href=route+'?q='+encodeURIComponent(q);a.textContent=lang()==='ar'?'افتح القسم المناسب ←':'Open the right section →';box.appendChild(a)}
async function submitAI(q,{fromVoice=false}={}){
 q=String(q||'').trim().slice(0,1800);if(!q||submitting)return;submitting=true;voiceTurn=!!fromVoice;const input=document.querySelector('#aiChatInput');if(input)input.value='';appendMsg('user',q);const pending=appendMsg('bot',thinkingText(),'thinking');const h=history();
 try{const d=await fetchAI({message:q,country:countryName(),countryCode:country(),language:lang(),scope:country()==='WW'?'worldwide':'country',fast:true,history:h});if(pending){pending.textContent=d.response;pending.classList.remove('thinking')}const ans=document.querySelector('#aiAnswer');if(ans)ans.textContent=d.response;showRoute(d,q);window.dispatchEvent(new CustomEvent('seekvera:ai-response-r31',{detail:{text:d.response,language:d.language||lang()}}));if(fromVoice)speak(d.response)}catch(e){if(pending){pending.textContent=failText();pending.classList.remove('thinking')}voiceTurn=false}finally{submitting=false}
}
function startFastVoice(btn){
 const input=document.querySelector('#aiChatInput');if(!SpeechRecognition){return false}if(recognition){cancelRecognition(false);return true}try{speechSynthesis?.cancel?.()}catch{}const r=new SpeechRecognition();recognition=r;r.lang=locale();r.interimResults=true;r.continuous=false;r.maxAlternatives=1;let final='',heard=false,ended=false,stopTimer=0,hard=0;const finish=()=>{if(ended)return;ended=true;clearTimeout(stopTimer);clearTimeout(hard);resetMic(btn);if(recognition===r)recognition=null;const q=(final||input?.value||'').trim();if(q)submitAI(q,{fromVoice:true});else voiceTurn=false};const silence=()=>{clearTimeout(stopTimer);stopTimer=setTimeout(()=>{try{r.stop()}catch{}},900)};
 r.onstart=()=>{voiceTurn=true;btn.classList.add('listening');btn.textContent='■';btn.setAttribute('aria-label',lang()==='ar'?'إيقاف الاستماع':'Stop listening');if(input)input.placeholder=lang()==='ar'?'أسمعك…':'Listening…';hard=setTimeout(()=>{try{r.stop()}catch{}},12000)};
 r.onresult=e=>{heard=true;let interim='';for(let i=e.resultIndex;i<e.results.length;i++){const t=e.results[i][0].transcript;if(e.results[i].isFinal)final+=(final?' ':'')+t;else interim+=t}if(input)input.value=(final+(interim?((final?' ':'')+interim):'')).trim();silence()};
 r.onerror=e=>{if(['aborted'].includes(e?.error)){finish();return}if(!heard&&e?.error==='no-speech'){voiceTurn=false;finish();return}finish()};r.onend=finish;try{r.start();return true}catch{recognition=null;resetMic(btn);return false}
}
function bindChat(){
 document.addEventListener('click',e=>{const mic=e.target.closest?.('#aiChatMic');if(!mic)return;if(SpeechRecognition){e.preventDefault();e.stopImmediatePropagation();startFastVoice(mic)}},true);
 const input=document.querySelector('#aiChatInput');input?.addEventListener('input',()=>{if(recognition)cancelRecognition(true)});
 const form=document.querySelector('#aiChatForm');form?.addEventListener('submit',e=>{const q=input?.value?.trim();if(!q)return;const activeAttachment=document.querySelector('#aiAttachmentState:not([hidden])');if(activeAttachment&&activeAttachment.textContent?.trim())return;e.preventDefault();e.stopImmediatePropagation();if(recognition)cancelRecognition(true);submitAI(q,{fromVoice:false})},true);
}
function bindLocale(){document.addEventListener('change',e=>{if(e.target?.id==='country'||e.target?.id==='lang'||e.target?.id==='currency'){atomicLocale()}},true);new MutationObserver(ms=>{if(!ms.some(m=>m.type==='childList'))return;clearTimeout(observerTimer);observerTimer=setTimeout(()=>{repairCategoryIcons();localizeCurrencies()},90)}).observe(document.documentElement,{subtree:true,childList:true})}
function boot(){installAtomicCSS();repairCategoryIcons();localizeCurrencies();bindLocale();bindChat();atomicLocale();document.documentElement.dataset.r31=VERSION}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
window.SEEKVERA_R31={version:VERSION,refresh:atomicLocale,currencyLabel,repairCategoryIcons,cancelVoice:cancelRecognition,submitAI,startFastVoice,hasFastVoice:!!SpeechRecognition};
})();