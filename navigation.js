/* SEEKVERA universal navigation + worldwide AI stability R16 */
(()=>{'use strict';
const HOME_PATHS=new Set(['/','/index.html','/app.html']);
const RTL=new Set(['ar','fa','ur','he','ps','dv']);
const WORLD_LANGS=['en','ar','fr','zh','es','hi','pt','de','ja','ko','id','tr','ru','ur','bn','vi','it','sw','th','fa','pl','nl','ms','fil','ha','yo','ig','am','he','el','uk','ro','cs','sk','hu','sv','no','da','fi','bg','hr','sr','sl','lt','lv','et','ca','eu','gl','is','sq','mk','ka','hy','az','kk','uz','ky','tg','tk','ne','si','ta','te','ml','mr','gu','pa','km','lo','my','mn','zu','af','be','bs','dz','ti','fo','kl','rw','sm','to','so','ps','dv','mt','mg','ga','cy','mi','fy','lb','rm','ku','xh','st','tn'];
const CMD_LOCALES=['en','ar','fr','es','de','pt','tr','ru','it','nl','hi','ur'];
const STATIC_AI_SOURCE="I’m the SEEKVERA AI assistant. Tell me what you need and I’ll help you find the right section, compare options or search worldwide.";
let localeTimer=0,translateSeq=0;
const localeControl=id=>document.querySelector(`.sv-controls select#${id},select#${id}.sv-select`);

const sameOriginReferrer=()=>{try{return document.referrer&&new URL(document.referrer).origin===location.origin}catch{return false}};
function goHome(){location.href='index.html'}
function goBack(){
  if(sameOriginReferrer()&&history.length>1){history.back();return;}
  const last=sessionStorage.getItem('seekvera_last_internal_page');
  if(last&&last!==location.pathname+location.search+location.hash){location.href=last;return;}
  goHome();
}
function rememberInternalLinks(){
  document.addEventListener('click',e=>{
    const a=e.target.closest?.('a[href]');if(!a)return;
    try{const u=new URL(a.href,location.href);if(u.origin===location.origin){sessionStorage.setItem('seekvera_last_internal_page',location.pathname+location.search+location.hash)}}catch{}
  },true);
}
function buildNav(){
  rememberInternalLinks();
  if(HOME_PATHS.has(location.pathname))return;
  if(document.getElementById('svUniversalNav'))return;
  const st=document.createElement('style');st.id='svUniversalNavStyles';st.textContent=`
#svUniversalNav{position:fixed;z-index:2147483000;top:calc(env(safe-area-inset-top,0px) + 10px);inset-inline-start:10px;display:flex;gap:8px;align-items:center;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
#svUniversalNav button,#svUniversalNav a{appearance:none;border:1px solid rgba(15,23,42,.16);background:rgba(255,255,255,.96);color:#0f172a;min-height:42px;padding:0 13px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;gap:7px;font:700 14px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;text-decoration:none;box-shadow:0 8px 24px rgba(15,23,42,.14);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);cursor:pointer}
#svUniversalNav button:active,#svUniversalNav a:active{transform:scale(.97)}
#svUniversalNav .sv-nav-icon{font-size:20px;line-height:1}
@media(max-width:640px){#svUniversalNav{top:calc(env(safe-area-inset-top,0px) + 7px);inset-inline-start:7px;gap:6px}#svUniversalNav button,#svUniversalNav a{min-height:40px;padding:0 10px;font-size:12px}.sv-nav-label{display:none}#svUniversalNav .sv-nav-icon{font-size:21px}}
@media(prefers-color-scheme:dark){#svUniversalNav button,#svUniversalNav a{background:rgba(15,23,42,.94);color:#fff;border-color:rgba(255,255,255,.18)}}`;
  document.head.appendChild(st);
  const nav=document.createElement('nav');nav.id='svUniversalNav';nav.setAttribute('aria-label','Page navigation');
  nav.innerHTML=`<button type="button" id="svBackButton" aria-label="Back"><span class="sv-nav-icon" aria-hidden="true">←</span><span class="sv-nav-label">Back</span></button><a href="index.html" id="svHomeButton" aria-label="Home"><span class="sv-nav-icon" aria-hidden="true">⌂</span><span class="sv-nav-label">Home</span></a>`;
  document.body.appendChild(nav);
  document.getElementById('svBackButton')?.addEventListener('click',goBack);
}

function langCode(){
  let v=localeControl('lang')?.value||localStorage.getItem('seekvera_lang')||document.documentElement.lang||navigator.language||'en';
  if(v==='auto')v=navigator.language||'en';
  return String(v).toLowerCase().split(/[-_]/)[0]||'en';
}
function displayLanguage(code,display=langCode()){
  try{return new Intl.DisplayNames([display],{type:'language'}).of(code)||code.toUpperCase()}catch{return code.toUpperCase()}
}
function displayRegion(code,display=langCode()){
  try{return new Intl.DisplayNames([display],{type:'region'}).of(code)||code}catch{return code}
}
function ensureLanguageCoverage(){
  const el=localeControl('lang');if(!el)return;
  const selected=el.value||localStorage.getItem('seekvera_lang')||'auto';
  if(![...el.options].some(o=>o.value==='auto'))el.insertBefore(new Option('⚙️','auto'),el.firstChild);
  for(const code of WORLD_LANGS){if(![...el.options].some(o=>o.value===code))el.add(new Option(code.toUpperCase(),code));}
  const d=langCode();
  for(const o of el.options){
    if(o.value==='auto'){
      const device=String(navigator.language||'en').split(/[-_]/)[0];
      o.textContent='⚙️ '+displayLanguage(device,d);
    }else if(/^[a-z]{2,3}$/i.test(o.value))o.textContent=displayLanguage(o.value,d);
  }
  if([...el.options].some(o=>o.value===selected))el.value=selected;
}
function localizeCountryOptions(){
  const el=localeControl('country');if(!el)return;
  const d=langCode();
  for(const o of el.options){
    const code=String(o.value||'').toUpperCase();
    if(code==='WW')o.textContent='🌐 '+(window.SEEKVERA_LOCALE_R14?.t?.('worldwide')||'Worldwide');
    else if(/^[A-Z]{2}$/.test(code))o.textContent=displayRegion(code,d);
  }
}
function localizeDocumentDirection(){
  const l=langCode();document.documentElement.lang=l;document.documentElement.dir=RTL.has(l)?'rtl':'ltr';
}
async function translateStaticAI(){
  const box=document.querySelector('#aiMessages .ai-msg.bot:first-child');if(!box)return;
  const l=langCode();
  if(!box.dataset.svSource)box.dataset.svSource=(box.textContent||STATIC_AI_SOURCE).trim();
  const source=box.dataset.svSource||STATIC_AI_SOURCE;
  if(l==='en'){box.textContent=source;box.dataset.svLang='en';return;}
  if(box.dataset.svLang===l)return;
  const key='sv_static_ai_'+l+'_'+source;
  let cached='';try{cached=localStorage.getItem(key)||sessionStorage.getItem(key)||''}catch{}if(cached){box.textContent=cached;box.dataset.svLang=l;return;}
  const mine=++translateSeq;
  try{
    const language=displayLanguage(l,'en');
    const r=await fetch('/api/ui-translate',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language,strings:[source]})});
    const d=await r.json().catch(()=>null);const t=String(d?.translations?.[0]||'').trim();
    if(r.ok&&t&&mine===translateSeq){try{localStorage.setItem(key,t)}catch{}box.textContent=t;box.dataset.svLang=l;}
  }catch{}
}
function runLocaleEngines(){
  try{window.SEEKVERA_I18N?.apply?.()}catch{}
  try{window.SEEKVERA_LOCALE_GUARD_R9?.apply?.()}catch{}
  ensureLanguageCoverage();localizeCountryOptions();localizeDocumentDirection();
  translateStaticAI();
  hardenAIUI();
}
function scheduleLocalePass(){clearTimeout(localeTimer);localeTimer=setTimeout(runLocaleEngines,50)}
function stripDuplicateDepartments(){
  if(!HOME_PATHS.has(location.pathname))return;
  document.querySelector('.r8-department-strip')?.remove();
  document.querySelector('.r5-left')?.remove();
  if(document.getElementById('svR10HomeCleanup'))return;
  const st=document.createElement('style');st.id='svR10HomeCleanup';st.textContent='@media(min-width:980px){body.sv-home-global .r5-market,.r5-market{grid-template-columns:minmax(0,1fr) 240px!important}}';document.head.appendChild(st);
}

function ensureAIStableStyles(){
  if(document.getElementById('svR16AIStableStyles'))return;
  const st=document.createElement('style');st.id='svR16AIStableStyles';st.textContent=`
#aiChat,.sv-unified-chat{max-width:100%!important;min-width:0!important;overflow:hidden!important;contain:layout!important}
#aiChat *, .sv-unified-chat *{box-sizing:border-box}
#aiChat .sv-chat-head,.sv-unified-chat .sv-chat-head{display:grid!important;grid-template-columns:minmax(0,1fr) auto 48px!important;align-items:center!important;gap:8px!important;min-width:0!important}
#aiChat .sv-chat-head>div,.sv-unified-chat .sv-chat-head>div{min-width:0!important;overflow:hidden!important}
#aiChat .sv-chat-head b,.sv-unified-chat .sv-chat-head b{display:block!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}
#aiChat .sv-chat-head small,.sv-unified-chat .sv-chat-head small{display:block!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;max-width:100%!important}
#aiChat .sv-chat-head>span,.sv-unified-chat .sv-chat-head>span{white-space:nowrap!important;min-width:0!important}
#aiChatSpeaker,.sv-global-speaker{width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important;min-height:48px!important;padding:0!important;overflow:hidden!important;white-space:nowrap!important;font-size:0!important;line-height:1!important;display:inline-flex!important;align-items:center!important;justify-content:center!important}
#aiChatSpeaker::before,.sv-global-speaker::before{content:'🔊';font-size:22px!important;line-height:1!important}
#aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{height:220px!important;min-height:220px!important;max-height:220px!important;overflow-y:auto!important;overflow-x:hidden!important;scroll-behavior:smooth!important;overscroll-behavior:auto!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important;overflow-anchor:none!important}
#aiChat .ai-msg,.sv-unified-chat .ai-msg{max-width:min(92%,560px)!important;min-width:0!important;overflow-wrap:anywhere!important;word-break:normal!important;white-space:pre-wrap!important}
#aiChat .sv-chat-form,.sv-unified-chat .sv-chat-form{display:grid!important;grid-template-columns:44px minmax(0,1fr) 44px 44px 50px!important;gap:7px!important;align-items:center!important;min-width:0!important;width:100%!important}
#aiChat .sv-chat-form input,.sv-unified-chat .sv-chat-form input{min-width:0!important;width:100%!important;max-width:100%!important;direction:auto!important;text-align:start!important}
#aiChatAttach,#aiChatCamera,#aiChatMic,#aiChat .sv-chat-form .send,.sv-unified-chat .sv-chat-form .attach,.sv-unified-chat .sv-chat-form .camera,.sv-unified-chat .sv-chat-form .mic,.sv-unified-chat .sv-chat-form .send{width:44px!important;min-width:44px!important;max-width:44px!important;height:44px!important;min-height:44px!important;padding:0!important;overflow:hidden!important;white-space:nowrap!important;font-size:0!important;line-height:1!important;display:inline-flex!important;align-items:center!important;justify-content:center!important}
#aiChat .sv-chat-form .send,.sv-unified-chat .sv-chat-form .send{width:50px!important;min-width:50px!important;max-width:50px!important}
#aiChatAttach::before,.sv-unified-chat .sv-chat-form .attach::before{content:'📎';font-size:20px!important}
#aiChatCamera::before,.sv-unified-chat .sv-chat-form .camera::before{content:'📷';font-size:20px!important}
#aiChatMic::before,.sv-unified-chat .sv-chat-form .mic::before{content:'🎤';font-size:20px!important}
#aiChat .sv-chat-form .send::before,.sv-unified-chat .sv-chat-form .send::before{content:'➤';font-size:22px!important}
#aiActions,.sv-ai-actions{display:flex!important;position:static!important;clear:both!important;flex-wrap:wrap!important;gap:8px!important;align-items:center!important;min-width:0!important;max-width:100%!important;padding:8px 12px 12px!important;overflow:visible!important}
#aiActions>* ,.sv-ai-actions>*{max-width:100%!important;min-width:0!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important}
#aiChat,#aiChat *,.sv-unified-chat,.sv-unified-chat *{animation:none!important}
html.sv-r15-applying #aiChat,html.sv-r15-applying #aiChat *{transition:none!important}
@media(max-width:600px){
 #aiChat .sv-chat-head,.sv-unified-chat .sv-chat-head{grid-template-columns:minmax(0,1fr) auto 44px!important;padding:10px!important;gap:6px!important}
 #aiChatSpeaker,.sv-global-speaker{width:44px!important;min-width:44px!important;max-width:44px!important;height:44px!important;min-height:44px!important}
 #aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{height:230px!important;min-height:230px!important;max-height:230px!important;padding:10px!important}
 #aiChat .sv-chat-form,.sv-unified-chat .sv-chat-form{grid-template-columns:minmax(0,1fr) 42px 42px 48px!important;gap:6px!important;padding:8px!important}
 #aiChatAttach,.sv-unified-chat .sv-chat-form .attach{display:none!important}
 #aiChatCamera,#aiChatMic,.sv-unified-chat .sv-chat-form .camera,.sv-unified-chat .sv-chat-form .mic{width:42px!important;min-width:42px!important;max-width:42px!important;height:42px!important;min-height:42px!important}
 #aiChat .sv-chat-form .send,.sv-unified-chat .sv-chat-form .send{width:48px!important;min-width:48px!important;max-width:48px!important;height:42px!important;min-height:42px!important}
 #aiChat .sv-chat-head small,.sv-unified-chat .sv-chat-head small{font-size:9px!important}
 #aiChat .sv-chat-head>span,.sv-unified-chat .sv-chat-head>span{font-size:10px!important}
}
@media(max-width:370px){
 #aiChat .sv-chat-head,.sv-unified-chat .sv-chat-head{grid-template-columns:minmax(0,1fr) 42px!important}
 #aiChat .sv-chat-head>span,.sv-unified-chat .sv-chat-head>span{display:none!important}
}
`;
  document.head.appendChild(st);
}
function fixAIControlButtons(){
  const defs=[['aiChatAttach','📎'],['aiChatCamera','📷'],['aiChatMic','🎤']];
  for(const [id,emoji] of defs){const b=document.getElementById(id);if(!b)continue;b.setAttribute('data-no-i18n','1');b.setAttribute('data-no-translate','1');if((b.textContent||'').trim()!==emoji)b.textContent=emoji;}
  const sp=document.getElementById('aiChatSpeaker');if(sp){sp.setAttribute('data-no-i18n','1');sp.setAttribute('data-no-translate','1');if(!/[🔊🔈🔇]/u.test(sp.textContent||''))sp.textContent='🔊';}
  const send=document.querySelector('#aiChatForm .send,#aiChat .sv-chat-form .send');if(send){send.setAttribute('data-no-i18n','1');send.setAttribute('data-no-translate','1');if((send.textContent||'').trim()!=='➤')send.textContent='➤';}
  const brand=document.querySelector('#aiChat .sv-chat-head b');if(brand){brand.setAttribute('data-no-i18n','1');brand.setAttribute('data-no-translate','1');if(!/SEEKVERA\s+AI/i.test(brand.textContent||''))brand.textContent='✨ SEEKVERA AI';}
  const input=document.getElementById('aiChatInput');if(input){input.setAttribute('dir','auto');input.style.minWidth='0';}
}
function hardenAIUI(){
  ensureAIStableStyles();fixAIControlButtons();
  const chat=document.getElementById('aiChat');if(!chat||chat.dataset.r16Observed==='1')return;
  chat.dataset.r16Observed='1';
  const mo=new MutationObserver(ms=>{for(const m of ms){const t=m.target?.nodeType===1?m.target:m.target?.parentElement;if(t?.closest?.('#aiChatSpeaker,#aiChatAttach,#aiChatCamera,#aiChatMic,#aiChatForm .send,#aiChat .sv-chat-head b')){queueMicrotask(fixAIControlButtons);break}}});
  mo.observe(chat,{subtree:true,childList:true,characterData:true});
}

function normalizeText(s){return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[’'`´]/g,'').replace(/[^\p{L}\p{N}]+/gu,' ').trim()}
const COUNTRY_TERMS='country|region|دولة|الدولة|بلد|البلد|منطقة|pays|région|国家|地区|país|región|देश|क्षेत्र|região|land|国|地域|국가|지역|negara|wilayah|ülke|bölge|страна|регион|ملک|علاقہ|দেশ|অঞ্চল|quốc gia|khu vực|paese|regione|nchi|eneo|ประเทศ|ภูมิภาค|کشور|منطقه|kraj|regio|bansa|rehiyon|ƙasa|yanki|orilẹ-ede|agbegbe|obodo|mpaghara|ሀገር|ክልል|מדינה|אזור|χώρα|περιοχή|країна|регіон|țară|regiune|země|krajina|régión|ország|régió|maa|alue|държава|država|regija|šalis|regionas|valsts|reģions|riik|piirkond|regió|herrialde|eskualde|rexión|svæði|vend|rajon|земја|ქვეყანა|რეგიონი|երկիր|տարածաշրջան|ölkə|ел|аймақ|mamlakat|hudud|өлкө|аймак|кишвар|минтақа|ýurt|sebit|රට|කලාපය|நாடு|பகுதி|దేశం|ప్రాంతం|രാജ്യം|പ്രദേശം|प्रदेश|દેશ|ਪ੍ਰਦੇਸ਼|ਦੇਸ਼|ਖੇਤਰ|ប្រទេស|តំបន់|ປະເທດ|ພາກພື້ນ|နိုင်ငံ|ဒေသ|улс|бүс|izwe|isifunda|streek|краіна|рэгіён|ሃገር|øki|nuna|igihugu|akarere|atunuu|itulagi|fonua|dal|gobol|هېواد|سیمه|ޤައުމު|ސަރަހައްދު|pajji|reġjun|firenena|faritra|tír|réigiún|gwlad|rhanbarth|whenua|rohe|lân|regioun|pajais|regiun|welat|herêm|ilizwe|ummandla|naha|sebaka|naga|kgaolo'.split('|').map(normalizeText).filter(Boolean);
function hasCountryTerm(text){const s=normalizeText(text),pad=' '+s+' ';return COUNTRY_TERMS.some(t=>/^[a-z0-9\- ]+$/i.test(t)?pad.includes(' '+t+' '):s.includes(t))}
function isCountryCommand(text,code=''){
  const raw=String(text||''),s=normalizeText(raw);
  let direct=false;
  if(code){
    const names=countryNames(code);
    const latin=/\b(?:set|switch|change|choose|select|go|move|use|open|control|app|market|country|region|take|put)\b/.test(s);
    const native=/(?:حط|حطلي|اختار|اختر|غير|غيرلي|حول|حوللي|انتقل|اذهب|استخدم|غيّر|حوّل|बदल|चुन|जाओ|देश|ऐप|परिवर्तन|ملک|بدل|منتخب|смени|сменить|выбери|установи|cambia|elige|selecciona|change|choisis|wechsle|wähle|mudar|trocar|seç|degistir|imposta|scegli)/u.test(raw);
    const short=s.split(/\s+/).filter(Boolean).length<=3;
    const hasTarget=names.some(n=>n.length>=2&&(s===n||(' '+s+' ').includes(' '+n+' ')||((latin||native)&&s.includes(n))));
    direct=hasTarget&&(latin||native||short);
  }
  return direct
    || /\b(?:set|switch|change|choose|select)\b.{0,35}\b(?:country|region)\b/.test(s)
    || /(?:حط|حطلي|اختار|اختر|غير|غيرلي|حول|حوللي).{0,30}(?:الدولة|دولة|البلد|بلد)/u.test(raw)
    || /\b(?:mets?|change|passe|choisis?)\b.{0,35}\b(?:pays|region)\b/.test(s)
    || /\b(?:cambia|cambiar|pon|elige|selecciona)\b.{0,35}\b(?:pais|region)\b/.test(s)
    || /\b(?:ander|wechsle|wahle|setze)\b.{0,35}\b(?:land|region)\b/.test(s)
    || /\b(?:mudar|muda|trocar|troca|escolher|escolha)\b.{0,35}\b(?:pais|regiao)\b/.test(s)
    || /\b(?:degistir|sec|seç)\b.{0,35}\b(?:ulke|ülke|bolge|bölge)\b/.test(s)
    || /(?:смени|сменить|выбери|выбрать|установи).{0,35}(?:стран|регион)/u.test(raw)
    || /\b(?:cambia|imposta|scegli)\b.{0,35}\b(?:paese|regione)\b/.test(s)
    || /(?:ملک|ملک کو|ملک بدل).{0,30}(?:بدل|منتخب|چن)/u.test(raw)
    || hasCountryTerm(text);
}
const COUNTRY_COMMAND_ALIASES={LB:['lebanese','libanese','libanais','libanaise','لبناني','لبنانية','لبنانيه','लेबनानी']};
function countryNames(code){
  const out=new Set([code,...(COUNTRY_COMMAND_ALIASES[code]||[])]);
  const current=langCode();
  for(const l of [current,...CMD_LOCALES]){try{const n=new Intl.DisplayNames([l],{type:'region'}).of(code);if(n)out.add(n)}catch{}}
  return [...out].map(x=>normalizeText(x)).filter(Boolean).sort((a,b)=>b.length-a.length);
}
function resolveCountry(text){
  const el=localeControl('country');if(!el)return null;
  const s=normalizeText(text);const hits=[];
  for(const o of el.options){const code=String(o.value||'').toUpperCase();if(!/^[A-Z]{2}$/.test(code))continue;for(const n of countryNames(code)){if(n.length>=3&&s.includes(n)){hits.push({code,n});break}}}
  hits.sort((a,b)=>b.n.length-a.n.length);return hits[0]?.code||null;
}
function addCountryConfirmation(code){
  const name=displayRegion(code,langCode());
  const box=document.getElementById('aiMessages');if(box){const m=document.createElement('div');m.className='ai-msg bot';m.dataset.noTranslate='1';m.dataset.noI18n='1';m.textContent='🌍 '+name+' ✓';box.appendChild(m);box.scrollTop=box.scrollHeight;}
  try{window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:name,language:langCode()}}))}catch{}
}
function bindAICountryControl(){
  document.addEventListener('submit',e=>{
    const form=e.target;if(!(form instanceof HTMLFormElement))return;
    if(!(form.id==='aiChatForm'||form.classList.contains('sv-global-compose')||form.closest('#aiChat')))return;
    const input=form.querySelector('#aiChatInput,input[type="text"],input:not([type])');const text=input?.value?.trim()||'';
    if(!text)return;
    const code=resolveCountry(text);if(!code||!isCountryCommand(text,code))return;
    e.preventDefault();e.stopImmediatePropagation();
    const c=localeControl('country');
    if(window.SEEKVERA_LOCALE_R15)window.SEEKVERA_LOCALE_R15.setCountry(code);
    else {if(!c)return;c.value=code;c.dispatchEvent(new Event('input',{bubbles:true}));c.dispatchEvent(new Event('change',{bubbles:true}));}
    if(input)input.value='';
    setTimeout(()=>{scheduleLocalePass();addCountryConfirmation(code)},180);
  },true);
}
function primeVoiceOnGesture(e){
  if(!e.target.closest?.('#aiChatMic,#aiChatSpeaker,.sv-global-compose .mic,.sv-global-speaker'))return;
  try{
    const s=window.speechSynthesis;if(!s||!window.SpeechSynthesisUtterance)return;
    s.getVoices?.();s.resume?.();
    if(!s.speaking){const u=new SpeechSynthesisUtterance(' ');u.volume=0;u.rate=1;s.speak(u);}
  }catch{}
}
function bindLocaleControls(){
  document.addEventListener('change',e=>{const t=e.target;if(t&&(t===localeControl('country')||t===localeControl('lang'))){if(t===localeControl('lang'))localStorage.setItem('seekvera_lang',t.value);queueMicrotask(runLocaleEngines);scheduleLocalePass()}},true);
  window.addEventListener('pageshow',scheduleLocalePass);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)scheduleLocalePass()});
  document.addEventListener('pointerdown',primeVoiceOnGesture,true);
  document.addEventListener('touchstart',primeVoiceOnGesture,{capture:true,passive:true});
  if(window.speechSynthesis){try{speechSynthesis.addEventListener?.('voiceschanged',()=>speechSynthesis.getVoices?.())}catch{}}
}
function init(){stripDuplicateDepartments();buildNav();hardenAIUI();bindLocaleControls();bindAICountryControl();scheduleLocalePass()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
