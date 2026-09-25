/* SEEKVERA R23 — stability guard + transparent zero-cost local routing fallback. */
(()=>{'use strict';
if(window.__SEEKVERA_R23_STABILITY)return;window.__SEEKVERA_R23_STABILITY=true;
window.__seekveraLocaleGuardR9=true;
const VERSION='20260925-r23-stable',AI_FALLBACK='20260925-r23-ai-local';
let timer=0,raf=0;
function installStyle(){
  if(document.getElementById('svR23Stability'))return;
  const s=document.createElement('style');s.id='svR23Stability';s.textContent=`
html,body{max-width:100%;overflow-x:hidden!important;-webkit-text-size-adjust:100%;text-size-adjust:100%}
html{scrollbar-gutter:stable}
body{overflow-anchor:none}
.r5-shell,.r5-main,.r5-market,.r5-center,#categories,.r5-grid,#aiChat,.sv-unified-chat{min-width:0!important;max-width:100%!important}
#categories .r5-tile{min-width:0!important;width:100%!important;overflow:hidden!important;contain:layout paint!important}
#categories .r5-tile-body{min-width:0!important;overflow:hidden!important}
#categories .r5-tile-body>b,#categories .r5-tile-body>small{max-width:100%!important;overflow-wrap:anywhere!important;word-break:normal!important}
#aiChat,.sv-unified-chat{min-width:0!important;max-width:100%!important;overflow-x:hidden!important;contain:layout!important;overflow-anchor:none!important}
#aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{overflow-anchor:none!important;scroll-behavior:auto!important}
html.sv-r15-applying *,html.sv-r23-applying *{animation:none!important;transition:none!important}
@media(max-width:780px){#categories .r5-tile,#aiChat,.sv-unified-chat{transform:none!important}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;scroll-behavior:auto!important;transition-duration:.01ms!important}}
`;
  document.head.appendChild(s);
}
const NAME_CODE={english:'en',arabic:'ar',hindi:'hi',french:'fr',spanish:'es',portuguese:'pt',german:'de',chinese:'zh',mandarin:'zh',japanese:'ja',korean:'ko',turkish:'tr',russian:'ru',italian:'it',urdu:'ur',bengali:'bn',indonesian:'id',swahili:'sw'};
const ROUTES={general:['marketplace.html',0],travel:['travel.html',1],property:['property.html',5],cars:['cars-auto.html',6],jobs:['jobs.html',7],shopping:['shopping.html',8],restaurants:['restaurants-food.html',9],services:['local-services.html',10],equipment:['equipment-machinery.html',11],boats:['boats-marine.html',12],business:['import-export.html',13],shipping:['shipping-logistics.html',14],software:['software.html',16],solar:['solar-energy.html',18],education:['education.html',19],health:['health.html',20],money:['money-insurance.html',21],media:['media.html',22],games:['games.html',24],connectivity:['connectivity.html',25],wifi:['wifi.html',26],promote:['promote.html',30]};
function langCode(v,text=''){let s=String(v||'').toLowerCase().trim();if(NAME_CODE[s])return NAME_CODE[s];s=s.split(/[-_ ]/)[0];if(/^[a-z]{2,3}$/.test(s)&&s!=='auto')return s;if(/[\u0600-\u06ff]/.test(text))return'ar';if(/[\u0900-\u097f]/.test(text))return'hi';if(/[\u4e00-\u9fff]/.test(text))return'zh';if(/[\u3040-\u30ff]/.test(text))return'ja';if(/[\uac00-\ud7af]/.test(text))return'ko';return String(document.getElementById('lang')?.value||document.documentElement.lang||'en').toLowerCase().split(/[-_]/)[0]||'en'}
function localCategory(t){t=String(t||'').toLowerCase();const tests=[['wifi',/free wi-?fi|public wi-?fi|واي فاي|वाई.?फाई/u],['connectivity',/esim|internet|sim card|mobile data|انترنت|إنترنت|شريحة|इंटरनेट|सिम/u],['travel',/hotel|flight|travel|tourism|airport|visa|فندق|سفر|سياحة|طيران|होटल|उड़ान|यात्रा|पर्यटन/u],['property',/property|house|apartment|land|rent|عقار|بيت|شقة|ارض|أرض|إيجار|मकान|अपार्टमेंट|ज़मीन|किराया/u],['cars',/car|vehicle|spare part|سيارة|مركبة|قطع غيار|कार|वाहन/u],['jobs',/job|career|vacancy|وظيفة|عمل|नौकरी|करियर/u],['restaurants',/restaurant|food|cafe|مطعم|طعام|قهوة|रेस्तरां|खाना/u],['health',/hospital|clinic|doctor|pharmacy|health|مستشفى|عيادة|طبيب|صيدلية|صحة|अस्पताल|डॉक्टर|स्वास्थ्य/u],['shipping',/shipping|freight|cargo|delivery|شحن|بضائع|توصيل|शिपिंग|डिलीवरी/u],['business',/supplier|manufacturer|import|export|factory|مورد|مصنع|استيراد|تصدير|आयात|निर्यात|आपूर्तिकर्ता/u],['equipment',/equipment|machinery|machine|معدات|آلات|मशीन|उपकरण/u],['boats',/boat|marine|yacht|قارب|يخت|समुद्री|नाव/u],['solar',/solar|energy|panel|طاقة شمسية|ألواح|सौर|ऊर्जा/u],['education',/school|course|education|university|مدرسة|دورة|تعليم|جامعة|स्कूल|कोर्स|शिक्षा/u],['money',/insurance|finance|money|تأمين|تمويل|مال|बीमा|वित्त/u],['games',/game|play|لعبة|ألعاب|खेल/u],['software',/software|hosting|website|app|برنامج|استضافة|موقع|सॉफ्टवेयर|वेबसाइट/u],['shopping',/shop|buy|product|shopping|شراء|منتج|تسوق|खरीद|उत्पाद|शॉपिंग/u],['services',/service|repair|plumber|electrician|خدمة|تصليح|سباك|كهربائي|सेवा|मरम्मत/u],['media',/movie|film|music|news|tv|فيلم|موسيقى|أخبار|تلفزيون|फिल्म|संगीत|समाचार/u],['promote',/promote|advertise|business plan|ترويج|إعلان|व्यवसाय|प्रचार/u]];for(const [c,r]of tests)if(r.test(t))return c;return'general'}
function titleFor(lang,cat){const idx=(ROUTES[cat]||ROUTES.general)[1],d=window.SEEKVERA_R14_CATEGORIES?.data?.[lang];if(Array.isArray(d)&&d[idx])return String(d[idx]).trim();if(lang==='ar')return cat==='general'?'السوق':'SEEKVERA';if(lang==='hi')return cat==='general'?'बाज़ार':'SEEKVERA';return lang==='en'?(cat==='general'?'Marketplace':cat[0].toUpperCase()+cat.slice(1)):'SEEKVERA'}
function fallbackText(lang,title){const x={en:`SEEKVERA Assist is in local mode right now. I can still take you to ${title} and keep your request ready.`,ar:`مساعد SEEKVERA يعمل الآن بوضع محلي. أستطيع توجيهك إلى ${title} وإبقاء طلبك جاهزًا.`,hi:`SEEKVERA सहायक अभी स्थानीय मोड में है। मैं आपको ${title} तक ले जा सकता हूँ और आपका अनुरोध तैयार रख सकता हूँ।`,fr:`L’assistant SEEKVERA fonctionne actuellement en mode local. Je peux vous diriger vers ${title} et garder votre demande prête.`,es:`El asistente SEEKVERA está en modo local. Puedo llevarte a ${title} y mantener tu solicitud lista.`,pt:`O assistente SEEKVERA está em modo local. Posso levar você a ${title} e manter seu pedido pronto.`,de:`SEEKVERA Assist läuft gerade im lokalen Modus. Ich kann Sie zu ${title} führen und Ihre Anfrage bereithalten.`,zh:`SEEKVERA 助手目前处于本地模式。我仍可带您前往 ${title} 并保留您的请求。`,ja:`SEEKVERA アシストは現在ローカルモードです。${title} へ案内し、リクエストを保持できます。`,ko:`SEEKVERA 도우미는 현재 로컬 모드입니다. ${title}로 안내하고 요청을 준비해 둘 수 있습니다.`,tr:`SEEKVERA Asistan şu anda yerel modda. Sizi ${title} bölümüne yönlendirebilir ve isteğinizi hazır tutabilirim.`,ru:`SEEKVERA Assist сейчас работает в локальном режиме. Я могу направить вас в ${title} и сохранить ваш запрос готовым.`,it:`SEEKVERA Assist è ora in modalità locale. Posso portarti a ${title} e mantenere pronta la tua richiesta.`};return x[lang]||`🔎 ${title}`}
function installAiFallback(){
  if(window.__SEEKVERA_AI_LOCAL_FALLBACK)return;window.__SEEKVERA_AI_LOCAL_FALLBACK=true;
  const native=window.fetch.bind(window);
  window.fetch=async function(input,init){
    const reqClone=(typeof Request!=='undefined'&&input instanceof Request)?input.clone():null;
    const res=await native(input,init);
    let url='';try{url=new URL(typeof input==='string'?input:input?.url||'',location.href).pathname}catch{}
    if(url!=='/api/ai'||res.status!==503)return res;
    let err=null;try{err=await res.clone().json()}catch{}
    if(!err?.retryable)return res;
    let raw=init?.body;try{if(raw==null&&reqClone)raw=await reqClone.text()}catch{}
    let body={};try{body=typeof raw==='string'?JSON.parse(raw):{}}catch{}
    const message=String(body.message||body.prompt||''),lang=langCode(body.language,message),cat=localCategory(message),[route]=ROUTES[cat]||ROUTES.general,title=titleFor(lang,cat);
    const payload={ok:true,response:fallbackText(lang,title),language:lang,category:cat,route,countryAction:null,liveData:false,degraded:true,providerAvailable:false,reason:String(err.reason||'ai_provider_unavailable'),model:'seekvera-local-router',fallbackVersion:AI_FALLBACK};
    return new Response(JSON.stringify(payload),{status:200,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-seekvera-ai-mode':'local-router'}});
  }
}
function apply(){
  installStyle();installAiFallback();
  document.documentElement.dataset.svR20='ready';document.documentElement.dataset.svR23='stable';document.documentElement.dataset.svAiFallback='ready';
  document.documentElement.classList.add('sv-r23-applying');
  cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>requestAnimationFrame(()=>document.documentElement.classList.remove('sv-r23-applying')));
  try{window.SEEKVERA_R22_CATEGORY_LOCK?.schedule?.(24)}catch{}
}
function schedule(ms=60){clearTimeout(timer);timer=setTimeout(apply,ms)}
function bind(){installStyle();installAiFallback();schedule(0);schedule(220);window.addEventListener('pageshow',()=>schedule(20));window.addEventListener('load',()=>schedule(20),{once:true});window.addEventListener('seekvera:languagechange',()=>schedule(40));window.addEventListener('seekvera:countrychange',()=>schedule(40));window.addEventListener('orientationchange',()=>schedule(120))}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
window.SEEKVERA_R20_FINAL={version:VERSION,aiFallbackVersion:AI_FALLBACK,apply,schedule,descriptions:[],extraLanguages:[]};
})();
