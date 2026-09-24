/* SEEKVERA R9 visible-UI locale guard */
(()=>{'use strict';
if(window.__seekveraLocaleGuardR9)return;window.__seekveraLocaleGuardR9=true;
const VERSION='20260924-final-r9';
const textSource=new WeakMap(),attrSource=new WeakMap(),memory=new Map();
let applying=false,pending=false,timer=0,seq=0;
const SKIP='script,style,noscript,code,pre,svg,select,option,textarea,#aiMessages,#aiResult,.ai-msg,.sv-ai-answer,.sv-ai-actions,[data-no-translate]';
const QUICK={
 ar:{'AI & Search':'الذكاء والبحث','Flights':'الرحلات الجوية','Find it faster. Compare it better.':'اعثر عليه أسرع. قارنه بشكل أفضل.','Hotels, homes, cars, jobs, products, suppliers, media and services — from one global marketplace.':'فنادق ومنازل وسيارات ووظائف ومنتجات وموردون وإعلام وخدمات — من سوق عالمي واحد.','Worldwide':'العالم كله','AI assisted':'بمساعدة الذكاء الاصطناعي','Voice + Chat':'صوت + دردشة','Browse categories':'تصفح الأقسام','Popular categories':'الأقسام الشائعة','Marketplace':'السوق','Travel':'السفر','Hotels':'الفنادق','Tourism':'السياحة','Property':'العقارات','Cars & Auto':'السيارات والمركبات','Jobs':'الوظائف','Shopping':'التسوق','Restaurants & Food':'المطاعم والطعام','Local Services':'الخدمات المحلية','Equipment & Machinery':'المعدات والآلات','Boats & Marine':'القوارب والبحرية','Import & Export':'الاستيراد والتصدير','Shipping & Logistics':'الشحن والخدمات اللوجستية','Business Software':'برامج الأعمال','Software':'البرامج','Websites & Hosting':'المواقع والاستضافة','Solar & Energy':'الطاقة الشمسية والطاقة','Education':'التعليم','Health':'الصحة','Money & Insurance':'المال والتأمين','Entertainment':'الترفيه','News & Media':'الأخبار والإعلام','Games':'الألعاب','Connectivity':'الاتصال','Free Wi‑Fi':'واي فاي مجاني','AI Deal Agent':'وكيل الصفقات بالذكاء الاصطناعي','Everyday':'الاحتياجات اليومية','Scan / QR':'مسح / QR','Post Ad':'أضف إعلاناً','Promote / Business':'الترويج / الأعمال','Near Me':'بالقرب مني','My Country':'بلدي','Choose a country once and SEEKVERA switches the app language, currency, AI context and country-aware sections automatically. You can still change language manually if you want.':'اختر دولة مرة واحدة، وستغيّر SEEKVERA تلقائياً لغة التطبيق والعملة وسياق الذكاء الاصطناعي والأقسام المرتبطة بالدولة. ويمكنك تغيير اللغة يدوياً متى أردت.'},
 fr:{'AI & Search':'IA et recherche','Flights':'Vols','Find it faster. Compare it better.':'Trouvez plus vite. Comparez mieux.','Worldwide':'Monde entier','AI assisted':'Assisté par IA','Voice + Chat':'Voix + chat','Browse categories':'Parcourir les catégories','Popular categories':'Catégories populaires'},
 hi:{'AI & Search':'एआई और खोज','Flights':'उड़ानें','Find it faster. Compare it better.':'तेज़ी से खोजें। बेहतर तुलना करें।','Worldwide':'दुनिया भर','AI assisted':'एआई सहायक','Voice + Chat':'आवाज़ + चैट','Browse categories':'श्रेणियाँ देखें','Popular categories':'लोकप्रिय श्रेणियाँ'},
 zh:{'AI & Search':'AI 与搜索','Flights':'航班','Find it faster. Compare it better.':'更快找到，更好比较。','Worldwide':'全球','AI assisted':'AI 辅助','Voice + Chat':'语音 + 聊天','Browse categories':'浏览分类','Popular categories':'热门分类'}
};
function api(path){return location.hostname==='seekveraglobal.com'||location.hostname==='www.seekveraglobal.com'||location.hostname.endsWith('workers.dev')?path:'https://seekvera-main.seekvera-global.workers.dev'+path}
function lang(){let v=document.getElementById('lang')?.value||document.documentElement.lang||navigator.language||'en';if(v==='auto')v=navigator.language||'en';return String(v).toLowerCase().split('-')[0]||'en'}
function langName(code){try{return new Intl.DisplayNames(['en'],{type:'language'}).of(code)||code}catch{return code}}
function skipNode(n){const p=n?.parentElement;return !p||p.closest(SKIP)}
function worth(s){s=String(s||'').trim();if(!s||s.length<2)return false;if(/^SEEKVERA$/i.test(s))return false;if(/^[A-Z]{3}$/.test(s))return false;if(/^[\d\s.,:+\-/%$€£₦¥₹]+$/.test(s))return false;return /[A-Za-z\u00C0-\u024F\u0400-\u052F\u0600-\u06FF\u0900-\u097F\u3040-\u30FF\u3400-\u9FFF]/.test(s)}
function capture(root=document){
 const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){if(skipNode(n))continue;const s=n.nodeValue?.trim();if(worth(s)&&!textSource.has(n))textSource.set(n,s)}
 const els=(root===document?[...document.querySelectorAll('[placeholder],[aria-label],[title]')]:[...(root.querySelectorAll?.('[placeholder],[aria-label],[title]')||[])]);
 for(const el of els){if(el.closest?.(SKIP))continue;let m=attrSource.get(el);if(!m){m={};attrSource.set(el,m)}for(const a of ['placeholder','aria-label','title']){const s=el.getAttribute?.(a)?.trim();if(worth(s)&&!(a in m))m[a]=s}}
}
function cacheKey(l,s){return l+'\u0000'+s}
function cached(l,s){return memory.get(cacheKey(l,s))||QUICK[l]?.[s]||''}
function put(l,s,v){if(v&&v.trim())memory.set(cacheKey(l,s),v.trim())}
async function batchTranslate(l,arr){if(!arr.length)return new Map();const out=new Map();for(let i=0;i<arr.length;i+=12){const batch=arr.slice(i,i+12);try{const r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:langName(l),strings:batch})});const d=await r.json().catch(()=>null);if(r.ok&&Array.isArray(d?.translations)&&d.translations.length===batch.length){batch.forEach((s,j)=>{const v=String(d.translations[j]||'').trim();if(v){put(l,s,v);out.set(s,v)}})}}catch{}}
 return out}
async function apply(){if(applying){pending=true;return}applying=true;pending=false;const my=++seq;capture(document);const l=lang();document.documentElement.lang=l;document.documentElement.dir=['ar','fa','ur','he','ps'].includes(l)?'rtl':'ltr';
 const textNodes=[],attrs=[],need=new Set();
 const w=document.createTreeWalker(document,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){if(skipNode(n))continue;const src=textSource.get(n);if(!src)continue;textNodes.push([n,src]);if(l!=='en'&&!cached(l,src))need.add(src)}
 for(const el of document.querySelectorAll('[placeholder],[aria-label],[title]')){const m=attrSource.get(el);if(!m||el.closest?.(SKIP))continue;for(const [a,src] of Object.entries(m)){attrs.push([el,a,src]);if(l!=='en'&&!cached(l,src))need.add(src)}}
 if(l!=='en'&&need.size)await batchTranslate(l,[...need]);if(my!==seq){applying=false;return}
 for(const [node,src] of textNodes){if(!node.isConnected)continue;const v=l==='en'?src:cached(l,src);if(v)node.nodeValue=node.nodeValue.replace(node.nodeValue.trim(),v)}
 for(const [el,a,src] of attrs){if(!el.isConnected)continue;const v=l==='en'?src:cached(l,src);if(v)el.setAttribute(a,v)}
 applying=false;if(pending)schedule(40)}
function schedule(ms=160){clearTimeout(timer);timer=setTimeout(apply,ms)}
function bind(){capture(document);document.addEventListener('change',e=>{if(e.target?.id==='lang'||e.target?.id==='country')schedule(220)},true);new MutationObserver(ms=>{let added=false,locale=false;for(const m of ms){if(m.type==='attributes'&&m.target===document.documentElement&&['lang','dir'].includes(m.attributeName))locale=true;for(const n of m.addedNodes||[]){if(n.nodeType===1){capture(n);added=true}}}if(locale||added)schedule(180)}).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['lang','dir']});schedule(0)}
if(document.readyState==='loading'){capture(document);document.addEventListener('DOMContentLoaded',bind,{once:true})}else bind();
window.SEEKVERA_LOCALE_GUARD_R9={apply,schedule,version:VERSION};
})();
