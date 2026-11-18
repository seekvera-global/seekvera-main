const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const i18n=fs.readFileSync('i18n-ui.js','utf8');
const navigation=fs.readFileSync('navigation.js','utf8');
const r32=fs.readFileSync('r32-i18n.js','utf8');
const BLOCK='sv_ui_translate_blocked_r19',LOCK='sv_ui_translate_lock_r19';
function storage(seed={}){const map=new Map(Object.entries(seed));return{getItem:k=>map.has(k)?map.get(k):null,setItem:(k,v)=>map.set(k,String(v)),removeItem:k=>map.delete(k),map};}
function harness(code,store,responses,options={}){
 let calls=0;
 const context={sessionStorage:store,AbortController,setTimeout:options.setTimeout||setTimeout,clearTimeout,api:p=>p,langName:l=>l,valid:v=>typeof v==='string'&&!!v.trim(),fetch:async(...args)=>{calls++;if(options.fetch)return options.fetch(...args);const x=responses.shift()||{status:503,body:{reason:'all_translation_backends_unavailable'}};return{status:x.status,ok:x.status>=200&&x.status<300,json:async()=>x.body};},console};
 vm.createContext(context);vm.runInContext(code,context);
 return{context,calls:()=>calls,store};
}
function extract(source,start,end,label){const a=source.indexOf(start),b=source.indexOf(end,a);assert(a>=0&&b>a,label+' source block not found');return source.slice(a,b);}
const quickBlock=extract(i18n,'const QUICK={','};\n// Provisional quota-neutral overrides','QUICK locale map');
const quickContext={INITIAL_AI:'test seed'};
vm.createContext(quickContext);
vm.runInContext(quickBlock+'};this.quick=QUICK;',quickContext);
assert.equal(JSON.stringify(quickContext.quick.az),JSON.stringify({'Back':'Geri','Page navigation':'Səhifə naviqasiyası','Voice reply':'Səsli cavab','Voice':'Səs'}),'Azerbaijani QUICK map must contain the exact local labels');
assert.equal(JSON.stringify(quickContext.quick.kk),JSON.stringify({'Back':'Артқа','Page navigation':'Бет навигациясы','Voice reply':'Дыбыстық жауап','Voice':'Дыбыс'}),'Kazakh QUICK map must contain the exact local labels');
const i18nBlock=extract(i18n,"const UI_TRANSLATE_BLOCK_KEY='sv_ui_translate_blocked_r19'","async function translate(l,arr)","i18n quota helper");
const navBlock=extract(navigation,"let localeTimer=0,translateSeq=0,uiTranslationBlocked=false","const localeControl=","navigation quota helper");
const i18nCode=i18nBlock+"\nthis.cloudTranslate=cloudTranslate;this.blocked=()=>CLOUD_TRANSLATE_BLOCKED;this.alreadyLocalizedValue=alreadyLocalizedValue;";
const navCode=navBlock+"\nthis.requestUiTranslation=requestUiTranslation;this.blocked=()=>uiTranslationBlocked;";
async function main(){
 // A single 503 blocks subsequent language batches in the same tab session.
 const shared=storage(),c=harness(i18nCode,shared,[{status:503,body:{reason:'all_translation_backends_unavailable'}}]);
 const results=await Promise.all([c.context.cloudTranslate('French',['one']),c.context.cloudTranslate('German',['two']),c.context.cloudTranslate('Arabic',['three'])]);
 assert.deepEqual(results,[null,null,null]);assert.equal(c.calls(),1);assert.equal(shared.getItem(BLOCK),'1');assert.equal(shared.getItem(LOCK),null);
 // The navigation fallback shares the same session block and cannot issue another request.
 const n=harness(navCode,shared,[{status:200,body:{translations:['مرحبا']}}]);
 assert.equal(await n.context.requestUiTranslation('Arabic',['Hello']),null);assert.equal(n.calls(),0);
 // Locally reviewed pack/quick labels must bypass the provider entirely.
 const localLabels={'Back':'वापस','Page navigation':'पृष्ठ नेविगेशन','Voice reply':'आवाज़ में जवाब','Voice':'आवाज़'};
 let localFetchCalls=0;
 const localNav={sessionStorage:storage(),AbortController,setTimeout,clearTimeout,fetch:async()=>{localFetchCalls++;return{status:503,ok:false,json:async()=>({reason:'all_translation_backends_unavailable'})}},langCode:()=> 'hi',window:{SEEKVERA_I18N_R32:{tFor:(code,source)=>code==='hi'?(localLabels[source]||source):source}},console};
 vm.createContext(localNav);vm.runInContext(navBlock,localNav);
 const localResult=await localNav.requestUiTranslation('Hindi',['Back','Page navigation','Voice reply','Voice']);
 assert.deepEqual(localResult,['वापस','पृष्ठ नेविगेशन','आवाज़ में जवाब','आवाज़']);assert.equal(localFetchCalls,0);
 // German quick labels must also resolve locally instead of probing the quota-limited provider.
 const germanLabels={'Back':'Zurück','Page navigation':'Seitennavigation','Voice reply':'Sprachantwort','Voice':'Stimme'};
 assert(i18n.includes("'Sprachantwort'") && i18n.includes("'Seitennavigation'"),'German quick labels missing from i18n-ui.js');
 let germanFetchCalls=0;
 const germanNav={sessionStorage:storage(),AbortController,setTimeout,clearTimeout,fetch:async()=>{germanFetchCalls++;return{status:503,ok:false,json:async()=>({reason:'all_translation_backends_unavailable'})}},langCode:()=> 'de',window:{SEEKVERA_I18N_R32:{tFor:(code,source)=>code==='de'?(germanLabels[source]||source):source}},console};
 vm.createContext(germanNav);vm.runInContext(navBlock,germanNav);
 const germanResult=await germanNav.requestUiTranslation('German',['Back','Page navigation','Voice reply','Voice']);
 assert.deepEqual(germanResult,['Zurück','Seitennavigation','Sprachantwort','Stimme']);assert.equal(germanFetchCalls,0);
 // Quota-neutral quick labels for Japanese navigation, Thai plan names and Zulu section headings.
 const quickCases=[
  {code:'vi',language:'Vietnamese',labels:{'Back':'Quay lại','Page navigation':'Điều hướng trang','Voice reply':'Trả lời bằng giọng nói','Voice':'Giọng nói'}},
  {code:'bn',language:'Bangla',labels:{'Back':'পেছনে','Page navigation':'পৃষ্ঠা নেভিগেশন','Voice reply':'কণ্ঠে উত্তর','Voice':'ভয়েস'}},
  {code:'bg',language:'Bulgarian',labels:{'Back':'Назад','Page navigation':'Навигация по страниците','Voice reply':'Гласов отговор','Voice':'Глас'}},
  {code:'hr',language:'Croatian',labels:{'Back':'Natrag','Page navigation':'Navigacija po stranicama','Voice reply':'Glasovni odgovor','Voice':'Glas'}},
  {code:'sr',language:'Serbian',labels:{'Back':'Назад','Page navigation':'Навигација по страницама','Voice reply':'Гласовни одговор','Voice':'Глас'}},
  {code:'ru',language:'Russian',labels:{'Back':'Назад','Page navigation':'Навигация по страницам','Voice reply':'Голосовой ответ','Voice':'Голос'}},
  {code:'ur',language:'Urdu',labels:{'Back':'واپس','Page navigation':'صفحات پر نیویگیشن','Voice reply':'صوتی جواب','Voice':'آواز','Business Yearly':'سالانہ کاروباری منصوبہ','Business Monthly':'ماہانہ کاروباری منصوبہ'}},
  {code:'ja',language:'Japanese',labels:{'Back':'戻る','Page navigation':'ページナビゲーション','Voice reply':'音声で返信','Voice':'音声'}},
  {code:'fil',language:'Filipino',labels:{'Back':'Bumalik','Page navigation':'Pag-navigate sa pahina','Voice reply':'Sagot sa boses','Voice':'Boses'}},
  {code:'el',language:'Greek',labels:{'Back':'Πίσω','Page navigation':'Πλοήγηση σε σελίδα','Voice reply':'Απάντηση με φωνή','Voice':'Φωνή'}},
  {code:'ro',language:'Romanian',labels:{'Back':'Înapoi','Page navigation':'Navigarea paginilor','Voice reply':'Răspuns vocal','Voice':'Voce'}},
  {code:'cs',language:'Czech',labels:{'Back':'Zpět','Page navigation':'Navigace stránek','Voice reply':'Hlasová odpověď','Voice':'Hlas'}},
  {code:'fi',language:'Finnish',labels:{'Back':'Takaisin','Page navigation':'Sivunavigointi','Voice reply':'Äänivastaus','Voice':'Ääni'}},
  {code:'et',language:'Estonian',labels:{'Back':'Tagasi','Page navigation':'Lehe navigatsioon','Voice reply':'Kõne vastus','Voice':'Kõne'}},
  {code:'zu',language:'Zulu',labels:{"Back":"Emuva","Page navigation":"Ukuzulazula kwamakhasi","Voice reply":"Impendulo yezwi","Voice":"Izwi"}},
  {code:'da',language:'Danish',labels:{"Back":"Tilbage","Page navigation":"Sidenavigation","Voice reply":"Stemmesvar","Voice":"Stemme"}},
  {code:'st',language:'Sesotho',labels:{"Back":"Khutlela morao","Page navigation":"Tsamaiso ea maqephe","Voice reply":"Karabo ea lentsoe","Voice":"Lentsoe"}},
  {code:'hu',language:'Hungarian',labels:{"Back":"Vissza","Page navigation":"Oldalnavigáció","Voice reply":"Hangos válasz","Voice":"Hang"}},
  {code:'mt',language:'Maltese',labels:{"Back":"Lura","Page navigation":"Navigazzjoni tal-paġni","Voice reply":"Tweġiba bil-vuċi","Voice":"Vuċi"}},
  {code:'sk',language:'Slovak',labels:{"Back":"Späť","Page navigation":"Navigácia stránok","Voice reply":"Hlasová odpoveď","Voice":"Hlas"}},
  {code:'sv',language:'Swedish',labels:{"Back":"Tillbaka","Page navigation":"Sidnavigering","Voice reply":"Röstsvar","Voice":"Röst"}},
  {code:'no',language:'Norwegian',labels:{"Back":"Tilbake","Page navigation":"Sidenavigasjon","Voice reply":"Talesvar","Voice":"Stemme"}},
  {code:'af',language:'Afrikaans',labels:{"Back":"Terug","Page navigation":"Bladsynavigasie","Voice reply":"Stemantwoord","Voice":"Stem"}},
  {code:'th',language:'Thai',labels:{'Back':'กลับ','Page navigation':'การนำทางหน้าเว็บ','Voice reply':'การตอบกลับด้วยเสียง','Voice':'เสียง','Business Yearly':'แพ็กเกจธุรกิจรายปี','Business Monthly':'แพ็กเกจธุรกิจรายเดือน'}},
  {code:'zu',language:'Zulu',labels:{'GLOBAL AI MARKETPLACE':'Imakethe ye-AI yomhlaba wonke','Courier & last mile':'Ukuthumela nokuletha impahla esigabeni sokugcina'}},
  {code:'ko',language:'Korean',labels:{'Back':'뒤로','Page navigation':'페이지 탐색','Voice reply':'음성 답변','Voice':'음성'}},
  {code:'it',language:'Italian',labels:{'Back':'Indietro','Page navigation':'Navigazione tra le pagine','Voice reply':'Risposta vocale','Voice':'Voce'}},
  {code:'sw',language:'Swahili',labels:{'Back':'Rudi nyuma','Page navigation':'Urambazaji wa kurasa','Voice reply':'Jibu la sauti','Voice':'Sauti'}},
  {code:'fa',language:'Persian',labels:{'Back':'بازگشت','Page navigation':'پیمایش صفحات','Voice reply':'پاسخ صوتی','Voice':'صدا'}},
  {code:'pl',language:'Polish',labels:{'Back':'Wstecz','Page navigation':'Nawigacja stron','Voice reply':'Odpowiedź głosowa','Voice':'Głos'}},
  {code:'nl',language:'Dutch',labels:{'Back':'Terug','Page navigation':'Paginanavigatie','Voice reply':'Spraakantwoord','Voice':'Stem'}},
  {code:'ms',language:'Malay',labels:{'Back':'Kembali','Page navigation':'Navigasi halaman','Voice reply':'Balasan suara','Voice':'Suara'}},
  {code:'ha',language:'Hausa',labels:{'Back':'Komawa baya','Page navigation':'Kewayawa shafuka','Voice reply':'Amsar murya','Voice':'Murya'}},
  {code:'yo',language:'Yoruba',labels:{'Back':'Pada sẹhin','Page navigation':'Lilọ kiri oju-iwe','Voice reply':'Idahun ohun','Voice':'Ohùn'}},
  {code:'ig',language:'Igbo',labels:{'Back':'Laghachi azụ','Page navigation':'Ịgagharị peeji','Voice reply':'Nzaghachi olu','Voice':'Olu'}},
  {code:'am',language:'Amharic',labels:{'Back':'ተመለስ','Page navigation':'የገጽ አሰሳ','Voice reply':'የድምፅ መልስ','Voice':'ድምፅ'}},
  {code:'he',language:'Hebrew',labels:{'Back':'חזרה','Page navigation':'ניווט בעמודים','Voice reply':'תשובה קולית','Voice':'קול'}},
  {code:'uk',language:'Ukrainian',labels:{'Back':'Назад','Page navigation':'Навігація сторінками','Voice reply':'Голосова відповідь','Voice':'Голос'}},
  {code:'ca',language:'Catalan',labels:{'Back':'Enrere','Page navigation':'Navegació de pàgina','Voice reply':'Resposta de veu','Voice':'Veu'}},
  {code:'is',language:'Icelandic',labels:{'Back':'Til baka','Page navigation':'Síðuleiðsögn','Voice reply':'Raddsvör','Voice':'Rödd'}},
  {code:'sq',language:'Albanian',labels:{'Back':'Kthehu','Page navigation':'Navigimi në faqe','Voice reply':'Përgjigje me zë','Voice':'Zëri'}},
  {code:'mk',language:'Macedonian',labels:{'Back':'Назад','Page navigation':'Навигација на страна','Voice reply':'Гласен одговор','Voice':'Глас'}},
  {code:'ka',language:'Georgian',labels:{'Back':'უკან','Page navigation':'გვერდის ნავიგაცია','Voice reply':'ხმის პასუხი','Voice':'ხმა'}},
  {code:'ky',language:'Kyrgyz',labels:{'Back':'Артка','Page navigation':'Барак навигациясы','Voice reply':'Үн менен жооп','Voice':'Үн'}},
  {code:'uz',language:'Uzbek',labels:{'Back':'Orqaga','Page navigation':'Sahifa navigatsiyasi','Voice reply':'Ovoz javobi','Voice':'Ovoz'}},
  {code:'hy',language:'Armenian',labels:{'Back':'Վերադարձ','Page navigation':'Էջի նավիգացիա','Voice reply':'Ձայնային պատասխան','Voice':'Ձայն'}},
  {code:'tg',language:'Tajik',labels:{'Back':'Бозгашт','Page navigation':'Навигатсияи саҳифаҳо','Voice reply':'Ҷавоби овозӣ','Voice':'Овоз'}}
 ];
 const quickContext={INITIAL_AI:'__TEST_INITIAL_AI__'};vm.createContext(quickContext);
 vm.runInContext(extract(i18n,'const QUICK={','// Provisional quota-neutral overrides','QUICK map')+';this.quick=QUICK;',quickContext);
 const quickMap=quickContext.quick;
 for(const item of quickCases){
  for(const [source,value] of Object.entries(item.labels))assert.equal(quickMap[item.code]?.[source],value,item.code+' quick label missing or differs in the actual QUICK map: '+source);
  let calls=0;
  const nav={sessionStorage:storage(),AbortController,setTimeout,clearTimeout,fetch:async()=>{calls++;return{status:503,ok:false,json:async()=>({reason:'all_translation_backends_unavailable'})}},langCode:()=>item.code,window:{SEEKVERA_I18N_R32:{tFor:(code,source)=>code===item.code?(quickMap[code]?.[source]||source):source}},console};
  vm.createContext(nav);vm.runInContext(navBlock,nav);
  const result=await nav.requestUiTranslation(item.language,Object.keys(item.labels));
  assert.deepEqual(result,Object.values(item.labels));assert.equal(calls,0);
 }
 // Google/provider 429 is also terminal for this browser session.
 const s429=storage(),c429=harness(i18nCode,s429,[{status:429,body:{reason:'provider_rate_limited'}}]);
 await Promise.all([c429.context.cloudTranslate('French',['one']),c429.context.cloudTranslate('Arabic',['two'])]);
 assert.equal(c429.calls(),1);assert.equal(s429.getItem(BLOCK),'1');
 // Exact daily quota token is terminal even if returned in the JSON body.
 const sQuota=storage(),nQuota=harness(navCode,sQuota,[{status:503,body:{reason:'daily_free_ai_limit'}}]);
 await Promise.all([nQuota.context.requestUiTranslation('French',['one']),nQuota.context.requestUiTranslation('German',['two'])]);
 assert.equal(nQuota.calls(),1);assert.equal(sQuota.getItem(BLOCK),'1');
 // A non-quota 500 is not persisted as a permanent session block; a later success can recover.
 const s500=storage(),c500=harness(i18nCode,s500,[{status:500,body:{reason:'temporary_internal_error'}},{status:200,body:{translations:['Bonjour']}}]);
 assert.equal(await c500.context.cloudTranslate('French',['Hello']),null);
 assert.deepEqual(await c500.context.cloudTranslate('French',['Hello']),['Bonjour']);
 assert.equal(c500.calls(),2);assert.equal(s500.getItem(BLOCK),null);
 // A pre-existing lock prevents a second component from racing an in-flight request.
 const locked=storage({[LOCK]:String(Date.now())}),nLocked=harness(navCode,locked,[{status:200,body:{translations:['x']}}]);
 assert.equal(await nLocked.context.requestUiTranslation('French',['Hello']),null);assert.equal(nLocked.calls(),0);
 // A hung navigation request is aborted and releases the shared lock without setting a quota block.
 const timeoutStore=storage();
 const timed=harness(navCode,timeoutStore,[],{setTimeout:(fn)=>setTimeout(fn,1),fetch:async(_url,init)=>new Promise((resolve,reject)=>{init.signal.addEventListener('abort',()=>reject(new Error('aborted')),{once:true});})});
 assert.equal(await timed.context.requestUiTranslation('French',['Hello']),null);
 assert.equal(timed.calls(),1);assert.equal(timeoutStore.getItem(LOCK),null);assert.equal(timeoutStore.getItem(BLOCK),null);
 // The main UI translation loop is serial and stops after the first terminal response.
 const translateStart=i18n.indexOf('async function translate(l,arr){'),translateEnd=i18n.indexOf('function setText(',translateStart);
 assert(translateStart>=0&&translateEnd>translateStart,'translation loop source not found');
 const loop=i18n.slice(translateStart,translateEnd);
 assert(!loop.includes('Promise.all'),'translation batches must not run in parallel');
 assert(loop.includes('for(const batch of groups)'),'translation batches must run sequentially');
 const full=harness(i18nCode,storage(),[{status:503,body:{reason:'all_translation_backends_unavailable'}}]);
 full.context.loadPack=async()=>true;full.context.get=()=>'';full.context.worth=()=>true;full.context.put=()=>{};full.context.MEM=new Map();full.context.PACK_VALUES=new Map();full.context.QUICK={};full.context.norm=s=>String(s).toLowerCase();full.context.canonical=s=>String(s).replace(/\\s+/g,' ').trim();
 vm.runInContext(loop+'\nthis.runTranslate=translate;',full.context);
 const changed=await full.context.runTranslate('French',Array.from({length:29},(_,i)=>'source '+i));
 assert.equal(changed,false);assert.equal(full.calls(),1);
 // Reverse pack-value lookup must not re-submit text already localized by the loaded pack.
 const arabicLocalized='لا توجد حالياً إعلانات سوق مباشرة معتمدة. لا تنشئ SEEKVERA إعلانات وهمية.';
 let reversePayload=null;
 const reverse=harness(i18nCode,storage(),[],{fetch:async(_url,init)=>{reversePayload=JSON.parse(init.body);return{status:200,ok:true,json:async()=>({translations:['Hello translated']})};}});
 reverse.context.loadPack=async()=>true;reverse.context.get=()=>'';reverse.context.worth=()=>true;reverse.context.put=()=>{};
 reverse.context.PACK_VALUES=new Map([['ar',new Set([arabicLocalized])]]);
 reverse.context.QUICK={ar:{'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':arabicLocalized}};
 reverse.context.norm=s=>String(s).toLowerCase();reverse.context.canonical=s=>String(s).replace(/\\s+/g,' ').trim();
 vm.runInContext(loop+'\nthis.runTranslate=translate;',reverse.context);
 assert.equal(reverse.context.alreadyLocalizedValue('ar',arabicLocalized),true);
 const reverseChanged=await reverse.context.runTranslate('ar',[arabicLocalized,'Hello']);
 assert.equal(reverseChanged,true);assert.deepEqual(reversePayload.strings,['Hello']);assert.equal(reverse.calls(),1);
 // Embedded feature labels reuse existing production-pack translations without another provider call.
 const getBlock=extract(i18n,"const EMBEDDED_TRANSLATION_TERMS=","function put(l,s,v)","embedded locale-term helper");
 const embeddedContext={QUICK:{hi:{'Back':'वापस','Page navigation':'पृष्ठ नेविगेशन','Voice reply':'आवाज़ में जवाब','Voice':'आवाज़'}},MEM:new Map(),localStorage:storage(),canonical:s=>String(s).replace(/\s+/g,' ').trim(),plainKey:s=>String(s),k:(l,s)=>'sv_'+l+'_'+s};
 vm.createContext(embeddedContext);vm.runInContext(getBlock+'\nthis.get=get;',embeddedContext);
 const msSource='paid calls, paid APIs, paid verification, ads, subscriptions or company payments require an owner notice first. Auto Recharge remains OFF.';
 const msValue='betelle oproppen, betelle APIs, betelle ferifikaasje. Auto Recharge bliuwt OFF.';
 embeddedContext.MEM.set('fy\u0000Auto Recharge','Automatysk opladen');
 embeddedContext.MEM.set('fy\u0000'+msSource,msValue);
 assert.equal(embeddedContext.get('fy',msSource),msValue.replace('Auto Recharge','Automatysk opladen'));
 const klSource='Live marketplace-imi allattorsimaffiit akuerineqarsimasut maannakkut pissarsiarineqarsinnaanngillat.';
 embeddedContext.MEM.set('kl\u0000Live marketplace','Live-mik pisiniarfik');
 embeddedContext.MEM.set('kl\u0000'+klSource,klSource);
 assert.equal(embeddedContext.get('kl',klSource),klSource.replace('Live marketplace','Live-mik pisiniarfik'));
 const tnSource='Games are self-contained SEEKVERA mini games. No stranger chat, gambling, paid loot boxes or external ad network is used.';
 const tnValue='Metshameko ya SEEKVERA e ikemetse. No stranger chat, gambling, paid loot boxes or external ad network is used.';
 embeddedContext.MEM.set('tn\u0000No stranger chat','Ga go na motlotlo ope o o sa tlwaelegang');
 embeddedContext.MEM.set('tn\u0000'+tnSource,tnValue);
 assert.equal(embeddedContext.get('tn',tnSource),tnValue.replace('No stranger chat','Ga go na motlotlo ope o o sa tlwaelegang'));
 assert.equal(embeddedContext.get('hi','Back'),'वापस');
 assert.equal(embeddedContext.get('hi','Page navigation'),'पृष्ठ नेविगेशन');
 assert.equal(embeddedContext.get('hi','Voice reply'),'आवाज़ में जवाब');
 assert.equal(embeddedContext.get('hi','Voice'),'आवाज़');
 // Both navigation fallbacks must use the shared guarded helper, never fetch the endpoint directly.
 const staticFn=extract(navigation,'async function translateStaticAI()','async function translateResidualUI()','static AI fallback');
 const residualFn=extract(navigation,'async function translateResidualUI()','function runLocaleEngines()','residual UI fallback');
 assert(staticFn.includes('requestUiTranslation'));assert(residualFn.includes('requestUiTranslation'));
 assert(staticFn.includes('loadPack')&&staticFn.includes('isLocalizedValue'),'static AI fallback must reuse local pack translations and skip already-localized values');
 assert(residualFn.includes('loadPack')&&residualFn.includes('isLocalizedValue'),'residual UI fallback must reuse local pack translations and skip already-localized values');
 assert(i18n.includes('PACK_VALUES.set(l,localizedValues)'),'locale runtime must index translated pack values for reverse lookup');
 assert(i18n.includes('alreadyLocalizedValue(l,s)'),'locale runtime must skip already-localized pack values');
 assert(r32.includes('PACK_VALUES.set(l,localizedValues)')&&r32.includes('alreadyLocalizedValue(l,s)'),'source runtime must match the deployed reverse-value guard');
 assert(!staticFn.includes("fetch('/api/ui-translate'"));assert(!residualFn.includes("fetch('/api/ui-translate'"));

 // Indonesian quick UI labels must resolve locally with zero provider calls.
 const indonesianLabels={'Back':'Kembali','Page navigation':'Navigasi halaman','Voice reply':'Balasan suara','Voice':'Suara'};
 for(const value of Object.values(indonesianLabels))assert(i18n.includes(value),'Missing Indonesian quick label: '+value);
 let indonesianFetchCalls=0;
 const indonesianNav={sessionStorage:storage(),AbortController,setTimeout,clearTimeout,fetch:async()=>{indonesianFetchCalls++;return{status:503,ok:false,json:async()=>({reason:'all_translation_backends_unavailable'})}},langCode:()=> 'id',window:{SEEKVERA_I18N_R32:{tFor:(code,source)=>code==='id'?(indonesianLabels[source]||source):source}},console};
 vm.createContext(indonesianNav);vm.runInContext(navBlock,indonesianNav);
 const indonesianResult=await indonesianNav.requestUiTranslation('Indonesian',['Back','Page navigation','Voice reply','Voice']);
 assert.deepEqual(indonesianResult,['Kembali','Navigasi halaman','Balasan suara','Suara']);assert.equal(indonesianFetchCalls,0);

 // Provisional Filipino labels for the exact R125 homepage leaks must resolve locally.
 const filipinoLabels={'Back':'Bumalik','Page navigation':'Pag-navigate sa pahina','Voice reply':'Sagot sa boses','Voice':'Boses','OPEN MARKETPLACE →':'Buksan ang pamilihan →','GLOBAL AI MARKETPLACE':'Pamilihang pandaigdig na pinapagana ng AI','🏙️ City break':'🏙️ Maikling bakasyon sa lungsod','GLOBAL AUTO SEARCH':'Pandaigdigang paghahanap ng sasakyan','CROSS-BORDER LOGISTICS':'Logistikang tumatawid sa mga hangganan','Venue / hotel Wi‑Fi QR':'QR para sa Wi‑Fi ng lugar o hotel','Auto Recharge':'Awtomatikong pag-recharge','Zero‑Cost Mode':'Mode na walang gastos','RFQ / supplier sourcing':'Kahilingan sa presyo / paghahanap ng tagapagtustos'};
 for(const value of Object.values(filipinoLabels))assert(i18n.includes(value),'Missing Filipino quick label: '+value);
 let filipinoFetchCalls=0;
 const filipinoNav={sessionStorage:storage(),AbortController,setTimeout,clearTimeout,fetch:async()=>{filipinoFetchCalls++;return{status:503,ok:false,json:async()=>({reason:'all_translation_backends_unavailable'})}},langCode:()=> 'fil',window:{SEEKVERA_I18N_R32:{tFor:(code,source)=>code==='fil'?(filipinoLabels[source]||source):source}},console};
 vm.createContext(filipinoNav);vm.runInContext(navBlock,filipinoNav);
 const filipinoResult=await filipinoNav.requestUiTranslation('Filipino',Object.keys(filipinoLabels));
 assert.deepEqual(filipinoResult,Object.values(filipinoLabels));assert.equal(filipinoFetchCalls,0);

 // Additional quota-neutral locale labels for the R125 exact-leak findings.
 const provisionalQuickCases=[
  {code:'az',language:'Azerbaijani',labels:{'Back':'Geri','Page navigation':'Səhifə naviqasiyası','Voice reply':'Səsli cavab','Voice':'Səs'}},
  {code:'kk',language:'Kazakh',labels:{'Back':'Артқа','Page navigation':'Бет навигациясы','Voice reply':'Дыбыстық жауап','Voice':'Дыбыс'}},
  {code:'da',language:'Danish',labels:{'Find Wi-Fi →':'Søg efter Wi-Fi →','Find catering':'Søg efter catering','AI Voice Agent':'AI-stemmeassistent'}},
  {code:'st',language:'Sesotho',labels:{'Free / Public Wi-Fi Finder':'Sesebelisoa sa ho fumana Wi-Fi ea mahala kapa ea sechaba','RFQ / supplier sourcing':'Kopo ea theko / ho fumana barekisi','Delivery & Courier':'Phano le litšebeletso tsa ba tsamaisang thepa'}},
  {code:'ro',language:'Romanian',labels:{'🏙️ City break':'🏙️ Escapadă urbană','Business Monthly':'Plan de afaceri lunar'}},
  {code:'hu',language:'Hungarian',labels:{'← Travel Hub':'← Utazási központ'}},
  {code:'mt',language:'Maltese',labels:{'🏙️ City break':'🏙️ Vjaġġ qasir fil-belt'}},
  {code:'el',language:'Greek',labels:{'AI Voice Agent':'Φωνητικός βοηθός AI'}},
  {code:'cs',language:'Czech',labels:{'AI Voice Agent':'Hlasový asistent AI'}},
  {code:'sk',language:'Slovak',labels:{'AI Voice Agent':'Hlasový asistent AI'}},
  {code:'sv',language:'Swedish',labels:{'AI Voice Agent':'AI-röstassistent'}},
  {code:'no',language:'Norwegian',labels:{'AI Voice Agent':'AI-stemmeassistent','Business Monthly':'Månedlig bedriftsplan'}},
  {code:'sl',language:'Slovenian',labels:{'Back':'Nazaj','Page navigation':'Navigacija po straneh','Voice reply':'Glasovni odgovor','Voice':'Glas'}},
  {code:'lt',language:'Lithuanian',labels:{'Back':'Atgal','Page navigation':'Puslapių naršymas','Voice reply':'Atsakymas balsu','Voice':'Balsas'}},
  {code:'lv',language:'Latvian',labels:{'Back':'Atpakaļ','Page navigation':'Lapu navigācija','Voice reply':'Balss atbilde','Voice':'Balss'}},
  {code:'af',language:'Afrikaans',labels:{'AI Voice Agent':'KI-stemassistent'}}
 ];
 for(const item of provisionalQuickCases){
  for(const value of Object.values(item.labels))assert(i18n.includes(value),'Missing '+item.code+' provisional quick label: '+value);
  let calls=0;
  const nav={sessionStorage:storage(),AbortController,setTimeout,clearTimeout,fetch:async()=>{calls++;return{status:503,ok:false,json:async()=>({reason:'all_translation_backends_unavailable'})}},langCode:()=>item.code,window:{SEEKVERA_I18N_R32:{tFor:(code,source)=>code===item.code?(item.labels[source]||source):source}},console};
  vm.createContext(nav);vm.runInContext(navBlock,nav);
  const result=await nav.requestUiTranslation(item.language,Object.keys(item.labels));
  assert.deepEqual(result,Object.values(item.labels));assert.equal(calls,0,item.code+' must not call the translation provider');
 }


 // R125 exact English UI leaks must resolve from quota-neutral provisional overrides.
 const provisionalBlock=extract(i18n,'const R125_PROVISIONAL={','function api(p)','R125 provisional locale map');
 const provisionalContext={};vm.createContext(provisionalContext);
 vm.runInContext(provisionalBlock+';this.labels=R125_PROVISIONAL;',provisionalContext);
 const r125Labels=provisionalContext.labels;
 assert.deepEqual(Object.keys(r125Labels).sort(),['fy','lb','lo','mg','rm','rw','tn','tr'].sort());
 const rawGetBlock=extract(i18n,'function rawGet(l,s){','function get(l,s){','R125 provisional raw lookup');
 const rawContext={canonical:s=>String(s||'').trim(),QUICK:{},R125_PROVISIONAL:r125Labels,MEM:new Map(),plainKey:s=>String(s||''),localStorage:storage(),k:()=>''};
 vm.createContext(rawContext);vm.runInContext(rawGetBlock+';this.rawGet=rawGet;',rawContext);
 const localizedValueBlock=extract(i18n,'function alreadyLocalizedValue(l,s){','async function translate(l,arr){','R125 provisional reverse-value lookup');
 const localizedValueContext={norm:s=>String(s||'').toLowerCase(),canonical:s=>String(s||'').trim(),PACK_VALUES:new Map(),QUICK:{},R125_PROVISIONAL:r125Labels};
 vm.createContext(localizedValueContext);vm.runInContext(localizedValueBlock+';this.isLocalized=alreadyLocalizedValue;',localizedValueContext);
 for(const [code,labels] of Object.entries(r125Labels)){
  for(const [source,value] of Object.entries(labels)){
   assert.equal(localizedValueContext.isLocalized(code,value),true,code+' provisional value must be recognized as already localized');
   assert.equal(localizedValueContext.isLocalized(code,source),false,code+' English source must not be mistaken for a localized value');
  }
 }
 let r125LabelCount=0;
 for(const [code,labels] of Object.entries(r125Labels)){
  assert(Object.keys(labels).length>0,code+' provisional labels missing');
  for(const [source,value] of Object.entries(labels)){
   assert(value.trim()&&value!==source,code+' still has an English/empty override for '+source);
   assert.equal(rawContext.rawGet(code,source),value,code+' rawGet override mismatch for '+source);
   r125LabelCount++;
  }
  let calls=0;
  const nav={sessionStorage:storage(),AbortController,setTimeout,clearTimeout,fetch:async()=>{calls++;return{status:503,ok:false,json:async()=>({reason:'all_translation_backends_unavailable'})}},langCode:()=>code,window:{SEEKVERA_I18N_R32:{tFor:(language,source)=>language===code?(labels[source]||source):source}},console};
  vm.createContext(nav);vm.runInContext(navBlock,nav);
  const result=await nav.requestUiTranslation(code,Object.keys(labels));
  assert.deepEqual(result,Object.values(labels),code+' provisional labels should resolve locally');
  assert.equal(calls,0,code+' provisional labels must not call translation provider');
 }
 assert.equal(r125LabelCount,36,'unexpected R125 provisional mapping count');
 assert(i18n.includes("typeof R125_PROVISIONAL!=='undefined'"),'rawGet must remain compatible with isolated legacy tests');

 console.log('PASS: session quota circuit breaker, shared in-flight lock, sequential batches, navigation fallback and reverse pack-value guard');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
