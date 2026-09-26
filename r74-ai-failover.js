/* SEEKVERA R74 — multilingual, quota-safe routing overlay. */
(()=>{'use strict';
if(window.__SEEKVERA_R74_FAILOVER)return;window.__SEEKVERA_R74_FAILOVER=true;
const VERSION='20260926-r74-global-ai-failover';
const nativeFetch=window.fetch.bind(window);
const norm=s=>String(s||'').normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f\u0670]/g,'').toLowerCase();
const groups={
 travel:['hotel','flight','travel','tourism','airport','visa','فندق','سفر','رحلة','طيران','酒店','航班','旅行','होटल','उड़ान','यात्रा','ہوٹل','سفر','হোটেল','ভ্রমণ','hôtel','voyage','vuelo','viaje','otel','seyahat'],
 property:['property','house','apartment','land','rent','عقار','بيت','ارض','إيجار','房产','土地','मकान','ज़मीन','किराया','گھر','زمین','maison','terrain','casa','alquiler'],
 cars:['car','vehicle','auto','سيارة','مركبة','汽车','कार','گاڑی','voiture','coche','araba'],
 jobs:['job','career','vacancy','work','employment','وظيفة','وظائف','عمل','شغل','工作','职位','नौकरी','काम','نوکری','চাকরি','emploi','travail','trabajo','arbeit','iş'],
 shopping:['buy','shopping','product','price','shop','شراء','تسوق','购物','购买','खरीद','कीमत','خرید','acheter','comprar','kaufen'],
 business:['supplier','manufacturer','factory','wholesale','import','export','مورد','مصنع','استيراد','تصدير','供应商','工厂','आपूर्तिकर्ता','कारखाना','سپلائر','importation','exportation'],
 restaurant:['restaurant','food','cafe','coffee','مطعم','قهوة','餐厅','咖啡','रेस्तरां','खाना','ریستوران','restaurant','comida'],
 health:['hospital','clinic','pharmacy','doctor','health','مستشفى','صيدلية','طبيب','医院','医生','अस्पताल','डॉक्टर','ہسپتال','طبیب','hôpital','médecin'],
 connectivity:['wifi','wi-fi','esim','sim card','internet','mobile data','واي فاي','انترنت','شريحة','网络','互联网','इंटरनेट','वाईफाई','انٹرنیٹ'],
 education:['school','course','university','training','education','مدرسة','جامعة','دورة','学校','大学','स्कूल','विश्वविद्यालय','تعلیم'],
 media:['news','movie','music','radio','tv','أخبار','أفلام','موسيقى','新闻','电影','समाचार','فلم','موسیقی']
};
const routes={travel:'travel.html',property:'property.html',cars:'cars-auto.html',jobs:'jobs.html',shopping:'shopping.html',business:'import-export.html',restaurant:'restaurants-food.html',health:'health.html',connectivity:'connectivity.html',education:'education.html',media:'media.html',marketplace:'marketplace.html'};
function intent(q){const t=norm(q);let best='marketplace',score=0;for(const [k,words]of Object.entries(groups)){const n=words.reduce((v,w)=>v+(t.includes(norm(w))?1:0),0);if(n>score){best=k;score=n}}return best}
function sameApi(input){try{return new URL(typeof input==='string'?input:input?.url||'',location.href).pathname==='/api/ai'}catch{return false}}
window.fetch=async function(input,init){const res=await nativeFetch(input,init);if(!sameApi(input))return res;let body={};try{body=JSON.parse(String(init?.body||'{}'))}catch{}let data;try{data=await res.clone().json()}catch{return res}const q=String(body.message||body.prompt||''),cat=intent(q);if((data?.category==='general'||!data?.category)&&cat!=='marketplace'){data.category=cat;data.route=routes[cat]}if(data?.model==='seekvera-local-router'){data.ok=true;data.retryable=false;data.providerAvailable=false;data.route=data.route||routes[cat]||routes.marketplace}const headers=new Headers(res.headers);headers.set('content-type','application/json; charset=utf-8');headers.set('cache-control','no-store');headers.set('x-seekvera-release',VERSION);return new Response(JSON.stringify(data),{status:res.ok?res.status:(data?.response?200:res.status),headers})};
window.SEEKVERA_R74_FAILOVER={version:VERSION,intent,routes};
})();
