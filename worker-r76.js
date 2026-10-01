import baseWorker from './worker-r31.js';

const RELEASE='20261001-r125-dialect-voice-quality';
const PRIMARY='@cf/zai-org/glm-4.7-flash';
const FALLBACK='@cf/qwen/qwen3-30b-a3b-fp8';
const FAST='@cf/meta/llama-3.1-8b-instruct-fast';
const ASR_PRIMARY='@cf/openai/whisper-large-v3-turbo',ASR_FALLBACK='@cf/openai/whisper';
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
function historyText(h){if(!Array.isArray(h))return'';return h.slice(-18).map(x=>`${x?.role==='assistant'?'assistant':'user'}: ${clean(x?.content,1000)}`).filter(Boolean).join('\n').slice(-10000)}

const LANGUAGE_NAMES={english:'en',arabic:'ar',french:'fr',chinese:'zh',spanish:'es',hindi:'hi',portuguese:'pt',german:'de',japanese:'ja',korean:'ko',indonesian:'id',turkish:'tr',russian:'ru',urdu:'ur',bengali:'bn',vietnamese:'vi',italian:'it',swahili:'sw',thai:'th',persian:'fa',polish:'pl',dutch:'nl',malay:'ms',filipino:'fil',hausa:'ha',yoruba:'yo',igbo:'ig',amharic:'am',hebrew:'he',greek:'el',ukrainian:'uk',romanian:'ro',czech:'cs',slovak:'sk',hungarian:'hu',swedish:'sv',norwegian:'no',danish:'da',finnish:'fi',bulgarian:'bg',croatian:'hr',serbian:'sr',slovenian:'sl',lithuanian:'lt',latvian:'lv',estonian:'et',catalan:'ca',basque:'eu',galician:'gl',icelandic:'is',albanian:'sq',macedonian:'mk',georgian:'ka',armenian:'hy',azerbaijani:'az',kazakh:'kk',uzbek:'uz',kyrgyz:'ky',tajik:'tg',turkmen:'tk',nepali:'ne',sinhala:'si',tamil:'ta',telugu:'te',malayalam:'ml',marathi:'mr',gujarati:'gu',punjabi:'pa',khmer:'km',lao:'lo',burmese:'my',mongolian:'mn',zulu:'zu',afrikaans:'af',belarusian:'be',bosnian:'bs',dzongkha:'dz',tigrinya:'ti',faroese:'fo',greenlandic:'kl',kalaallisut:'kl',kinyarwanda:'rw',samoan:'sm',tongan:'to',somali:'so',pashto:'ps',divehi:'dv',maltese:'mt',malagasy:'mg',irish:'ga',welsh:'cy',maori:'mi',frisian:'fy',luxembourgish:'lb',romansh:'rm',kurdish:'ku',xhosa:'xh',sotho:'st',tswana:'tn'};
function normalizedLanguage(v,message=''){
 const direct=languageCode(v);if(direct)return direct;
 const n=clean(v,80).toLowerCase();if(LANGUAGE_NAMES[n])return LANGUAGE_NAMES[n];
 const t=String(message||'');if(/[\u0600-\u06ff]/u.test(t))return'ar';if(/[\u3040-\u30ff]/u.test(t))return'ja';if(/[\u4e00-\u9fff]/u.test(t))return'zh';if(/[\uac00-\ud7af]/u.test(t))return'ko';if(/[\u0900-\u097f]/u.test(t))return'hi';if(/[\u0590-\u05ff]/u.test(t))return'he';return'en';
}
function messageLanguage(message,suggested=''){
 const t=String(message||''),s=t.toLowerCase(),q=languageCode(suggested);
 const pick=(list,def)=>q&&list.includes(q)?q:def;
 // Script-first detection. Preserve a trustworthy model/ASR hint inside scripts shared by multiple languages.
 if(/[\u0600-\u06ff]/u.test(t))return pick(['ar','fa','ur','ps','ku'],'ar');
 if(/[\u0900-\u097f]/u.test(t))return pick(['hi','mr','ne'],'hi');
 if(/[\u0980-\u09ff]/u.test(t))return pick(['bn'],'bn');
 if(/[\u0a00-\u0a7f]/u.test(t))return pick(['pa'],'pa');
 if(/[\u0a80-\u0aff]/u.test(t))return pick(['gu'],'gu');
 if(/[\u0b80-\u0bff]/u.test(t))return pick(['ta'],'ta');
 if(/[\u0c00-\u0c7f]/u.test(t))return pick(['te'],'te');
 if(/[\u0d00-\u0d7f]/u.test(t))return pick(['ml'],'ml');
 if(/[\u0d80-\u0dff]/u.test(t))return pick(['si'],'si');
 if(/[\u0e00-\u0e7f]/u.test(t))return'th';
 if(/[\u0e80-\u0eff]/u.test(t))return'lo';
 if(/[\u1000-\u109f]/u.test(t))return'my';
 if(/[\u1200-\u137f]/u.test(t))return pick(['am','ti'],'am');
 if(/[\u1780-\u17ff]/u.test(t))return'km';
 if(/[\u10a0-\u10ff]/u.test(t))return'ka';
 if(/[\u0530-\u058f]/u.test(t))return'hy';
 if(/[\u0370-\u03ff]/u.test(t))return'el';
 if(/[\u0590-\u05ff]/u.test(t))return'he';
 if(/[\u3040-\u30ff]/u.test(t))return'ja';
 if(/[\uac00-\ud7af]/u.test(t))return'ko';
 if(/[\u4e00-\u9fff]/u.test(t))return pick(['zh','ja'],'zh');
 if(/[\u0400-\u052f]/u.test(t))return pick(['ru','uk','bg','sr','mk','be'],'ru');
 // Strong Latin-script clues. If there is no clue, use the model/ASR hint rather than guessing English.
 if(/[ğışİ]/u.test(t)||/\b(merhaba|nasılsın|nasilsin|istiyorum|arıyorum|ariyorum|otel|ülke|ulke|değiş|degis)\b/iu.test(s))return'tr';
 if(/[đơư]/iu.test(t)||/(xin chào|cảm ơn|sân bay|tôi muốn|tôi cần)/iu.test(s))return'vi';
 if(/[ąćęłńśźż]/iu.test(t))return'pl';
 if(/[őű]/iu.test(t))return'hu';
 if(/[ăîșşțţ]/iu.test(t))return'ro';
 if(s.includes('olá')||/[ãõ]/iu.test(t)||/\b(ola|preciso|procuro|obrigado|obrigada|aeroporto|perto)\b/iu.test(s))return'pt';
 if(/[ñ¿¡]/iu.test(t)||/\b(hola|quiero|busco|necesito|gracias|país|pais|idioma)\b/iu.test(s))return'es';
 if(/[äöüß]/iu.test(t)||/\b(hallo|ich|suche|möchte|mochte|sprache|land|danke)\b/iu.test(s))return'de';
 if(/\b(bonjour|salut|merci|cherche|voudrais|besoin|langue|pays|aéroport|aeroport|près|passe|aide|trouve|allemagne)\b|l[’']application/iu.test(s))return'fr';
 if(/\b(ciao|buongiorno|grazie|cerco|voglio|bisogno|lingua|paese|albergo)\b/iu.test(s))return'it';
 if(/\b(hallo|dank|zoek|nodig|taal|land|hotel)\b/iu.test(s)&&q==='nl')return'nl';
 if(/\b(habari|asante|nataka|nahitaji|tafuta|hoteli)\b/iu.test(s))return'sw';
 if(/\b(selamat|terima kasih|saya|ingin|cari|butuh|bandara|dekat)\b/iu.test(s))return pick(['id','ms'],'id');
 if(/\b(hello|hi|hey|how are you|i need|i want|i am looking|i'm looking|can you help|please help|thank you|thanks|what kind|which city|near the airport|change the app|switch the app|change country|switch country|take me to)\b/iu.test(s))return'en';
 return q||'en';
}
function aliasHit(s,a){a=String(a).toLowerCase();if(/^[a-z]{1,3}$/i.test(a))return new RegExp(`(?:^|[^a-z])${a.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}(?:$|[^a-z])`,'i').test(s);return s.includes(a)}
const COUNTRY_ALIASES={
 WW:['worldwide','global','all countries','كل الدول','كل العالم','العالم كله','ورلد وايد','وورلد وايد','عالمي'],
 TR:['turkey','türkiye','turkiye','تركيا'],LB:['lebanon','لبنان'],FR:['france','فرنسا'],NG:['nigeria','نيجيريا'],DE:['germany','deutschland','ألمانيا','المانيا'],US:['united states','usa','america','أمريكا','امريكا'],GB:['united kingdom','britain','england','uk','بريطانيا','إنجلترا','انجلترا'],AE:['united arab emirates','uae','emirates','الإمارات','الامارات'],SA:['saudi arabia','saudi','السعودية'],QA:['qatar','قطر'],CA:['canada','كندا'],AU:['australia','أستراليا','استراليا'],EG:['egypt','مصر'],SY:['syria','سوريا'],JO:['jordan','الأردن','الاردن'],KE:['kenya','كينيا'],IN:['india','الهند'],CN:['china','الصين'],JP:['japan','اليابان'],RU:['russia','روسيا'],BR:['brazil','البرازيل'],ES:['spain','إسبانيا','اسبانيا'],IT:['italy','إيطاليا','ايطاليا'],NL:['netherlands','holland','هولندا'],CH:['switzerland','سويسرا'],SE:['sweden','السويد'],NO:['norway','النرويج'],DK:['denmark','الدنمارك'],FI:['finland','فنلندا'],ZA:['south africa','جنوب أفريقيا','جنوب افريقيا'],GH:['ghana','غانا'],MA:['morocco','المغرب'],DZ:['algeria','الجزائر'],TN:['tunisia','تونس']
};
const ISO_CODES=`AF AL DZ AS AD AO AI AQ AG AR AM AW AU AT AZ BS BH BD BB BY BE BZ BJ BM BT BO BQ BA BW BV BR IO BN BG BF BI CV KH CM CA KY CF TD CL CN CX CC CO KM CD CG CK CR CI HR CU CW CY CZ DK DJ DM DO EC EG SV GQ ER EE SZ ET FK FO FJ FI FR GF PF TF GA GM GE DE GH GI GR GL GD GP GU GT GG GN GW GY HT HM VA HN HK HU IS IN ID IR IQ IE IM IL IT JM JP JE JO KZ KE KI KP KR KW KG LA LV LB LS LR LY LI LT LU MO MG MW MY MV ML MT MH MQ MR MU YT MX FM MD MC MN ME MS MA MZ MM NA NR NP NL NC NZ NI NE NG NU NF MK MP NO OM PK PW PS PA PG PY PE PH PN PL PT PR QA RE RO RU RW BL SH KN LC MF PM VC WS SM ST SA SN RS SC SL SG SX SK SI SB SO ZA GS SS ES LK SD SR SJ SE CH SY TW TJ TZ TH TL TG TK TO TT TN TR TM TC TV UG UA AE GB UM US UY UZ VU VE VN VG VI WF EH YE ZM ZW`.split(' ');
const LANGUAGE_ALIASES={
 tr:['turkish','türkçe','turkce','تركي','التركية'],ar:['arabic','عربي','العربية'],en:['english','انجليزي','إنجليزي','انكليزي','إنكليزي'],fr:['french','français','francais','فرنسي','الفرنسية'],de:['german','deutsch','ألماني','الماني','الألمانية'],es:['spanish','español','espanol','إسباني','اسباني'],zh:['chinese','中文','صيني','الصينية'],ja:['japanese','日本語','ياباني','اليابانية'],hi:['hindi','हिन्दी','हिंदी','هندي'],ru:['russian','русский','روسي','الروسية'],pt:['portuguese','português','برتغالي'],it:['italian','italiano','إيطالي','ايطالي'],nl:['dutch','nederlands','هولندي'],ko:['korean','한국어','كوري'],id:['indonesian','bahasa indonesia','إندونيسي','اندونيسي'],ur:['urdu','اردو','أردو']
};
function controlVerb(s){return /(?:\b(?:change|switch|set|select)\b.{0,28}\b(?:app|application|country|market|region|language)\b|\b(?:change|switch|set)\b.{0,24}\bto\b|حط(?:ني|لي)?|غي(?:ر|ّر)|حو(?:ل|ّل)|بد(?:ل|ّل)|انقل(?:ني)?|غيرلي|غير لي|حوّلني|حولني|cambia.{0,25}(?:app|pa[ií]s|idioma)|(?:changez|passe|passer|mets|mettre).{0,25}(?:application|pays|langue)|wechsel.{0,25}(?:app|land|sprache)|(?:uygulama|ülke|dil).{0,25}değiş|(?:приложение|стран|язык).{0,25}(?:смен|измен)|(?:应用|国家|语言).{0,12}(?:切换|更改|改))/iu.test(s)}
function languageIntent(s){return /language|لغة|langue|sprache|idioma|lingua|(?:^|\W)dil(?:i)?(?:\W|$)|язык|语言|語言|言語|भाषा/iu.test(s)}
function findAliasCode(s,map){let hits=[];for(const[code,aliases]of Object.entries(map))for(const a of aliases)if(aliasHit(s,a))hits.push([a.length,code]);hits.sort((a,b)=>b[0]-a[0]);return hits[0]?.[1]||''}
function anyCountryCode(s){const direct=findAliasCode(s,COUNTRY_ALIASES);if(direct)return direct;for(const locale of [...new Set(['en',messageLanguage(s,'en')])])try{const dn=new Intl.DisplayNames([locale],{type:'region'});for(const code of ISO_CODES){const n=String(dn.of(code)||'').toLowerCase();if(n&&n!==code.toLowerCase()&&aliasHit(s,n))return code}}catch{}return''}
function anyLanguageCode(s){const direct=findAliasCode(s,LANGUAGE_ALIASES);if(direct)return direct;let hits=[];for(const[name,code]of Object.entries(LANGUAGE_NAMES))if(aliasHit(s,name))hits.push([name.length,code]);hits.sort((a,b)=>b[0]-a[0]);return hits[0]?.[1]||''}
function explicitLanguageAction(message){const s=String(message||'').toLowerCase();if(!controlVerb(s))return'';const code=anyLanguageCode(s);if(!code)return'';if(languageIntent(s))return code;if(/[\u0600-\u06ff]/u.test(s)&&/(حط(?:لي|ني)?|غي(?:ر|ّر)|حو(?:ل|ّل)|بد(?:ل|ّل))/u.test(s)&&!anyCountryCode(s))return code;return''}
function explicitCountryAction(message){const s=String(message||'').toLowerCase();if(!controlVerb(s))return'';return anyCountryCode(s)}
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
  ja:{country:'了解しました。アプリを指定された国に切り替えます。',language:'了解しました。アプリの言語を変更します。'},
  ko:{country:'알겠습니다. 앱을 요청하신 국가로 변경합니다.',language:'알겠습니다. 앱 언어를 변경합니다.'},
  hi:{country:'समझ गया। अब ऐप को आपके चुने हुए देश पर बदल रहा हूँ।',language:'समझ गया। अब ऐप की भाषा बदल रहा हूँ।'},
  pt:{country:'Entendido. Vou mudar o aplicativo para o país solicitado agora.',language:'Entendido. Vou mudar o idioma do aplicativo agora.'},
  it:{country:'Capito. Ora imposto l’app sul Paese richiesto.',language:'Capito. Ora cambio la lingua dell’app.'},
  id:{country:'Baik. Saya akan mengubah aplikasi ke negara yang Anda minta sekarang.',language:'Baik. Saya akan mengubah bahasa aplikasi sekarang.'},
  th:{country:'เข้าใจแล้ว ตอนนี้ฉันจะเปลี่ยนแอปเป็นประเทศที่คุณขอ',language:'เข้าใจแล้ว ตอนนี้ฉันจะเปลี่ยนภาษาของแอป'},
  sw:{country:'Nimeelewa. Sasa ninabadilisha programu kwenda nchi uliyoomba.',language:'Nimeelewa. Sasa ninabadilisha lugha ya programu.'},
  ur:{country:'سمجھ گیا۔ اب ایپ کو آپ کے منتخب کردہ ملک پر تبدیل کر رہا ہوں۔',language:'سمجھ گیا۔ اب ایپ کی زبان تبدیل کر رہا ہوں۔'},
  fa:{country:'متوجه شدم. اکنون برنامه را به کشور درخواستی تغییر می‌دهم.',language:'متوجه شدم. اکنون زبان برنامه را تغییر می‌دهم.'},
  bn:{country:'বুঝেছি। এখন অ্যাপটি আপনার চাওয়া দেশে পরিবর্তন করছি।',language:'বুঝেছি। এখন অ্যাপের ভাষা পরিবর্তন করছি।'},
  vi:{country:'Đã hiểu. Tôi sẽ chuyển ứng dụng sang quốc gia bạn yêu cầu ngay.',language:'Đã hiểu. Tôi sẽ đổi ngôn ngữ ứng dụng ngay.'}
 };
 return(r[lang]||r.en)[kind];
}
function actionState(message,modelCC='',modelLL='',clientControls={}){
 const s=String(message||'').toLowerCase(),isControl=controlVerb(s),wantsLanguage=languageIntent(s);
 const localCC=explicitCountryAction(message)||(isControl?countryCode(clientControls?.country):''),localLL=explicitLanguageAction(message)||(isControl?languageCode(clientControls?.language):'');
 const cc=localCC||((isControl&&!wantsLanguage)?countryCode(modelCC):'');
 const ll=localLL||((isControl&&wantsLanguage)?languageCode(modelLL):'');
 return{cc,ll,isAction:!!(cc||ll)};
}
function arabicDialect(message,history=[]){
 const detect=t=>{
  t=String(t||'');
  if(/(?:^|[^\p{L}])(?:لبناني|لبنانية|لبنانيه|باللبناني|شامي|شامية|شو|كيفك|هلق|هلأ|بدي|بدّي|فيني|معي|عم بحكي|عم تحكي|رح|خلص)(?=$|[^\p{L}])/u.test(t))return'levantine';
  if(/(?:مصري|مصرية|بالمصري|عايز|عاوز|إزاي|ازاي|دلوقتي|مش عارف|كده|كدا)/u.test(t))return'egyptian';
  if(/(?:^|[^\p{L}])(?:خليجي|بالخليجي|وش|شلون|أبي|ابي|أبغى|ابغى|الحين|وايد)(?=$|[^\p{L}])/u.test(t))return'gulf';
  if(/(?:مغربي|دارجة|بالدارجة|بغيت|بزاف|دابا|واش)/u.test(t))return'maghrebi';
  if(/(?:بالفصحى|فصحى|الفصحى)/u.test(t))return'formal';
  return''
 };
 const current=detect(message);if(current)return current;
 for(const x of (Array.isArray(history)?history:[]).slice(-8).reverse())if(x?.role==='user'){const d=detect(x.content);if(d)return d}
 return'formal'
}
function dialectRouteReply(message,history=[]){
 const d=arabicDialect(message,history);
 return {levantine:'أكيد، عم بفتحلك القسم اللي بدك ياه.',egyptian:'تمام، هفتحلك القسم اللي إنت عايزه دلوقتي.',gulf:'أبشر، بفتح لك القسم اللي تبيه الحين.',maghrebi:'واخا، غادي نحل ليك القسم اللي بغيتي.',formal:'بالتأكيد، أفتح لك القسم المناسب الآن.'}[d]
}
function routeReplyFor(language,message,history=[]){return language==='ar'?dialectRouteReply(message,history):fastRouteReply(language)}
function speechLocaleFor(language,message,history=[]){if(language!=='ar')return language;return {levantine:'ar-LB',egyptian:'ar-EG',gulf:'ar-SA',maghrebi:'ar-MA',formal:'ar'}[arabicDialect(message,history)]}

function conversationOnly(message){const s=String(message||'').trim().toLowerCase().replace(/^[\s¿¡]+|[\s.!?؟،。！？]+$/gu,'');if(!s)return true;if(/(?:مرحبا|مرحباً|أهلا|اهلا|السلام عليكم)[\s،,.!?؟-]*(?:كيفك|كيف حالك)(?:\s+اليوم)?/iu.test(s))return true;if(/^(?:(?:hi|hello|hey)\s*,?\s*)?how\s+are\s+you(?:\s+today)?$|^(?:(?:مرحبا|مرحباً|أهلا|اهلا)\s*,?\s*)?(?:كيفك|كيف حالك)(?:\s+اليوم)?$/iu.test(s))return true;return /^(?:hi|hello|hey|good\s+(?:morning|afternoon|evening)|how\s+are\s+you(?:\s+today)?|what\s+are\s+you\s+doing|what(?:'s|\s+is)\s+your\s+name|who\s+are\s+you|thank\s*you|thanks|مرحبا|مرحباً|أهلا|اهلا|السلام عليكم|كيفك(?:\s+اليوم)?|كيف حالك(?:\s+اليوم)?|شو عم تعمل|شو الاخبار|مين انت|شكرا|شكراً|bonjour|salut|comment (?:ça|ca) va|merci|hola|buenos días|buenas tardes|cómo estás|como estas|gracias|hallo|guten morgen|wie geht(?:'s| es dir)?|danke|ciao|buongiorno|come stai|grazie|olá|ola|bom dia|como vai|obrigad[oa]|merhaba|nasılsın|nasilsin|teşekkürler|tesekkurler|привет|здравствуй(?:те)?|как дела|спасибо|你好|您好|你好吗|谢谢|こんにちは|おはよう|元気ですか|ありがとう|안녕|안녕하세요|어떻게 지내|감사합니다|नमस्ते|आप कैसे हैं|धन्यवाद|สวัสดี|เป็นอย่างไรบ้าง|ขอบคุณ|halo|apa kabar|terima kasih|jambo|habari|asante)$/iu.test(s)}
function metaConversation(message){
 const s=String(message||'').toLowerCase();
 return /(?:\b(?:i am|i'm|im|you are|you're|are you|can you|do you)\b.{0,45}\b(?:speaking|speak|understand|hear|listening|language|voice|arabic|english|french|turkish|spanish|german)\b)|(?:(?:أنا|انا|إنت|انت|عم|صرت|صار|هلأ|هلق|هون|هنا).{0,45}(?:بحكي|بتحكي|احكي|تفهم|بتفهم|سامع|تسمع|صوت|لغة|عربي|العربي|إنجليزي|انجليزي|فرنسي|تركي))|(?:parle|parles|comprends|écoute|langue).{0,30}(?:français|arabe|anglais|langue)?|(?:sprich|versteh|sprache).{0,30}|(?:habla|hablas|entiend|idioma).{0,30}|(?:konuş|anlıyor|anliyor|dil).{0,30}|(?:говор|понима|язык).{0,30}|(?:说|听懂|语言)|(?:話|言語)|(?:말|이해|언어)/iu.test(s)
}
function metaReply(message,language){
 const l=languageCode(language)||messageLanguage(message,'');
 const r={
  ar:'إيه، فهمتك. فيك تحكي معي بالعربي أو بأي لغة بشكل طبيعي، وما رح حوّلك على أي قسم إلا لما تطلب شي محدد.',
  en:'Yes, I understand you. Speak naturally in any language; I’ll stay in the conversation until you ask for something specific.',
  fr:'Oui, je vous comprends. Parlez naturellement dans n’importe quelle langue ; je resterai dans la conversation jusqu’à ce que vous demandiez quelque chose de précis.',
  es:'Sí, te entiendo. Habla con naturalidad en cualquier idioma; seguiré conversando hasta que pidas algo concreto.',
  de:'Ja, ich verstehe dich. Sprich ganz natürlich in jeder Sprache; ich bleibe im Gespräch, bis du etwas Bestimmtes möchtest.',
  tr:'Evet, seni anlıyorum. İstediğin dilde doğal konuş; belirli bir şey isteyene kadar sohbet içinde kalacağım.',
  ru:'Да, я вас понимаю. Говорите естественно на любом языке; я останусь в разговоре, пока вы не попросите что-то конкретное.',
  zh:'可以，我听得懂。你可以自然地用任何语言和我说话；只有当你提出明确需求时，我才会带你去相应栏目。',
  ja:'はい、理解できます。どの言語でも自然に話してください。具体的な依頼があるまでは会話を続けます。',
  ko:'네, 이해해요. 어떤 언어로든 자연스럽게 말씀하세요. 구체적인 요청을 하기 전까지는 대화를 계속할게요.',
  hi:'हाँ, मैं समझता हूँ। आप किसी भी भाषा में स्वाभाविक रूप से बोलें; जब तक आप कोई खास चीज़ नहीं माँगते, मैं बातचीत में ही रहूँगा।',
  pt:'Sim, eu entendo. Fale naturalmente em qualquer idioma; continuarei na conversa até você pedir algo específico.',
  it:'Sì, ti capisco. Parla naturalmente in qualsiasi lingua; resterò nella conversazione finché non chiederai qualcosa di specifico.'
 };
 return r[l]||r.en
}
function routeLikeReply(text){return /(?:take|send|move|route|redirect).{0,35}(?:section|department)|(?:section|department).{0,35}(?:now|direct)|(?:قسم|القسم).{0,35}(?:مباشر|الأنسب|المناسب|وديك|أوصلك|انقلك|أنقلك)/iu.test(String(text||''))}
function employmentIntent(message){const s=String(message||'').toLowerCase();return /\b(?:job|jobs|career|vacancy|employment|hiring|job opening|looking for work|need work|find work)\b|وظيف|وظائف|وظايف|فرصة عمل|أبحث عن عمل|ابحث عن عمل|عم دور على شغل|عم بدور على شغل|بدي شغل|بدور على شغل|ندور على شغل|دورلي على شغل|دوريني على شغل|نوريني على شغل|وريني شغل|شوفلي شغل|ساعدني دور على شغل|ساعديني دور على شغل|ساعديني ندور على شغل|دوام|emploi|emplois|travail|trabajo|empleo|trabalho|emprego|lavoro|arbeit|stellen|stelle|iş ilanı|is ilanı|ваканси|работу ищ|नौकरी|रोजगार|काम ढूँढ|काम खोज|工作|职位|求人|채용/iu.test(s)}
function conversationalFallback(message,language){const l=languageCode(language)||normalizedLanguage('',message);const how=/how\s+are\s+you|كيفك|كيف حالك|comment (?:ça|ca) va|cómo estás|como estas|wie geht|come stai|como vai|nasılsın|nasilsin|как дела|你好吗|元気ですか|어떻게 지내|आप कैसे हैं|เป็นอย่างไรบ้าง|apa kabar|habari/iu.test(message);const replies={
 ar:how?'منيح، شكراً إلك. أنا جاهز أحكي معك وأساعدك. شو حابب تعمل؟':'أهلاً وسهلاً! أنا SEEKVERA AI. احكي معي بشكل طبيعي، شو فيني ساعدك؟',
 en:how?'I’m doing well, thank you. I’m here and ready to help—what would you like to do?':'Hello! I’m SEEKVERA AI. Talk to me naturally—how can I help?',
 fr:how?'Je vais bien, merci. Je suis prêt à vous aider. Que souhaitez-vous faire ?':'Bonjour ! Je suis SEEKVERA AI. Comment puis-je vous aider ?',
 es:how?'Estoy bien, gracias. Estoy aquí para ayudarte. ¿Qué te gustaría hacer?':'¡Hola! Soy SEEKVERA AI. ¿Cómo puedo ayudarte?',
 de:how?'Mir geht es gut, danke. Ich bin bereit zu helfen. Was möchten Sie tun?':'Hallo! Ich bin SEEKVERA AI. Wie kann ich helfen?',
 tr:how?'İyiyim, teşekkür ederim. Yardım etmeye hazırım. Ne yapmak istersiniz?':'Merhaba! Ben SEEKVERA AI. Size nasıl yardımcı olabilirim?',
 zh:how?'我很好，谢谢。我随时可以帮助你。你想做什么？':'你好！我是 SEEKVERA AI。请自然地告诉我你需要什么帮助。',
 ja:how?'元気です、ありがとう。お手伝いできます。何をしたいですか？':'こんにちは！SEEKVERA AIです。どのようにお手伝いできますか？',
 ko:how?'잘 지내요, 감사합니다. 무엇을 도와드릴까요?':'안녕하세요! SEEKVERA AI입니다. 무엇을 도와드릴까요?',
 hi:how?'मैं ठीक हूँ, धन्यवाद। मैं आपकी मदद के लिए तैयार हूँ। आप क्या करना चाहते हैं?':'नमस्ते! मैं SEEKVERA AI हूँ। मैं आपकी कैसे मदद कर सकता हूँ?',
 ru:how?'У меня всё хорошо, спасибо. Я готов помочь. Что вы хотите сделать?':'Здравствуйте! Я SEEKVERA AI. Чем я могу помочь?',
 th:how?'ฉันสบายดี ขอบคุณ พร้อมช่วยคุณ คุณต้องการทำอะไร?':'สวัสดี! ฉันคือ SEEKVERA AI ให้ฉันช่วยอะไรได้บ้าง?',
 id:how?'Saya baik, terima kasih. Saya siap membantu. Apa yang ingin Anda lakukan?':'Halo! Saya SEEKVERA AI. Ada yang bisa saya bantu?',
 sw:how?'Niko vizuri, asante. Niko tayari kusaidia. Ungependa kufanya nini?':'Jambo! Mimi ni SEEKVERA AI. Ninaweza kukusaidiaje?'
 };return replies[l]||replies.en}
function usefulFallback(message,language,cat){const l=languageCode(language)||messageLanguage(message,'');if(cat&&cat!=='general')return fastRouteReply(l)||'✓';const r={
 ar:'ما فهمت قصدك من هالجملة. شو الشي اللي بدك تلاقيه؟',
 en:'I understand what you need. Tell me one useful detail such as the city, date or budget, and I’ll continue and show the right section only when your request is clear.',
 fr:'Je comprends votre demande. Donnez-moi un détail utile, comme la ville, la date ou le budget, et je continuerai avant d’ouvrir la bonne section.',
 es:'Entiendo lo que necesitas. Dime un dato útil, como la ciudad, la fecha o el presupuesto, y continuaré antes de abrir la sección adecuada.',
 de:'Ich verstehe Ihre Anfrage. Nennen Sie mir ein wichtiges Detail wie Stadt, Datum oder Budget; danach helfe ich weiter und öffne nur den passenden Bereich.',
 tr:'Ne istediğinizi anladım. Şehir, tarih veya bütçe gibi önemli bir ayrıntı söyleyin; ardından devam edip yalnızca uygun bölümü göstereceğim.',
 zh:'我明白你的需求。请告诉我一个重要细节，例如城市、日期或预算；我会继续帮助你，并只在需求明确后显示合适的栏目。',
 ja:'ご希望は分かりました。都市、日付、予算など重要な詳細を一つ教えてください。内容が明確になってから適切なセクションをご案内します。',
 ko:'요청을 이해했습니다. 도시, 날짜, 예산 같은 중요한 정보 하나를 알려 주세요. 요청이 명확해진 뒤에만 알맞은 섹션을 보여 드릴게요.',
 hi:'मैं आपकी ज़रूरत समझ गया। शहर, तारीख या बजट जैसी एक उपयोगी जानकारी बताइए; अनुरोध स्पष्ट होने पर ही मैं सही सेक्शन दिखाऊँगा।',
 ru:'Я понял ваш запрос. Укажите одну важную деталь — город, дату или бюджет; после уточнения я продолжу и покажу подходящий раздел.',
 pt:'Entendi o que você precisa. Diga um detalhe útil, como cidade, data ou orçamento; continuarei e só mostrarei a seção certa quando o pedido estiver claro.',
 it:'Ho capito la richiesta. Indicami un dettaglio utile, come città, data o budget; continuerò e mostrerò la sezione giusta solo quando sarà chiaro.',
 id:'Saya memahami kebutuhan Anda. Beri satu detail penting seperti kota, tanggal, atau anggaran; saya akan lanjut dan hanya membuka bagian yang tepat setelah jelas.',
 th:'ฉันเข้าใจสิ่งที่คุณต้องการ โปรดบอกรายละเอียดสำคัญหนึ่งอย่าง เช่น เมือง วันที่ หรืองบประมาณ แล้วฉันจะช่วยต่อและแสดงหมวดที่เหมาะสมเมื่อคำขอชัดเจน',
 sw:'Nimeelewa unachohitaji. Nipe jambo moja muhimu kama mji, tarehe au bajeti; nitaendelea na kuonyesha sehemu sahihi baada ya ombi kuwa wazi.',
 ur:'میں آپ کی ضرورت سمجھ گیا ہوں۔ شہر، تاریخ یا بجٹ جیسی ایک اہم تفصیل بتائیں؛ درخواست واضح ہونے پر ہی میں درست سیکشن دکھاؤں گا۔',
 fa:'درخواست شما را فهمیدم. یک جزئیات مهم مثل شهر، تاریخ یا بودجه بگویید؛ بعد از روشن شدن درخواست، بخش مناسب را نشان می‌دهم.',
 bn:'আমি আপনার প্রয়োজন বুঝেছি। শহর, তারিখ বা বাজেটের মতো একটি গুরুত্বপূর্ণ তথ্য দিন; অনুরোধ পরিষ্কার হলে আমি সঠিক বিভাগ দেখাব।',
 vi:'Tôi hiểu nhu cầu của bạn. Hãy cho tôi một chi tiết quan trọng như thành phố, ngày hoặc ngân sách; tôi sẽ tiếp tục và chỉ mở mục phù hợp khi yêu cầu đã rõ.'
 };return r[l]||r.en}

function replyScript(text){
 const t=String(text||'');
 if(/[\u0600-\u06ff]/u.test(t))return'arabic';
 if(/[\u0900-\u097f]/u.test(t))return'devanagari';
 if(/[\u0980-\u09ff]/u.test(t))return'bengali';
 if(/[\u0a00-\u0a7f]/u.test(t))return'gurmukhi';
 if(/[\u0a80-\u0aff]/u.test(t))return'gujarati';
 if(/[\u0b80-\u0bff]/u.test(t))return'tamil';
 if(/[\u0c00-\u0c7f]/u.test(t))return'telugu';
 if(/[\u0d00-\u0d7f]/u.test(t))return'malayalam';
 if(/[\u0d80-\u0dff]/u.test(t))return'sinhala';
 if(/[\u0e00-\u0e7f]/u.test(t))return'thai';
 if(/[\u0e80-\u0eff]/u.test(t))return'lao';
 if(/[\u1000-\u109f]/u.test(t))return'myanmar';
 if(/[\u1200-\u137f]/u.test(t))return'ethiopic';
 if(/[\u1780-\u17ff]/u.test(t))return'khmer';
 if(/[\u10a0-\u10ff]/u.test(t))return'georgian';
 if(/[\u0530-\u058f]/u.test(t))return'armenian';
 if(/[\u0370-\u03ff]/u.test(t))return'greek';
 if(/[\u0590-\u05ff]/u.test(t))return'hebrew';
 if(/[\u3040-\u30ff]/u.test(t))return'japanese';
 if(/[\uac00-\ud7af]/u.test(t))return'korean';
 if(/[\u4e00-\u9fff]/u.test(t))return'han';
 if(/[\u0400-\u052f]/u.test(t))return'cyrillic';
 if(/[A-Za-zÀ-ÖØ-öø-ÿ]/u.test(t))return'latin';
 return''
}
function expectedReplyScripts(language){
 const l=languageCode(language);
 if(['ar','fa','ur','ps','ku'].includes(l))return['arabic'];
 if(['hi','mr','ne'].includes(l))return['devanagari'];
 if(l==='bn')return['bengali'];if(l==='pa')return['gurmukhi'];if(l==='gu')return['gujarati'];if(l==='ta')return['tamil'];if(l==='te')return['telugu'];if(l==='ml')return['malayalam'];if(l==='si')return['sinhala'];
 if(l==='th')return['thai'];if(l==='lo')return['lao'];if(l==='my')return['myanmar'];if(['am','ti'].includes(l))return['ethiopic'];if(l==='km')return['khmer'];if(l==='ka')return['georgian'];if(l==='hy')return['armenian'];if(l==='el')return['greek'];if(l==='he')return['hebrew'];
 if(l==='ja')return['japanese','han'];if(l==='zh')return['han'];if(l==='ko')return['korean'];if(['ru','uk','bg','sr','mk','be'].includes(l))return['cyrillic'];
 return['latin']
}
function confidentLatinLanguage(text){
 const t=' '+String(text||'').toLowerCase().replace(/[^a-zà-öø-ÿğışçñ¿¡ðþæœ]+/gu,' ')+' ';
 if(/[ðþ]/u.test(t)||/\b(hvað|þú|það|ertu|erum|leita|þarf|aðstoð|vinna|vinnu)\b/u.test(t))return'is';
 if(/[ğış]/u.test(t)||/\b(merhaba|nasılsın|istiyorum|arıyorum|havaalanı|yakın|teşekkür)\b/u.test(t))return'tr';
 if(/[ãõ]/u.test(t)||/\b(olá|obrigad|procuro|preciso|aeroporto|perto)\b/u.test(t))return'pt';
 if(/[ñ¿¡]/u.test(t)||/\b(hola|quiero|busco|necesito|gracias|aeropuerto|cerca)\b/u.test(t))return'es';
 if(/[äöüß]/u.test(t)||/\b(ich|suche|möchte|danke|flughafen|nähe)\b/u.test(t))return'de';
 if(/\b(bonjour|merci|cherche|voudrais|besoin|aéroport|près|comment allez)\b/u.test(t))return'fr';
 if(/\b(ciao|buongiorno|grazie|cerco|voglio|bisogno|aeroporto|vicino)\b/u.test(t))return'it';
 if(/[đơư]/u.test(t)||/\b(xin chào|cảm ơn|tôi muốn|tôi cần|sân bay)\b/u.test(t))return'vi';
 if(/\b(habari|asante|nataka|nahitaji|hoteli|uwanja wa ndege)\b/u.test(t))return'sw';
 if(/\b(selamat|terima kasih|saya ingin|saya perlu|bandara|dekat)\b/u.test(t))return'id';
 if(/\b(hello|thank you|i need|i want|i am looking|how are you|please tell me|what kind|can you help)\b/u.test(t))return'en';
 return''
}
function translationRequest(message){return /\btranslate\b|\btranslation\b|ترجم|ترجمة|ترجمي|traduire|traducción|traducir|übersetz|traduz|çevir|перевед|翻译|翻訳|번역/iu.test(String(message||''))}
function replyMatchesLanguage(reply,language,message=''){
 const text=clean(reply,5000),l=languageCode(language)||messageLanguage(message,'');if(!text)return false;
 if(translationRequest(message))return true;
 const script=replyScript(text),expected=expectedReplyScripts(l);
 if(script&&script!=='latin')return expected.includes(script);
 if(!expected.includes('latin'))return false;
 const guessed=confidentLatinLanguage(text);return !guessed||guessed===l
}
function guardedReply(reply,language,message=''){const text=clean(reply,5000);return replyMatchesLanguage(text,language,message)?text:''}
function languageSafeHistory(h,target){
 if(!Array.isArray(h))return'';
 return h.slice(-18).filter(x=>x?.role!=='assistant'||replyMatchesLanguage(x?.content,target,'')).map(x=>`${x?.role==='assistant'?'assistant':'user'}: ${clean(x?.content,1000)}`).filter(Boolean).join('\n').slice(-10000)
}

function safetyReply(language){const l=languageCode(language)||'en',r={ar:'لا يمكن لـSEEKVERA المساعدة في شراء أو بيع أو توفير أو ترويج مواد أو خدمات محظورة أو غير قانونية.',en:'SEEKVERA cannot help buy, sell, source or promote prohibited or illegal items or services.',fr:'SEEKVERA ne peut pas aider à acheter, vendre, fournir ou promouvoir des articles ou services interdits ou illégaux.',es:'SEEKVERA no puede ayudar a comprar, vender, conseguir o promocionar artículos o servicios prohibidos o ilegales.',de:'SEEKVERA kann nicht beim Kauf, Verkauf, Beschaffen oder Bewerben verbotener oder illegaler Waren oder Dienste helfen.',tr:'SEEKVERA yasaklı veya yasa dışı ürün ya da hizmetleri satın alma, satma, bulma veya tanıtma konusunda yardımcı olamaz.',zh:'SEEKVERA 无法协助购买、销售、获取或推广被禁止或非法的商品或服务。',ja:'SEEKVERAは、禁止または違法な商品・サービスの購入、販売、調達、宣伝を支援できません。',ko:'SEEKVERA는 금지되거나 불법인 상품 및 서비스의 구매, 판매, 조달 또는 홍보를 도울 수 없습니다.',hi:'SEEKVERA प्रतिबंधित या अवैध वस्तुओं अथवा सेवाओं को खरीदने, बेचने, मंगाने या बढ़ावा देने में सहायता नहीं कर सकता।',ru:'SEEKVERA не помогает покупать, продавать, искать или продвигать запрещённые либо незаконные товары и услуги.'};return r[l]||r.en}
async function transcribeAudio(request,env){
 if(!env.AI)return json(request,{ok:false,error:'Speech AI unavailable'},503);
 if(Number(request.headers.get('content-length')||0)>9*1024*1024)return json(request,{ok:false,error:'Audio request too large'},413);
 let b={};try{b=await request.json()}catch{return json(request,{ok:false,error:'Invalid audio request'},400)}
 const raw=String(b.audio||''),m=raw.match(/^data:(audio\/(?:webm|mp4|mpeg|wav|ogg|x-m4a|aac|3gpp))(?:;codecs=[^;,]+)?;base64,([A-Za-z0-9+/=]+)$/i);
 if(!m)return json(request,{ok:false,error:'Valid recorded audio is required'},400);
 const approx=Math.floor(m[2].length*3/4);if(approx<80||approx>6*1024*1024)return json(request,{ok:false,error:'Audio size is invalid'},400);
 // Reject digital silence before ASR: Whisper can hallucinate words on empty audio.
 if(/^(?:audio\/wav)$/i.test(m[1])){
   try{
     const bin=atob(m[2]),bytes=Uint8Array.from(bin,c=>c.charCodeAt(0)),view=new DataView(bytes.buffer);
     const tag=o=>String.fromCharCode(...bytes.subarray(o,o+4));
     if(tag(0)==='RIFF'&&tag(8)==='WAVE'){
       let pcm=false,dataOffset=0,dataSize=0;
       for(let o=12;o+8<=bytes.length;){
         const size=view.getUint32(o+4,true),end=o+8+size;if(end>bytes.length)break;
         if(tag(o)==='fmt '&&size>=16)pcm=view.getUint16(o+8,true)===1&&view.getUint16(o+22,true)===16;
         if(tag(o)==='data'){dataOffset=o+8;dataSize=size}
         o=end+(size%2);
       }
       if(pcm&&dataSize>=2){
         let energy=0,peak=0,count=0;
         for(let o=dataOffset;o+1<dataOffset+dataSize;o+=2){const x=view.getInt16(o,true)/32768;energy+=x*x;peak=Math.max(peak,Math.abs(x));count++}
         if(count&&Math.sqrt(energy/count)<.0005&&peak<.003)return json(request,{ok:false,error:'No speech detected',retryable:true,reason:'silent_audio'},422);
       }
     }
   }catch{}
 }
 const nativeText=clean(b.nativeText,4000),nativeConfidence=Math.max(0,Math.min(1,Number(b.nativeConfidence)||0));
 const uiHint=languageCode(b.uiLanguage||''),sentHint=languageCode(b.languageHint||''),conversationHint=languageCode(b.conversationLanguage||''),softHint=sentHint||conversationHint||uiHint;
 const family=t=>{t=String(t||'');if(/[\u0600-\u06ff]/u.test(t))return'arabic';if(/[\u0900-\u097f]/u.test(t))return'devanagari';if(/[\u0980-\u09ff]/u.test(t))return'bengali';if(/[\u0a00-\u0a7f]/u.test(t))return'gurmukhi';if(/[\u0a80-\u0aff]/u.test(t))return'gujarati';if(/[\u0b80-\u0bff]/u.test(t))return'tamil';if(/[\u0c00-\u0c7f]/u.test(t))return'telugu';if(/[\u0d00-\u0d7f]/u.test(t))return'malayalam';if(/[\u0d80-\u0dff]/u.test(t))return'sinhala';if(/[\u0e00-\u0e7f]/u.test(t))return'thai';if(/[\u0e80-\u0eff]/u.test(t))return'lao';if(/[\u1000-\u109f]/u.test(t))return'myanmar';if(/[\u1200-\u137f]/u.test(t))return'ethiopic';if(/[\u1780-\u17ff]/u.test(t))return'khmer';if(/[\u10a0-\u10ff]/u.test(t))return'georgian';if(/[\u0530-\u058f]/u.test(t))return'armenian';if(/[\u0370-\u03ff]/u.test(t))return'greek';if(/[\u0590-\u05ff]/u.test(t))return'hebrew';if(/[\u3040-\u30ff]/u.test(t))return'japanese';if(/[\uac00-\ud7af]/u.test(t))return'korean';if(/[\u4e00-\u9fff]/u.test(t))return'han';if(/[\u0400-\u052f]/u.test(t))return'cyrillic';if(/[A-Za-zÀ-ÖØ-öø-ÿ]/u.test(t))return'latin';return''};
 const nativeFamily=family(nativeText),nativeLang=nativeText?messageLanguage(nativeText,softHint):'';
 const strongHint=languageCode(b.language)==='auto'?'':languageCode(b.language||'');
 const common={task:'transcribe',vad_filter:true,condition_on_previous_text:false,beam_size:5,no_speech_threshold:.68,compression_ratio_threshold:2.4,log_prob_threshold:-1,hallucination_silence_threshold:1.0};
 const timed=(model,input,ms)=>Promise.race([env.AI.run(model,input),new Promise((_,reject)=>setTimeout(()=>reject(Error('asr timeout')),ms))]);
 const usable=r=>{
   const info=r?.transcription_info||r?.result||r||{},segments=r?.segments||info.segments;
   if(Array.isArray(segments)&&segments.length){
     const bad=segments.every(s=>(Number.isFinite(s.no_speech_prob)&&s.no_speech_prob>.6)||(Number.isFinite(s.avg_logprob)&&s.avg_logprob< -1)||(Number.isFinite(s.compression_ratio)&&s.compression_ratio>2.4));
     if(bad)return false;
   }
   return true;
 };
 const errors=[];
 let picked=null,pickedModel='',pickedFormat='';
 const primary={...common,audio:m[2],...(strongHint?{language:strongHint}:{} )};
 try{const r=await timed(ASR_PRIMARY,primary,4800),text=clean(r?.text||r?.transcription_info?.text||r?.result?.text||r?.result||'',5000);if(text&&usable(r)){picked=r;pickedModel=ASR_PRIMARY;pickedFormat=strongHint?'base64-hinted':'base64-auto'}}catch(e){errors.push(ASR_PRIMARY+':'+clean(e?.message||e,140))}
 // Accept only audio-derived transcription with usable confidence metadata.
 let text=picked?clean(picked?.text||picked?.transcription_info?.text||picked?.result?.text||picked?.result||'',5000):'';
 const quality=r=>{
   const info=r?.transcription_info||r?.result||r||{},segments=r?.segments||info.segments||[];
   const logs=segments.map(x=>x.avg_logprob).filter(Number.isFinite),probs=segments.map(x=>x.no_speech_prob).filter(Number.isFinite);
   const probability=[r?.language_probability,info.language_probability].find(Number.isFinite);
   return{logprob:logs.length?logs.reduce((a,b)=>a+b,0)/logs.length:null,noSpeech:probs.length?Math.max(...probs):null,languageProbability:probability??null}
 };
 const initialQuality=quality(picked),initialLang=languageCode(picked?.language||picked?.detected_language||picked?.transcription_info?.language||picked?.result?.language||'');
 const uncertain=initialQuality.logprob!==null&&initialQuality.logprob<-.65||initialQuality.noSpeech!==null&&initialQuality.noSpeech>.45||initialQuality.languageProbability!==null&&initialQuality.languageProbability<.7;
 if(text&&uncertain&&!strongHint&&conversationHint&&conversationHint!==initialLang){
   try{const retry=await timed(ASR_PRIMARY,{...common,audio:m[2],language:conversationHint},2800),rq=quality(retry),rt=clean(retry?.text||retry?.transcription_info?.text||retry?.result?.text||retry?.result||'',5000);
     if(rt&&usable(retry)&&rq.logprob!==null&&initialQuality.logprob!==null&&rq.logprob>initialQuality.logprob+.25){picked=retry;text=rt;pickedFormat='base64-confidence-recovery'}
   }catch(e){errors.push('confidence retry:'+clean(e?.message||e,80))}
 }
 // Auto detection must not force Arabic or replace audio with a
 // phone transcript constrained to the UI language.
 // If the first pass failed, use legacy Whisper bytes as a bounded fallback.
 if(!text){try{const bin=atob(m[2]),audio=Array.from(bin,c=>c.charCodeAt(0)),input={...common,audio,...(strongHint?{language:strongHint}:{})};const r=await timed(ASR_FALLBACK,input,3200),t=clean(r?.text||r?.result?.text||r?.result||'',5000);if(t&&usable(r)){text=t;picked=r;pickedModel=ASR_FALLBACK;pickedFormat='bytes-fallback'}}catch(e){errors.push(ASR_FALLBACK+':'+clean(e?.message||e,140))}}
 if(text){const q=quality(picked),needsReview=Boolean(q.logprob===null&&q.languageProbability===null||q.logprob!==null&&q.logprob<-.65||q.noSpeech!==null&&q.noSpeech>.45||q.languageProbability!==null&&q.languageProbability<.7);const detected=clean(picked?.language||picked?.detected_language||picked?.transcription_info?.language||picked?.result?.language||'',24),language=languageCode(detected)||messageLanguage(text,strongHint||softHint);return json(request,{ok:true,text,language,needsReview,confidence:q,detectedLanguage:language,model:pickedModel,audioFormat:pickedFormat,autoLanguage:!strongHint,languageHintUsed:strongHint||null,nativeRescue:pickedModel.startsWith('native-')},200)}
 return json(request,{ok:false,error:'Voice transcription is temporarily unavailable',retryable:true,detail:errors.join(' | ')},503)
}

function directCategoryIntent(message,modelCategory='general'){
 const s=String(message||'').toLowerCase().trim();
 if(employmentIntent(message))return'jobs';
 if(/(?:کار.{0,24}(?:پیدا|بگرد)|(?:پیدا|بگرد).{0,24}کار|شغل.{0,24}(?:پیدا|بگرد)|(?:پیدا|بگرد).{0,24}شغل)/u.test(s))return'jobs';
 if(/(?:نوکری|ملازمت).{0,28}(?:تلاش|ڈھونڈ|چاہ)|(?:تلاش|ڈھونڈ).{0,28}(?:نوکری|ملازمت)/u.test(s))return'jobs';
 const action=/(?:\b(?:find|search|show|open|take me|go to|book|reserve|buy|sell|rent|need|want|looking for|look for|apply for|help me find|help me get)\b|دوريني|دورلي|ندور|عم دور|بدور|ابحث|أبحث|فتش|فتشي|بدي|بدّي|عايز|عاوز|أبغى|ابغى|أبي|ابي|بغيت|اريد|أريد|احتاج|أحتاج|افتح|افتحي|وديني|ودّيني|خذني|خدني|احجز|احجزي|اشتري|بيع|استأجر|استاجر|ساعدني|ساعديني|cherch(?:e|er|ez)|trouv(?:e|er|ez)(?:-moi)?|montre(?:z|-moi)?|ouvre(?:z)?|réserve|reserver|achet(?:e|er)|vend(?:s|re)|lou(?:e|er)|besoin|veux|búscame|buscame|busca|buscar|encuéntrame|encuentrame|encuentra|muéstrame|muestrame|muestra|abre|llévame|llevame|quiero|necesito|reservar|comprar|vender|alquilar|procure|procurar|encontre|mostre|abra|quero|preciso|alugar|finde|finden|suche|such|zeige|zeig|öffne|offne|brauche|möchte|mochte|buchen|kaufen|verkaufen|mieten|trova|cerca|apri|mostra|voglio|cerco|bisogno|arıyorum|ariyorum|bana|ara|bul|göster|goster|aç|ac|istiyorum|rezerv|satın|kirala|найди|найти|ищу|открой|покажи|нужен|хочу|забронируй|купить|продать|аренд|找|搜索|打开|带我|我想|我需要|预订|购买|出售|租|探して|検索|開いて|連れて|見せて|欲しい|必要|予約|購入|売|借|찾아|검색|열어|데려|보여|원해|필요|예약|구매|판매|임대|खोज|ढूंढ|ढूँढ|खोल|दिखा|चाहिए|चाहता|बुक|खरीद|बेच|किराए|tìm|tim|tìm kiếm|mở|mở|hãy tìm|hay tim|cari|carikan|buka|tunjukkan|tolong|ingin|butuh|tafuta|fungua|onyesha|nataka|nahitaji|খুঁজ|খোঁজ|দেখাও|খুল|পাই|پیدا|باز کن|بگرد|می.?خواهم|میخوام|تلاش|ڈھونڈ|ڈھونڈو|کھولو|دکھاؤ|چاہیے)/iu.test(s)
 if(!action)return category(modelCategory);
 if(/(?:بدي|أريد|اريد|احتاج|أحتاج).{0,15}(?:أسافر|اسافر|سافر)|\b(?:i want to|i need to|let me) travel\b/iu.test(s))return'travel';
 const rules=[
 ['jobs',/(?:\bjob|jobs|career|vacancy|employment|work\b|وظيف|وظائف|وظايف|شغل|فرصة عمل|emploi|travail|trabajo|empleo|trabalho|emprego|lavoro|arbeit|stelle|stellen|iş|kariyer|работ|ваканси|工作|职位|求人|仕事|채용|일자리|직업|नौकरी|रोजगार|काम|việc làm|công việc|viec lam|pekerjaan|kerja|kazi|ajira|চাকরি|কাজ|کار|شغل|نوکری|کام)/iu],
 ['travel',/(?:hotel|hotels|flight|flights|airport|travel|trip|room|فندق|فنادق|طيران|رحلة|سفر|غرفة|hôtel|vol|voyage|vuelo|viaje|voo|viagem|flug|reise|otel|uçuş|seyahat|отел|рейс|путешеств|酒店|航班|旅行|ホテル|フライト|호텔|항공|여행|होटल|उड़ान|यात्रा)/iu],
 ['property',/(?:property|real estate|house|home|apartment|land|عقار|بيت|منزل|شقة|ارض|أرض|immobilier|maison|appartement|terrain|inmueble|casa|apartamento|terreno|imóvel|immobil|haus|wohnung|grundstück|emlak|ev|daire|arsa|недвиж|дом|квартир|земл|房产|房子|公寓|土地|不動産|家|アパート|부동산|집|아파트|토지|संपत्ति|घर|अपार्टमेंट|ज़मीन)/iu],
 ['cars',/(?:car|cars|vehicle|auto|سيارة|سيارات|مركبة|voiture|véhicule|coche|carro|veículo|wagen|fahrzeug|araba|otomobil|машин|авто|汽车|车辆|車|自動車|자동차|차량|कार|गाड़ी)/iu],
 ['shopping',/(?:shopping|product|products|shop|store|price|تسوق|منتج|منتجات|سعر|boutique|produit|achat|tienda|producto|compras|loja|produto|einkauf|produkt|alışveriş|ürün|магазин|товар|购物|产品|買い物|商品|쇼핑|제품|खरीदारी|उत्पाद)/iu],
 ['restaurants',/(?:restaurant|food|cafe|coffee|مطعم|مطاعم|اكل|أكل|قهوة|nourriture|café|restaurante|comida|essen|restoran|yemek|кафе|ресторан|еда|餐厅|咖啡|レストラン|食事|카페|레스토랑|음식|रेस्तरां|खाना|कैफे)/iu],
 ['services',/(?:service|services|repair|plumber|electrician|cleaning|خدمة|خدمات|صيانة|سباك|كهربائي|تنظيف|réparation|plombier|servicio|reparación|serviço|reparo|dienst|reparatur|hizmet|tamir|услуг|ремонт|服务|维修|サービス|修理|서비스|수리|सेवा|मरम्मत)/iu],
 ['equipment',/(?:equipment|machinery|machine|generator|معدات|ماكينات|آلات|مولد|équipement|equipo|maquinaria|equipamento|maschine|ausrüstung|ekipman|makine|оборудован|设备|机械|機械|設備|장비|기계|उपकरण|मशीन)/iu],
 ['boats',/(?:boat|boats|yacht|marine|قارب|قوارب|يخت|bateau|barco|iate|boot|yat|лодк|яхт|船|游艇|ボート|ヨット|보트|요트|नाव|यॉट)/iu],
 ['business',/(?:supplier|manufacturer|factory|wholesale|import|export|مورد|مصنع|استيراد|تصدير|fournisseur|fabricant|usine|proveedor|fábrica|fornecedor|lieferant|fabrik|tedarikçi|fabrika|поставщик|завод|供应商|工厂|サプライヤー|工場|공급업체|공장|आपूर्तिकर्ता|फैक्टरी)/iu],
 ['shipping',/(?:shipping|logistics|freight|cargo|delivery|شحن|لوجست|توصيل|fret|logistique|envío|logística|frete|versand|logistik|kargo|lojistik|достав|логист|货运|物流|配送|輸送|배송|물류|शिपिंग|लॉजिस्टिक|डिलीवरी)/iu],
 ['software',/(?:software|application|app development|برمجيات|تطبيق|تطبيقات|logiciel|aplicación|aplicativo|anwendung|yazılım|программ|软件|应用|ソフトウェア|アプリ|소프트웨어|앱|सॉफ्टवेयर|ऐप)/iu],
 ['hosting',/(?:hosting|domain|website|web hosting|استضافة|دومين|موقع|hébergement|domaine|alojamiento web|dominio|hospedagem|domínio|barındırma|alan adı|хостинг|домен|托管|域名|ホスティング|ドメイン|호스팅|도메인|होस्टिंग|डोमेन)/iu],
 ['solar',/(?:solar|inverter|photovoltaic|pv panel|طاقة شمسية|شمسي|انفرتر|ألواح|solaire|fotovolta|güneş|солнеч|光伏|太阳能|太陽光|ソーラー|태양광|सौर)/iu],
 ['education',/(?:education|school|university|course|training|تعليم|مدرسة|جامعة|دورة|تدريب|école|université|cours|escuela|universidad|curso|escola|universidade|schule|universität|kurs|okul|üniversite|курс|школ|университет|学校|大学|课程|コース|학교|대학|과정|स्कूल|विश्वविद्यालय|कोर्स)/iu],
 ['health',/(?:hospital|clinic|doctor|pharmacy|health|مستشفى|عيادة|طبيب|صيدلية|صحة|hôpital|clinique|médecin|farmacia|médico|clínica|arzt|krankenhaus|hastane|doktor|больниц|врач|医院|医生|薬局|病院|医師|병원|의사|अस्पताल|डॉक्टर|फार्मेसी)/iu],
 ['money',/(?:insurance|bank|loan|finance|money|تأمين|بنك|قرض|تمويل|assurance|banque|prêt|seguro|banco|préstamo|empréstimo|versicherung|kredit|sigorta|banka|kredi|страх|банк|кредит|保险|银行|贷款|保険|銀行|ローン|보험|은행|대출|बीमा|बैंक|ऋण)/iu],
 ['games',/(?:game|games|gaming|لعبة|العاب|ألعاب|jeu|juego|jogo|spiel|oyun|игр|游戏|ゲーム|게임|खेल)/iu],
 ['media',/(?:news|movie|music|radio|tv|أخبار|فيلم|موسيقى|actualités|film|musique|noticias|película|música|notícias|filme|musik|nachrichten|haber|müzik|новост|фильм|музык|新闻|电影|音乐|ニュース|映画|音楽|뉴스|영화|음악|समाचार|फिल्म|संगीत)/iu]
 ];
 for(const [cat,re] of rules)if(re.test(s))return cat;
 if(/^(?:بدي|أريد|اريد|عايز|عاوز|i want to|i need to)\s+(?:اشتري|أشتري|buy)(?:\s+(?:شي|شيء|حاجة|something))?[.!؟?]*$/iu.test(s))return'shopping';
 return category(modelCategory)
}

async function degradedFallback(request,env,ctx,body,message){
 const act=actionState(message,'','',body?.clientControls),language=messageLanguage(message,body?.language),meta=metaConversation(message),chat=conversationOnly(message)||meta,requested=directCategoryIntent(message,category(body?.conversationIntent||'general')),cat=(act.isAction||chat)?'general':requested,response=act.isAction?actionReply(language,act.cc,act.ll):meta?metaReply(message,language):chat?conversationalFallback(message,language):usefulFallback(message,language,cat);
 return json(request,{ok:true,response,language,speechLocale:speechLocaleFor(language,message,body?.history),category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'seekvera-r114-instant-local-fallback',fastPath:'r114-bounded-fallback',liveData:false},200)
}

async function runStructured(env,body){
 const message=clean(body?.message??body?.prompt,2400);if(!message)return null;
 const selected=clean(body?.country,120)||'Worldwide',targetLanguage=messageLanguage(message,body?.language),history=languageSafeHistory(body?.history,targetLanguage);
 const system=`You are SEEKVERA AI, the action assistant inside a worldwide marketplace and discovery app. You must understand the LATEST USER MESSAGE directly, including dialects, slang, Lebanese Arabic, mixed Arabic/English, transliteration, and any major world language. Never choose the reply language from the selected country, interface, or browser. Reply in the SAME language and script as the latest user message unless the user explicitly requests another reply language. Match the user’s DIALECT and register as well as language. Lebanese or Levantine Arabic must get natural spoken Lebanese Arabic, never Modern Standard Arabic. Egyptian, Gulf and Maghrebi speakers get their own dialect. Apply the same rule to slang, Pidgin and dialects in every language. Use the latest user turn and recent USER turns to preserve their dialect; never infer it from country, browser, or interface. Current Arabic dialect evidence: ${targetLanguage==='ar'?arabicDialect(message,body?.history):'not applicable'}. The reply text itself MUST visibly use that language/script; never translate Arabic speech into Icelandic, English, or another language, and never claim one languageCode while writing in another language.\
\
Return ONLY one JSON object with exactly these keys: reply, languageCode, category, countryAction, languageAction.\
- reply: behave like a real conversational AI assistant. Hold a normal back-and-forth conversation, answer questions directly, understand corrections and follow-ups, and use the recent conversation as memory. For greetings and genuine knowledge questions, answer naturally. For requests to travel, buy, sell, find, book, work, visit or browse, choose the relevant section immediately and give one short acknowledgement in the user’s language. Do not ask for city, dates, budget, quantity or preferences before opening a section; those filters are available there. For a generic purchase request choose shopping; for a generic travel request choose travel. Ask a clarification only when no section can be determined.\
- languageCode: best ISO language code for the latest user message.\
- category: exactly one of ${[...CATS].join(', ')}. Conversation-first rule: use general for greetings, small talk, questions, explanations, language/voice talk, corrections, incomplete requests, and every clarification turn. Choose a marketplace category only when the user's current goal is genuinely actionable and belongs there (find/search/book/buy/sell/apply/compare/use). A clear command such as ‘find me a job’, ‘دوريني على شغل’, ‘find me a hotel’, ‘show me cars’, or the equivalent in any language is actionable immediately: choose its category even if city, date or budget is not known yet. Never route merely because a keyword appears. Never classify casual uses of work/عمل/شغل as Jobs unless the person is actually seeking employment.\
- Language/voice meta-conversation rule: if the user says they are speaking a language, asks whether you understand/hear them, comments on which language you are speaking, or simply tests conversation (for example: ‘صرت بتحكي عربي هون’, ‘I am speaking Arabic now’, ‘Can you understand French?’), category MUST be general. Reply naturally to what they said. Never say you will send them to a section unless they actually ask for a marketplace task.\
- countryAction: the ISO-3166 alpha-2 code for ANY country in the world, or WW, ONLY when the user explicitly commands the SEEKVERA APP/MARKET/COUNTRY SELECTOR to change/switch/move/set. Understand country names in the user's own language and dialect. Leave empty when the user merely searches for something in a country.\
- languageAction: supported language code ONLY when the user explicitly commands the app/interface language to change. Leave empty otherwise.\
\
Action examples: “حطني تركيا” => countryAction TR. “change the app to France” => FR. “把应用切换到巴西” => BR. “حوّلني ورلد وايد” => WW. “حطلي تركي” when clearly asking app language => languageAction tr. “بدي فندق بفرنسا” is a search, NOT a country action. “I need a job in Germany” is jobs, NOT a country action.\
Selected market: ${selected}.\
Conversation history:\
${history||'(none)'}\
Latest user message: ${message}`;
 const messages=[{role:'system',content:system},{role:'user',content:message}];
 const modelAttempt=async model=>{
   const r=await Promise.race([env.AI.run(model,{messages,temperature:.18,max_tokens:420}),new Promise((_,reject)=>setTimeout(()=>reject(Error('model timeout')),3000))]),text=modelText(r),obj=parseJSON(text);if(!obj||!clean(obj.reply,5000))throw Error('invalid structured response');
   const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=messageLanguage(message,obj.languageCode||targetLanguage),declared=languageCode(obj.languageCode),meta=metaConversation(message),modelCat=category(obj.category),cat=(act.isAction||conversationOnly(message)||meta)?'general':directCategoryIntent(message,modelCat);
   if(declared&&declared!==language&&!translationRequest(message)&&!replyMatchesLanguage(obj.reply,language,message))throw Error('model language mismatch');
   let reply=act.isAction?actionReply(language,act.cc,act.ll):cat!=='general'&&routeReplyFor(language,message,body?.history)?routeReplyFor(language,message,body?.history):guardedReply(obj.reply,language,message);if(!reply)throw Error('reply language mismatch');if(meta&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);
   return{ok:true,response:reply,language,speechLocale:speechLocaleFor(language,message,body?.history),category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model,fastPath:act.isAction?'r114-verified-action-first':meta?'r114-meta-conversation-guard':'r114-fast-model-race',liveData:false}
 };
 try{const winner=await Promise.race([Promise.any([FAST,PRIMARY,FALLBACK].map(modelAttempt)),new Promise(resolve=>setTimeout(()=>resolve(null),3300))]);if(winner)return winner}catch(_){}
 // Keep a real conversational AI fallback, but never let it stall the UI.
 try{
   const backupPrompt=messages.map(x=>String(x?.role||'user').toUpperCase()+': '+String(x?.content||'')).join('\n').slice(-14000);
   const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),1400);
   try{
     const br=await fetch('https://text.pollinations.ai/'+encodeURIComponent(backupPrompt)+'?model=openai&private=true',{headers:{'accept':'text/plain','user-agent':'SEEKVERA/1.0'},signal:ctl.signal});
     if(br.ok){
       const raw=await br.text(),obj=parseJSON(raw);
       if(obj&&clean(obj.reply,5000)){
         const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=messageLanguage(message,obj.languageCode||targetLanguage),declared=languageCode(obj.languageCode),meta=metaConversation(message),modelCat=category(obj.category),cat=(act.isAction||conversationOnly(message)||meta)?'general':directCategoryIntent(message,modelCat);
         let reply=act.isAction?actionReply(language,act.cc,act.ll):cat!=='general'&&routeReplyFor(language,message,body?.history)?routeReplyFor(language,message,body?.history):guardedReply(obj.reply,language,message);if(declared&&declared!==language&&!translationRequest(message)&&!replyMatchesLanguage(obj.reply,language,message))reply='';if(meta&&reply&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);
         if(reply)return{ok:true,response:reply,language,speechLocale:speechLocaleFor(language,message,body?.history),category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'pollinations-private-conversation-fallback',fastPath:'r117-language-guard-fallback',liveData:false}
       }
       const plain=guardedReply(raw,targetLanguage,message);if(plain){const language=targetLanguage,meta=metaConversation(message),cat=(conversationOnly(message)||meta)?'general':directCategoryIntent(message,'general');return{ok:true,response:plain,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:null,languageAction:null,model:'pollinations-private-conversation-plain',fastPath:'r117-language-guard-plain',liveData:false}}
     }
   }finally{clearTimeout(to)}
 }catch(_){}

 return null;
}

function fastCommandLanguage(message,suggested=''){
 const t=String(message||''),s=t.toLowerCase();
 if(/[ٹڈڑںھۓے]/u.test(t)||/(?:میرے|لیے|نوکری|ملازمت|ڈھونڈ|دکھاؤ|چاہیے|کرو)/u.test(s))return'ur';
 if(/[پچژگ]/u.test(t)||/(?:برای|پیدا|بگرد|می.?خواهم|میخوام)/u.test(s))return'fa';
 if(/[ښږڅځټړ]/u.test(t))return'ps';
 if(/[ڵۆێ]/u.test(t))return'ku';
 if(/[\u0600-\u06ff]/u.test(t))return messageLanguage(t,suggested);
 if(/[\u0900-\u097f]/u.test(t))return'hi';if(/[\u0980-\u09ff]/u.test(t))return'bn';if(/[\u3040-\u30ff]/u.test(t))return'ja';if(/[\u4e00-\u9fff]/u.test(t))return'zh';if(/[\uac00-\ud7af]/u.test(t))return'ko';if(/[\u0400-\u052f]/u.test(t))return'ru';
 if(/[đăơư]/iu.test(t)||/(?:tìm|việc làm|công việc|khách sạn|xe hơi|giúp tôi|hãy)/iu.test(s))return'vi';
 if(/[ğışİ]/u.test(t)||/\b(?:bana|bul|arıyorum|ariyorum|istiyorum|iş|otel|araba|ev)\b/iu.test(s))return'tr';
 if(/(?:búscame|buscame|busca|encuéntrame|encuentrame|muéstrame|muestrame|quiero|necesito|trabajo|empleo|coche)/iu.test(s))return'es';
 if(/(?:trouve|cherch|montre|ouvre|je veux|besoin|emploi|travail|voiture|hôtel)/iu.test(s))return'fr';
 if(/(?:procure|encontre|mostre|quero|preciso|trabalho|emprego|carro)/iu.test(s))return'pt';
 if(/(?:finde|suche|zeige|öffne|offne|ich möchte|ich mochte|brauche|arbeit|stelle|wohnung)/iu.test(s))return'de';
 if(/(?:trova|cerca|apri|mostra|voglio|bisogno|lavoro|macchina|albergo)/iu.test(s))return'it';
 if(/(?:carikan|cari|buka|tunjukkan|tolong|pekerjaan|kerja|mobil|rumah)/iu.test(s))return'id';
 if(/(?:tafuta|fungua|onyesha|nataka|nahitaji|kazi|ajira|gari|nyumba)/iu.test(s))return'sw';
 return messageLanguage(t,suggested)
}

const FAST_DIRECT_LANGS=new Set(['ar','en','fr','es','de','tr','pt','it','vi','id','sw','ru','hi','zh','ja','ko','bn','fa','ur']);
function fastRouteReply(language){
 const r={
  ar:'أكيد، عم بفتحلك القسم المناسب.',
  en:'Sure. Opening the right section now.',
  fr:'Compris. J’ouvre directement la section adaptée à votre demande.',
  es:'Entendido. Voy a abrir directamente la sección adecuada para tu solicitud.',
  de:'Verstanden. Ich öffne jetzt direkt den passenden Bereich.',
  tr:'Anladım. Uygun bölümü şimdi doğrudan açıyorum.',
  pt:'Entendi. Vou abrir diretamente a seção certa para o seu pedido.',
  it:'Capito. Apro subito la sezione giusta per la tua richiesta.',
  vi:'Đã hiểu. Tôi đang mở ngay mục phù hợp với yêu cầu của bạn.',
  id:'Mengerti. Saya langsung membuka bagian yang tepat untuk permintaan Anda.',
  sw:'Nimekuelewa. Ninafungua moja kwa moja sehemu inayofaa kwa ombi lako.',
  ru:'Понял. Я сразу открываю подходящий раздел для вашего запроса.',
  hi:'समझ गया। मैं आपके अनुरोध के लिए सही सेक्शन सीधे खोल रहा हूँ।',
  zh:'明白了。我现在直接打开适合你请求的栏目。',
  ja:'わかりました。ご希望に合うセクションをすぐに開きます。',
  ko:'알겠습니다. 요청에 맞는 섹션을 바로 열겠습니다.',
  bn:'বুঝেছি। আপনার অনুরোধের জন্য সঠিক বিভাগটি এখনই খুলছি।',
  fa:'متوجه شدم. بخش مناسب درخواست شما را مستقیم باز می‌کنم.',
  ur:'سمجھ گیا۔ میں آپ کی درخواست کے لیے مناسب سیکشن فوراً کھول رہا ہوں۔'
 };
 return r[language]||''
}
function fastActionResult(message,body){
 const language=fastCommandLanguage(message,body?.language),act=actionState(message,'','',body?.clientControls);
 if(act.isAction){
  return{ok:true,response:actionReply(language,act.cc,act.ll),language,category:'general',route:null,countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'seekvera-r120-direct-control',fastPath:'r120-direct-control',liveData:false}
 }
 const cat=directCategoryIntent(message,'general');
 if(cat!=='general'&&FAST_DIRECT_LANGS.has(language)){
  const response=routeReplyFor(language,message,body?.history)||usefulFallback(message,language,cat);
  return{ok:true,response,language,speechLocale:speechLocaleFor(language,message,body?.history),category:cat,route:ROUTES[cat]||ROUTES.marketplace,countryAction:null,languageAction:null,model:'seekvera-r120-direct-intent',fastPath:'r120-direct-intent',liveData:false}
 }
 return null
}

export default{async fetch(request,env,ctx){
 const u=new URL(request.url);
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers:headers(request)});
 if(u.pathname==='/api/health'){
   const r=await baseWorker.fetch(request,env,ctx);let d={};try{d=await r.clone().json()}catch{}return json(request,{...d,release:RELEASE,r123:true,r123Runtime:'single-voice-turn-arabic-auto-rescue',r122:true,r122Runtime:'unified-home-direct-routing-and-language-independent-voice',r121e:true,r121eRuntime:'urdu-first-persian-distinctive-detection',r121d:true,r121dRuntime:'arabic-persian-urdu-disambiguation',r121c:true,r121cRuntime:'persian-urdu-arabic-script-command-routing',r121b:true,r121bRuntime:'repaired-global-command-inflections-and-language-detection',r121:true,r121Runtime:'global-command-inflections-and-fast-language-detection',r120:true,r120Runtime:'instant-controls-direct-intent-language-independent-voice',r119b:true,r119bRuntime:'language-independent-voice-direct-intent-atomic-controls',r119:true,r119Runtime:'explicit-intent-routing-plus-hinted-arabic-asr-rescue',r118:true,r118Runtime:'script-first-plus-model-hint-language-resolution',r117:true,r117Runtime:'strict-reply-language-contract-and-history-sanitizer',r105:true,r105Runtime:'worldwide-default-language-safe-ai-atomic-localization',r86:true,r86Runtime:'conversation-first-multilingual-ai',r92:true,r92Runtime:'native-asr-payload-per-model-auto-language',r89:true,r89Runtime:'workers-ai-whisper-byte-array-no-consent',r88:true,r88Runtime:'fast-auto-asr-server-first-tts-natural-fallback',r87:true,r87Runtime:'latest-message-language-plus-real-ai-fallback',r86Routing:'goal-aware-not-keyword-first',r86Voice:'whisper-auto-language-independent-of-ui',r86Asr:ASR_PRIMARY,r81:true,r81Runtime:'natural-multilingual-conversation',r81Routing:'explicit-intent-only',r81Voice:'server-auto-asr-first',r81Fallback:'natural-conversation-and-deterministic-actions'});
 }
 if(u.pathname==='/api/transcribe'&&request.method==='POST')return transcribeAudio(request,env);
 if(u.pathname==='/api/ai'&&request.method==='POST'){
   let body={};try{body=await request.clone().json()}catch{return json(request,{ok:false,error:'Invalid JSON'},400)}
   const message=clean(body?.message??body?.prompt,2400);if(!message)return json(request,{ok:false,error:'Message is required'},400);
   const reason=blocked(message);if(reason){const language=messageLanguage(message,body?.language);return json(request,{ok:true,blocked:true,reviewRequired:true,response:safetyReply(language),language,reason,category:'general',route:null,countryAction:null,languageAction:null,model:'seekvera-r105-safety'},200)}
   const quick=fastActionResult(message,body);if(quick)return json(request,quick,200);
   if(env.AI){const d=await runStructured(env,body);if(d)return json(request,d,200)}
   return degradedFallback(request,env,ctx,body,message);
 }
 return baseWorker.fetch(request,env,ctx);
}};
