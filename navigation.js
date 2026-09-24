/* SEEKVERA universal navigation + worldwide locale/voice hardening R12 */
(()=>{'use strict';
const HOME_PATHS=new Set(['/','/index.html','/app.html']);
const RTL=new Set(['ar','fa','ur','he','ps','dv']);
const WORLD_LANGS=['en','ar','fr','zh','es','hi','pt','de','ja','ko','id','tr','ru','ur','bn','vi','it','sw','th','fa','pl','nl','ms','fil','ha','yo','ig','am','he','el','uk','ro','cs','sk','hu','sv','no','da','fi','bg','hr','sr','sl','lt','lv','et','ca','eu','gl','is','sq','mk','ka','hy','az','kk','uz','ky','tg','tk','ne','si','ta','te','ml','mr','gu','pa','km','lo','my','mn','zu','af','be','bs','dz','ti','fo','kl','rw','sm','to','so','ps','dv','mt','mg','ga','cy','mi','fy','lb','rm','ku','xh','st','tn'];
const CMD_LOCALES=['en','ar','fr','es','de','pt','tr','ru','it','nl','hi','ur'];
const STATIC_AI_SOURCE="I’m the SEEKVERA AI assistant. Tell me what you need and I’ll help you find the right section, compare options or search worldwide.";
let localeTimer=0,translateSeq=0;

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
  let v=document.getElementById('lang')?.value||localStorage.getItem('seekvera_lang')||document.documentElement.lang||navigator.language||'en';
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
  const el=document.getElementById('lang');if(!el)return;
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
  const el=document.getElementById('country');if(!el)return;
  const d=langCode();
  for(const o of el.options){
    const code=String(o.value||'').toUpperCase();
    if(code==='WW')o.textContent='🌐';
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
  try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(20)}catch{}
  translateStaticAI();
}
function scheduleLocalePass(){
  clearTimeout(localeTimer);
  const passes=[0,120,500,1200];
  for(const ms of passes)setTimeout(runLocaleEngines,ms);
  localeTimer=setTimeout(runLocaleEngines,1800);
}
function stripDuplicateDepartments(){
  if(!HOME_PATHS.has(location.pathname))return;
  document.querySelector('.r8-department-strip')?.remove();
  document.querySelector('.r5-left')?.remove();
  if(document.getElementById('svR10HomeCleanup'))return;
  const st=document.createElement('style');st.id='svR10HomeCleanup';st.textContent='@media(min-width:980px){body.sv-home-global .r5-market,.r5-market{grid-template-columns:minmax(0,1fr) 240px!important}}';document.head.appendChild(st);
}
function normalizeText(s){return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[’'`´]/g,'').replace(/[^\p{L}\p{N}]+/gu,' ').trim()}
const COUNTRY_TERMS='country|region|دولة|الدولة|بلد|البلد|منطقة|pays|région|国家|地区|país|región|देश|क्षेत्र|região|land|国|地域|국가|지역|negara|wilayah|ülke|bölge|страна|регион|ملک|علاقہ|দেশ|অঞ্চল|quốc gia|khu vực|paese|regione|nchi|eneo|ประเทศ|ภูมิภาค|کشور|منطقه|kraj|regio|bansa|rehiyon|ƙasa|yanki|orilẹ-ede|agbegbe|obodo|mpaghara|ሀገር|ክልል|מדינה|אזור|χώρα|περιοχή|країна|регіон|țară|regiune|země|krajina|régión|ország|régió|maa|alue|държава|država|regija|šalis|regionas|valsts|reģions|riik|piirkond|regió|herrialde|eskualde|rexión|svæði|vend|rajon|земја|ქვეყანა|რეგიონი|երկիր|տարածաշրջան|ölkə|ел|аймақ|mamlakat|hudud|өлкө|аймак|кишвар|минтақа|ýurt|sebit|රට|කලාපය|நாடு|பகுதி|దేశం|ప్రాంతం|രാജ്യം|പ്രദേശം|प्रदेश|દેશ|ਪ੍ਰਦੇਸ਼|ਦੇਸ਼|ਖੇਤਰ|ប្រទេស|តំបន់|ປະເທດ|ພາກພື້ນ|နိုင်ငံ|ဒေသ|улс|бүс|izwe|isifunda|streek|краіна|рэгіён|ሃገር|øki|nuna|igihugu|akarere|atunuu|itulagi|fonua|dal|gobol|هېواد|سیمه|ޤައުމު|ސަރަހައްދު|pajji|reġjun|firenena|faritra|tír|réigiún|gwlad|rhanbarth|whenua|rohe|lân|regioun|pajais|regiun|welat|herêm|ilizwe|ummandla|naha|sebaka|naga|kgaolo'.split('|').map(normalizeText).filter(Boolean);
function hasCountryTerm(text){const s=normalizeText(text),pad=' '+s+' ';return COUNTRY_TERMS.some(t=>/^[a-z0-9\- ]+$/i.test(t)?pad.includes(' '+t+' '):s.includes(t))}
function isCountryCommand(text){
  const s=normalizeText(text);
  return /\b(?:set|switch|change|choose|select)\b.{0,35}\b(?:country|region)\b/.test(s)
    || /(?:حط|حطلي|اختار|اختر|غير|غيرلي|حول|حوللي).{0,30}(?:الدولة|دولة|البلد|بلد)/u.test(String(text||''))
    || /\b(?:mets?|change|passe|choisis?)\b.{0,35}\b(?:pays|region)\b/.test(s)
    || /\b(?:cambia|cambiar|pon|elige|selecciona)\b.{0,35}\b(?:pais|region)\b/.test(s)
    || /\b(?:ander|wechsle|wahle|setze)\b.{0,35}\b(?:land|region)\b/.test(s)
    || /\b(?:mudar|muda|trocar|troca|escolher|escolha)\b.{0,35}\b(?:pais|regiao)\b/.test(s)
    || /\b(?:degistir|degistir|sec|seç)\b.{0,35}\b(?:ulke|ülke|bolge|bölge)\b/.test(s)
    || /(?:смени|сменить|выбери|выбрать|установи).{0,35}(?:стран|регион)/u.test(String(text||''))
    || /\b(?:cambia|imposta|scegli)\b.{0,35}\b(?:paese|regione)\b/.test(s)
    || /(?:ملک|ملک کو|ملک بدل).{0,30}(?:بدل|منتخب|چن)/u.test(String(text||''))
    || hasCountryTerm(text);
}
function countryNames(code){
  const out=new Set([code]);
  const current=langCode();
  for(const l of [current,...CMD_LOCALES]){try{const n=new Intl.DisplayNames([l],{type:'region'}).of(code);if(n)out.add(n)}catch{}}
  return [...out].map(x=>normalizeText(x)).filter(Boolean).sort((a,b)=>b.length-a.length);
}
function resolveCountry(text){
  const el=document.getElementById('country');if(!el)return null;
  const s=normalizeText(text);const hits=[];
  for(const o of el.options){const code=String(o.value||'').toUpperCase();if(!/^[A-Z]{2}$/.test(code))continue;for(const n of countryNames(code)){if(n.length>=3&&s.includes(n)){hits.push({code,n});break}}}
  hits.sort((a,b)=>b.n.length-a.n.length);return hits[0]?.code||null;
}
function addCountryConfirmation(code){
  const name=displayRegion(code,langCode());
  const box=document.getElementById('aiMessages');if(box){const m=document.createElement('div');m.className='ai-msg bot';m.dataset.noTranslate='1';m.textContent='🌍 '+name+' ✓';box.appendChild(m);box.scrollTop=box.scrollHeight;}
  try{window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:name,language:langCode()}}))}catch{}
}
function bindAICountryControl(){
  document.addEventListener('submit',e=>{
    const form=e.target;if(!(form instanceof HTMLFormElement))return;
    if(!(form.id==='aiChatForm'||form.classList.contains('sv-global-compose')||form.closest('#aiChat')))return;
    const input=form.querySelector('#aiChatInput,input[type="text"],input:not([type])');const text=input?.value?.trim()||'';
    if(!text||!isCountryCommand(text))return;
    const code=resolveCountry(text);if(!code)return;
    e.preventDefault();e.stopImmediatePropagation();
    const c=document.getElementById('country');if(!c)return;
    c.value=code;c.dispatchEvent(new Event('input',{bubbles:true}));c.dispatchEvent(new Event('change',{bubbles:true}));
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
  document.addEventListener('change',e=>{if(e.target?.id==='country'||e.target?.id==='lang'){if(e.target.id==='lang')localStorage.setItem('seekvera_lang',e.target.value);queueMicrotask(runLocaleEngines);scheduleLocalePass()}},true);
  window.addEventListener('pageshow',scheduleLocalePass);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)scheduleLocalePass()});
  document.addEventListener('pointerdown',primeVoiceOnGesture,true);
  document.addEventListener('touchstart',primeVoiceOnGesture,{capture:true,passive:true});
  if(window.speechSynthesis){try{speechSynthesis.addEventListener?.('voiceschanged',()=>speechSynthesis.getVoices?.())}catch{}}
}
function init(){stripDuplicateDepartments();buildNav();bindLocaleControls();bindAICountryControl();scheduleLocalePass()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
