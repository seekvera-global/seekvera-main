const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const i18n=fs.readFileSync('i18n-ui.js','utf8');
const navigation=fs.readFileSync('navigation.js','utf8');
const BLOCK='sv_ui_translate_blocked_r19',LOCK='sv_ui_translate_lock_r19';
function storage(seed={}){const map=new Map(Object.entries(seed));return{getItem:k=>map.has(k)?map.get(k):null,setItem:(k,v)=>map.set(k,String(v)),removeItem:k=>map.delete(k),map};}
function harness(code,store,responses){
 let calls=0;
 const context={sessionStorage:store,AbortController,setTimeout,clearTimeout,api:p=>p,langName:l=>l,valid:v=>typeof v==='string'&&!!v.trim(),fetch:async()=>{calls++;const x=responses.shift()||{status:503,body:{reason:'all_translation_backends_unavailable'}};return{status:x.status,ok:x.status>=200&&x.status<300,json:async()=>x.body};},console};
 vm.createContext(context);vm.runInContext(code,context);
 return{context,calls:()=>calls};
}
function extract(source,start,end,label){const a=source.indexOf(start),b=source.indexOf(end,a);assert(a>=0&&b>a,label+' source block not found');return source.slice(a,b);}
const i18nBlock=extract(i18n,"const UI_TRANSLATE_BLOCK_KEY='sv_ui_translate_blocked_r19'","async function translate(l,arr)","i18n quota helper");
const navBlock=extract(navigation,"let localeTimer=0,translateSeq=0,uiTranslationBlocked=false","const localeControl=","navigation quota helper");
const i18nCode=i18nBlock+"\nthis.cloudTranslate=cloudTranslate;this.blocked=()=>CLOUD_TRANSLATE_BLOCKED;";
const navCode=navBlock+"\nthis.requestUiTranslation=requestUiTranslation;this.blocked=()=>uiTranslationBlocked;";
async function main(){
 // A single 503 blocks subsequent language batches in the same tab session.
 const shared=storage(),c=harness(i18nCode,shared,[{status:503,body:{reason:'all_translation_backends_unavailable'}}]);
 const results=await Promise.all([c.context.cloudTranslate('French',['one']),c.context.cloudTranslate('German',['two']),c.context.cloudTranslate('Arabic',['three'])]);
 assert.deepEqual(results,[null,null,null]);assert.equal(c.calls(),1);assert.equal(shared.getItem(BLOCK),'1');assert.equal(shared.getItem(LOCK),null);
 // The navigation fallback shares the same session block and cannot issue another request.
 const n=harness(navCode,shared,[{status:200,body:{translations:['مرحبا']}}]);
 assert.equal(await n.context.requestUiTranslation('Arabic',['Hello']),null);assert.equal(n.calls(),0);
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
 // The main UI translation loop is serial and stops after the first terminal response.
 const translateStart=i18n.indexOf('async function translate(l,arr){'),translateEnd=i18n.indexOf('function setText(',translateStart);
 assert(translateStart>=0&&translateEnd>translateStart,'translation loop source not found');
 const loop=i18n.slice(translateStart,translateEnd);
 assert(!loop.includes('Promise.all'),'translation batches must not run in parallel');
 assert(loop.includes('for(const batch of groups)'),'translation batches must run sequentially');
 const full=harness(i18nCode,storage(),[{status:503,body:{reason:'all_translation_backends_unavailable'}}]);
 full.context.loadPack=async()=>true;full.context.get=()=>'';full.context.worth=()=>true;full.context.put=()=>{};full.context.MEM=new Map();
 vm.runInContext(loop+'\nthis.runTranslate=translate;',full.context);
 const changed=await full.context.runTranslate('French',Array.from({length:29},(_,i)=>'source '+i));
 assert.equal(changed,false);assert.equal(full.calls(),1);
 // Both navigation fallbacks must use the shared guarded helper, never fetch the endpoint directly.
 const staticFn=extract(navigation,'async function translateStaticAI()','async function translateResidualUI()','static AI fallback');
 const residualFn=extract(navigation,'async function translateResidualUI()','function runLocaleEngines()','residual UI fallback');
 assert(staticFn.includes('requestUiTranslation'));assert(residualFn.includes('requestUiTranslation'));
 assert(!staticFn.includes("fetch('/api/ui-translate'"));assert(!residualFn.includes("fetch('/api/ui-translate'"));
 console.log('PASS: session quota circuit breaker, shared in-flight lock, sequential batches and navigation fallback guard');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
