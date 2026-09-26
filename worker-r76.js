import baseWorker from './worker-r31.js';

const RELEASE='20260926-r76-unified-global-ai';
const PRIMARY='@cf/zai-org/glm-4.7-flash';
const FALLBACK='@cf/qwen/qwen3-30b-a3b-fp8';
const ALLOWED=new Set(['https://seekveraglobal.com','https://www.seekveraglobal.com','https://seekvera-global.github.io','https://seekvera-main.seekvera-global.workers.dev']);
const ROUTES={marketplace:'marketplace.html',general:'marketplace.html',travel:'travel.html',tourism:'tourism.html',property:'property.html',cars:'cars-auto.html',jobs:'jobs.html',shopping:'shopping.html',restaurants:'restaurants-food.html',services:'local-services.html',equipment:'marketplace.html?q=equipment',boats:'marketplace.html?q=boats',business:'import-export.html',shipping:'shipping-logistics.html',businessSoftware:'business-software.html',software:'software.html',hosting:'web-hosting.html',solar:'solar.html',education:'education.html',health:'health.html',money:'money-insurance.html',entertainment:'entertainment.html',media:'media.html',games:'games.html',connectivity:'connectivity.html',wifi:'wifi.html',dealAgent:'deal-agent.html',everyday:'everyday.html',scan:'scan.html',promote:'seller-plans.html'};
const CATS=new Set(Object.keys(ROUTES));
const LANGS=new Set(['en','ar','fr','zh','es','hi','pt','de','ja','ko','id','tr','ru','ur','bn','vi','it','sw','th','fa','pl','nl','ms','fil','ha','yo','ig','am','he','el','uk','ro','cs','sk','hu','sv','no','da','fi','bg','hr','sr','sl','lt','lv','et','ca','eu','gl','is','sq','mk','ka','hy','az','kk','uz','ky','tg','tk','ne','si','ta','te','ml','mr','gu','pa','km','lo','my','mn','zu','af','be','bs','dz','ti','fo','kl','rw','sm','to','so','ps','dv','mt','mg','ga','cy','mi','fy','lb','rm','ku','xh','st','tn']);
const clean=(v,n=4000)=>String(v??'').replace(/[\u0000-\u001F\u007F]/g,' ').trim().slice(0,n);
function headers(req){const o=req.headers.get('origin')||'';return{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff','x-seekvera-release':RELEASE,...(ALLOWED.has(o)?{'access-control-allow-origin':o}:{}),'vary':'Origin'}}
function json(req,d,status=200){return new Response(JSON.stringify(d),{status,headers:headers(req)})}
function modelText(x){return typeof x==='string'?x.trim():typeof x?.response==='string'?x.response.trim():typeof x?.result?.response==='string'?x.result.response.trim():typeof x?.result==='string'?x.result.trim():typeof x?.choices?.[0]?.message?.content==='string'?x.choices[0].message.content.trim():''}
function blocked(t){const s=String(t||'').toLowerCase();const rules=[[/\b(gun|firearm|rifle|pistol|shotgun|ammunition|grenade|explosive|bomb|taser|switchblade)\b|سلاح|مسدس|بندقية|ذخيرة|قنبلة|متفجر/u,'weapons_or_explosives'],[/\b(nude|naked|porn|pornography|sexual services?|escort services?)\b|عاري|إباحي|خدمات جنسية/u,'explicit_sexual_content'],[/\b(cocaine|heroin|meth|fentanyl|mdma|lsd|illegal drugs?)\b|كوكايين|هيروين|مخدرات/u,'controlled_drugs'],[/\b(stolen goods?|counterfeit|fake passport|forged id)\b|مسروق|مزور/u,'stolen_counterfeit_or_fake_documents'],[/human trafficking|child sexual|terrorist propaganda|extremist propaganda|اتجار بالبشر|استغلال أطفال|دعاية إرهابية/u,'severe_illegal_content'],[/\b(otp|one.time password|cvv|cvc|bank password|email password|gmail password|password)\b|كلمة المرور|رمز التحقق|الرقم السري/u,'sensitive_credentials'],[/\b(seed phrase|recovery phrase|private key)\b|عبارة الاسترداد|مفتاح خاص/u,'financial_secret']];for(const[r,reason]of rules)if(r.test(s))return reason;return''}
function parseJSON(text){const raw=String(text||'').trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'');try{return JSON.parse(raw)}catch{}const a=raw.indexOf('{'),b=raw.lastIndexOf('}');if(a>=0&&b>a)try{return JSON.parse(raw.slice(a,b+1))}catch{}return null}
function countryCode(v){v=String(v||'').trim().toUpperCase();return v==='WW'||/^[A-Z]{2}$/.test(v)?v:''}
function languageCode(v){v=String(v||'').trim().toLowerCase().split(/[-_ ]/)[0];return LANGS.has(v)?v:''}
function category(v){v=String(v||'').trim();return CATS.has(v)?v:'general'}
function historyText(h){if(!Array.isArray(h))return'';return h.slice(-10).map(x=>`${x?.role==='assistant'?'assistant':'user'}: ${clean(x?.content,1000)}`).filter(Boolean).join('\n').slice(-6500)}

const LANGUAGE_NAMES={english:'en',arabic:'ar',french:'fr',chinese:'zh',spanish:'es',hindi:'hi',portuguese:'pt',german:'de',japanese:'ja',korean:'ko',indonesian:'id',turkish:'tr',russian:'ru',urdu:'ur',bengali:'bn',vietnamese:'vi',italian:'it',swahili:'sw',thai:'th',persian:'fa',polish:'pl',dutch:'nl',malay:'ms',filipino:'fil',hausa:'ha',yoruba:'yo',igbo:'ig',amharic:'am',hebrew:'he',greek:'el',ukrainian:'uk',romanian:'ro',czech:'cs',slovak:'sk',hungarian:'hu',swedish:'sv',norwegian:'no',danish:'da',finnish:'fi',bulgarian:'bg',croatian:'hr',serbian:'sr',slovenian:'sl',lithuanian:'lt',latvian:'lv',estonian:'et',catalan:'ca',basque:'eu',galician:'gl',icelandic:'is',albanian:'sq',macedonian:'mk',georgian:'ka',armenian:'hy',azerbaijani:'az',kazakh:'kk',uzbek:'uz',kyrgyz:'ky',tajik:'tg',turkmen:'tk',nepali:'ne',sinhala:'si',tamil:'ta',telugu:'te',malayalam:'ml',marathi:'mr',gujarati:'gu',punjabi:'pa',khmer:'km',lao:'lo',burmese:'my',mongolian:'mn',zulu:'zu',afrikaans:'af',belarusian:'be',bosnian:'bs',dzongkha:'dz',tigrinya:'ti',faroese:'fo',greenlandic:'kl',kalaallisut:'kl',kinyarwanda:'rw',samoan:'sm',tongan:'to',somali:'so',pashto:'ps',divehi:'dv',maltese:'mt',malagasy:'mg',irish:'ga',welsh:'cy',maori:'mi',frisian:'fy',luxembourgish:'lb',romansh:'rm',kurdish:'ku',xhosa:'xh',sotho:'st',tswana:'tn'};
function normalizedLanguage(v,message=''){
 const direct=languageCode(v);if(direct)return direct;
 const n=clean(v,80).toLowerCase();if(LANGUAGE_NAMES[n])return LANGUAGE_NAMES[n];
 const t=String(message||'');if(/[\u0600-\u06ff]/u.test(t))return'ar';if(/[\u3040-\u30ff]/u.test(t))return'ja';if(/[\u4e00-\u9fff]/u.test(t))return'zh';if(/[\uac00-\ud7af]/u.test(t))return'ko';if(/[\u0900-\u097f]/u.test(t))return'hi';if(/[\u0590-\u05ff]/u.test(t))return'he';return'en';
}
function aliasHit(s,a){a=String(a).toLowerCase();if(/^[a-z]{1,3}$/i.test(a))return new RegExp(`(?:^|[^a-z])${a.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}(?:$|[^a-z])`,'i').test(s);return s.includes(a)}
const COUNTRY_ALIASES={
 WW:['worldwide','global','all countries','كل الدول','كل العالم','العالم كله','ورلد وايد','وورلد وايد','عالمي'],
 TR:['turkey','türkiye','turkiye','تركيا'],LB:['lebanon','لبنان'],FR:['france','فرنسا'],NG:['nigeria','نيجيريا'],DE:['germany','deutschland','ألمانيا','المانيا'],US:['united states','usa','america','أمريكا','امريكا'],GB:['united kingdom','britain','england','uk','بريطانيا','إنجلترا','انجلترا'],AE:['united arab emirates','uae','emirates','الإمارات','الامارات'],SA:['saudi arabia','saudi','السعودية'],QA:['qatar','قطر'],CA:['canada','كندا'],AU:['australia','أستراليا','استراليا'],EG:['egypt','مصر'],SY:['syria','سوريا'],JO:['jordan','الأردن','الاردن'],KE:['kenya','كينيا'],IN:['india','الهند'],CN:['china','الصين'],JP:['japan','اليابان'],RU:['russia','روسيا'],BR:['brazil','البرازيل'],ES:['spain','إسبانيا','اسبانيا'],IT:['italy','إيطاليا','ايطاليا'],NL:['netherlands','holland','هولندا'],CH:['switzerland','سويسرا'],SE:['sweden','السويد'],NO:['norway','النرويج'],DK:['denmark','الدنمارك'],FI:['finland','فنلندا'],ZA:['south africa','جنوب أفريقيا','جنوب افريقيا'],GH:['ghana','غانا'],MA:['morocco','المغرب'],DZ:['algeria','الجزائر'],TN:['tunisia','تونس']
};
const LANGUAGE_ALIASES={
 tr:['turkish','türkçe','turkce','تركي','التركية'],ar:['arabic','عربي','العربية'],en:['english','انجليزي','إنجليزي','انكليزي','إنكليزي'],fr:['french','français','francais','فرنسي','الفرنسية'],de:['german','deutsch','ألماني','الماني','الألمانية'],es:['spanish','español','espanol','إسباني','اسباني'],zh:['chinese','中文','صيني','الصينية'],ja:['japanese','日本語','ياباني','اليابانية'],hi:['hindi','हिन्दी','हिंदी','هندي'],ru:['russian','русский','روسي','الروسية'],pt:['portuguese','português','برتغالي'],it:['italian','italiano','إيطالي','ايطالي'],nl:['dutch','nederlands','هولندي'],ko:['korean','한국어','كوري'],id:['indonesian','bahasa indonesia','إندونيسي','اندونيسي'],ur:['urdu','اردو','أردو']
};
function controlVerb(s){return /(?:\b(?:change|switch|set|select)\b.{0,28}\b(?:app|application|country|market|region|language)\b|\b(?:change|switch|set)\b.{0,24}\bto\b|حط(?:ني|لي)?|غي(?:ر|ّر)|حو(?:ل|ّل)|بد(?:ل|ّل)|انقل(?:ني)?|غيرلي|غير لي|حوّلني|حولني|cambia.{0,25}(?:app|pa[ií]s|idioma)|changez.{0,25}(?:application|pays|langue)|wechsel.{0,25}(?:app|land|sprache)|(?:uygulama|ülke|dil).{0,25}değiş|(?:приложение|стран|язык).{0,25}(?:смен|измен)|(?:应用|国家|语言).{0,12}(?:切换|更改|改))/iu.test(s)}
function languageIntent(s){return /language|لغة|langue|sprache|idioma|lingua|(?:^|\W)dil(?:i)?(?:\W|$)|язык|语言|語言|言語|भाषा/iu.test(s)}
function findAliasCode(s,map){let hits=[];for(const[code,aliases]of Object.entries(map))for(const a of aliases)if(aliasHit(s,a))hits.push([a.length,code]);hits.sort((a,b)=>b[0]-a[0]);return hits[0]?.[1]||''}
function explicitLanguageAction(message){const s=String(message||'').toLowerCase();if(!controlVerb(s))return'';const code=findAliasCode(s,LANGUAGE_ALIASES);if(!code)return'';if(languageIntent(s))return code;if(/[\u0600-\u06ff]/u.test(s)&&/(حط(?:لي|ني)?|غي(?:ر|ّر)|حو(?:ل|ّل)|بد(?:ل|ّل))/u.test(s)&&!findAliasCode(s,COUNTRY_ALIASES))return code;return''}
function explicitCountryAction(message){const s=String(message||'').toLowerCase();if(!controlVerb(s))return'';return findAliasCode(s,COUNTRY_ALIASES)}
function actionReply(lang,cc,ll){
 const kind=ll?'language':'country';
 const r={
  ar:{country:'تمام، فهمت. سأغيّر التطبيق الآن إلى الدولة التي طلبتها.',language:'تمام، فهمت. سأغيّر لغة التطبيق الآن.'},
  en:{country:'Got it. I’ll switch the app to the country you requested now.',language:'Got it. I’ll change the app language now.'},
  tr:{country:'Tamam. Uygulamayı istediğiniz ülkeye şimdi geçiriyorum.',language:'Tamam. Uygulama dilini şimdi değiştiriyorum.'},
  fr:{country:'Compris. Je passe maintenant l’application au pays demandé.',language:'Compris. Je change maintenant la langue de l’application.'},
  de:{country:'Verstanden. Ich stelle die App jetzt auf das gewünschte Land um.',language:'Verstanden. Ich ändere jetzt die Sprache der App.'},
  es:{country:'Entendido. Ahora cambio la app al país que pediste.',language:'Entendido. Ahora cambio el idioma de la app.'},
  ru:{country:'Понял. Сейчас переключу приложение на выбранную страну.',language:'Понял. Сейчас изменю язык приложения.'},
  zh:{country:'明白了。我现在把应用切换到你指定的国家。',language:'明白了。我现在更改应用语言。'},
  hi:{country:'समझ गया। अब ऐप को आपके चुने हुए देश पर बदल रहा हूँ।',language:'समझ गया। अब ऐप की भाषा बदल रहा हूँ।'}
 };
 return(r[lang]||r.en)[kind];
}
async function degradedFallback(request,env,ctx,body,message){
 const fallback=await baseWorker.fetch(request,env,ctx);let d=null;try{d=await fallback.clone().json()}catch{}
 if(!d||typeof d!=='object'){const h=new Headers(fallback.headers);h.set('x-seekvera-release',RELEASE);return new Response(fallback.body,{status:fallback.status,statusText:fallback.statusText,headers:h})}
 const language=normalizedLanguage(d.language,message),cat=category(d.category),localLL=explicitLanguageAction(message),localCC=explicitCountryAction(message),baseLL=languageCode(d?.languageAction?.code),baseCC=countryCode(d?.countryAction?.code),ll=localLL||baseLL,cc=localCC||baseCC;
 return json(request,{...d,ok:d.ok!==false,response:(cc||ll)?actionReply(language,cc,ll):clean(d.response,5000),language,category:cat,route:ROUTES[cat]||ROUTES.general,countryAction:cc?{type:'set-country',code:cc}:null,languageAction:ll?{type:'set-language',code:ll}:null,model:(cc||ll)?'seekvera-r76-local-action-fallback':d.model,fastPath:(cc||ll)?'r76-deterministic-action-fallback':(d.fastPath||'r76-base-fallback'),liveData:!!d.liveData},fallback.status||200)
}

async function runStructured(env,body){
 const message=clean(body?.message??body?.prompt,2400);if(!message)return null;
 const selected=clean(body?.country,120)||'Worldwide',history=historyText(body?.history);
 const system=`You are SEEKVERA AI, the action assistant inside a worldwide marketplace and discovery app. You must understand the LATEST USER MESSAGE directly, including dialects, slang, Lebanese Arabic, mixed Arabic/English, transliteration, and any major world language. Never choose the reply language from the selected country, interface, or browser. Reply in the SAME language and script as the latest user message unless the user explicitly requests another reply language.\n\nReturn ONLY one JSON object with exactly these keys: reply, languageCode, category, countryAction, languageAction.\n- reply: a natural, concise, useful answer that appears BEFORE any app action. Do not merely say you will help; actually answer what you can.\n- languageCode: best ISO language code for the latest user message.\n- category: exactly one of ${[...CATS].join(', ')}. Choose general when no app section is relevant.\n- countryAction: ISO-3166 alpha-2 code, or WW, ONLY when the user explicitly commands the SEEKVERA APP/MARKET/COUNTRY SELECTOR to change/switch/move/set. Leave empty when the user merely searches for something in a country.\n- languageAction: supported language code ONLY when the user explicitly commands the app/interface language to change. Leave empty otherwise.\n\nAction examples: “حطني تركيا” => countryAction TR. “change the app to France” => FR. “حوّلني ورلد وايد” => WW. “حطلي تركي” when clearly asking app language => languageAction tr. “بدي فندق بفرنسا” is a search, NOT a country action. “I need a job in Germany” is jobs, NOT a country action.\nSelected market: ${selected}.\nConversation history:\n${history||'(none)'}\nLatest user message: ${message}`;
 const messages=[{role:'system',content:system},{role:'user',content:message}];
 for(const model of [PRIMARY,FALLBACK]){try{const r=await env.AI.run(model,{messages,temperature:.1,max_tokens:520});const text=modelText(r),obj=parseJSON(text);if(!obj||!clean(obj.reply,5000))continue;const language=languageCode(obj.languageCode)||'en',cat=category(obj.category),cc=countryCode(obj.countryAction),ll=languageCode(obj.languageAction);return{ok:true,response:clean(obj.reply,5000),language,category:cat,route:ROUTES[cat]||ROUTES.general,countryAction:cc?{type:'set-country',code:cc}:null,languageAction:ll?{type:'set-language',code:ll}:null,model,fastPath:'r76-single-structured-ai',liveData:false}}catch{}}
 return null;
}

export default{async fetch(request,env,ctx){
 const u=new URL(request.url);
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers:headers(request)});
 if(u.pathname==='/api/health'){
   const r=await baseWorker.fetch(request,env,ctx);let d={};try{d=await r.clone().json()}catch{}return json(request,{...d,r76:true,r76Runtime:'single-structured-multilingual-ai',r76Voice:'server-auto-asr-first',r76Locale:'complete-static-pack-audit',r76Fallback:'deterministic-actions-over-base-fallback'});
 }
 if(u.pathname==='/api/ai'&&request.method==='POST'){
   let body={};try{body=await request.clone().json()}catch{return json(request,{ok:false,error:'Invalid JSON'},400)}
   const message=clean(body?.message??body?.prompt,2400);if(!message)return json(request,{ok:false,error:'Message is required'},400);
   const reason=blocked(message);if(reason)return json(request,{ok:true,blocked:true,reviewRequired:true,response:'SEEKVERA cannot help buy, sell, source or promote prohibited or illegal items or services.',reason,category:'general',route:ROUTES.general,countryAction:null,languageAction:null,model:'seekvera-r76-safety'},200);
   if(env.AI){const d=await runStructured(env,body);if(d)return json(request,d,200)}
   return degradedFallback(request,env,ctx,body,message);
 }
 return baseWorker.fetch(request,env,ctx);
}};
