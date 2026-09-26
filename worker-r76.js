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
   const r=await baseWorker.fetch(request,env,ctx);let d={};try{d=await r.clone().json()}catch{}return json(request,{...d,r76:true,r76Runtime:'single-structured-multilingual-ai',r76Voice:'server-auto-asr-first',r76Locale:'complete-static-pack-audit'});
 }
 if(u.pathname==='/api/ai'&&request.method==='POST'){
   let body={};try{body=await request.clone().json()}catch{return json(request,{ok:false,error:'Invalid JSON'},400)}
   const message=clean(body?.message??body?.prompt,2400);if(!message)return json(request,{ok:false,error:'Message is required'},400);
   const reason=blocked(message);if(reason)return json(request,{ok:true,blocked:true,reviewRequired:true,response:'SEEKVERA cannot help buy, sell, source or promote prohibited or illegal items or services.',reason,category:'general',route:ROUTES.general,countryAction:null,languageAction:null,model:'seekvera-r76-safety'},200);
   if(env.AI){const d=await runStructured(env,body);if(d)return json(request,d,200)}
   const fallback=await baseWorker.fetch(request,env,ctx);const h=new Headers(fallback.headers);h.set('x-seekvera-release',RELEASE);return new Response(fallback.body,{status:fallback.status,statusText:fallback.statusText,headers:h});
 }
 return baseWorker.fetch(request,env,ctx);
}};
