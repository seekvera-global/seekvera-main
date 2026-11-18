/* SEEKVERA R75 universal locale runtime: one country -> one language/currency -> every visible UI string. */
(()=>{'use strict';
if(window.__SEEKVERA_I18N_R32)return;window.__SEEKVERA_I18N_R32=true;
const VERSION='20261118-r125-global-quick-v31';
const SRC=new WeakMap(),ATTRSRC=new WeakMap(),OPTIONSRC=new WeakMap(),MEM=new Map(),PACKS=new Map(),PACKING=new Map(),PACK_VALUES=new Map(),RENDERED_TEXT=new WeakMap(),RENDERED_ATTR=new WeakMap();
const RTL=new Set(['ar','fa','ur','he','ps','dv']);
const ATTRS=['placeholder','aria-label','title'];
const SKIP='script,style,noscript,code,pre,svg,textarea,[data-no-translate],[data-user-content],.ai-msg,.sv-global-msg';
const INITIAL_AI='I’m the SEEKVERA AI assistant. Tell me what you need and I’ll help you find the right section, compare options or search worldwide.';
const QUICK={ar:{
'GLOBAL AI MARKETPLACE':'سوق عالمي بالذكاء الاصطناعي','SEEKVERA quick tools':'أدوات SEEKVERA السريعة','Country / Region':'الدولة / المنطقة','Language':'اللغة','Currency':'العملة','Install':'تثبيت','Post Ad':'أضف إعلاناً','Back':'رجوع','Page navigation':'التنقل بين الصفحات','Voice reply':'الرد الصوتي','Voice':'الصوت',
'Worldwide':'العالم كله','AI assisted':'بمساعدة الذكاء الاصطناعي','Voice + Chat':'صوت + دردشة','Find it faster. Compare it better.':'اعثر عليه أسرع. قارنه بشكل أفضل.','Hotels, homes, cars, jobs, products, suppliers, media and services — from one global marketplace.':'فنادق ومنازل وسيارات ووظائف ومنتجات وموردون وإعلام وخدمات — من سوق عالمي واحد.','Near Me':'بالقرب مني','My Country':'بلدي','Chat · Voice · Camera · Attach':'دردشة · صوت · كاميرا · إرفاق','Online':'متصل','Message SEEKVERA AI…':'راسل ذكاء SEEKVERA…','Choose a country once and SEEKVERA switches the app language, currency, AI context and country-aware sections automatically. You can still change language manually if you want.':'اختر دولة مرة واحدة، وستغيّر SEEKVERA تلقائياً لغة التطبيق والعملة وسياق الذكاء الاصطناعي والأقسام المرتبطة بالدولة. ويمكنك تغيير اللغة يدوياً متى أردت.',
'AI & Search':'الذكاء والبحث','Flights':'الرحلات الجوية','Popular categories':'الأقسام الشائعة','Clear visual routes, like a marketplace — no empty cards.':'مسارات واضحة مثل السوق — بدون بطاقات فارغة.','ALL CATEGORIES →':'كل الأقسام ←','Live marketplace':'السوق المباشر','Approved real listings only.':'إعلانات حقيقية معتمدة فقط.','OPEN MARKETPLACE →':'افتح السوق ←','Loading approved listings…':'جارٍ تحميل الإعلانات المعتمدة…','No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'لا توجد حالياً إعلانات سوق مباشرة معتمدة. لا تنشئ SEEKVERA إعلانات وهمية.','No approved live marketplace listings are available right now':'لا توجد حالياً إعلانات سوق مباشرة معتمدة.','SEEKVERA does not generate fake listings':'لا تنشئ SEEKVERA إعلانات وهمية.',
'Request anything':'اطلب أي شيء','Tell SEEKVERA what you need anywhere in the world.':'أخبر SEEKVERA بما تحتاج إليه في أي مكان في العالم.','Country / anywhere':'الدولة / أي مكان','City / area':'المدينة / المنطقة','Describe what you need':'اشرح ما تحتاج إليه','Send request':'إرسال الطلب','Find, compare, choose — worldwide.':'ابحث وقارن واختر — حول العالم.','Find, compare, choose — worldwide':'ابحث وقارن واختر — حول العالم','About':'حول','Privacy':'الخصوصية','Terms':'الشروط','Contact':'تواصل','Disclosure':'الإفصاح','Business':'الأعمال','Cars':'السيارات',
'Audio could not play. Tap the speaker to retry.':'تعذّر تشغيل الصوت. اضغط على مكبّر الصوت للمحاولة مجدداً.',
'I could not understand that audio yet — tap the microphone and try again.':'لم أتمكّن من فهم التسجيل — اضغط على الميكروفون وحاول مجدداً.',
'Understanding your speech…':'جارٍ فهم كلامك…',
'Please check the words, then tap Send.':'تأكّد من الكلام، وبعدين اضغط إرسال.',
'Voice recognition is not supported in this browser.':'التعرّف على الصوت غير مدعوم في هذا المتصفّح.',
[INITIAL_AI]:'أنا مساعد SEEKVERA بالذكاء الاصطناعي. أخبرني بما تحتاج إليه وسأساعدك في الوصول إلى القسم المناسب ومقارنة الخيارات أو البحث حول العالم.'
},fr:{
'Back':'Retour','Page navigation':'Navigation des pages','Voice reply':'Réponse vocale','Voice':'Voix',
'Audio could not play. Tap the speaker to retry.':'Impossible de lire le son. Appuyez sur le haut-parleur pour réessayer.',
'I could not understand that audio yet — tap the microphone and try again.':'Je n’ai pas compris cet enregistrement — appuyez sur le microphone et réessayez.',
'Understanding your speech…':'Analyse de vos paroles…',
'Please check the words, then tap Send.':'Vérifiez le texte, puis appuyez sur Envoyer.',
'Voice recognition is not supported in this browser.':'La reconnaissance vocale n’est pas prise en charge par ce navigateur.'
},
// Provisional Finnish quick UI labels; native review remains required.
fi:{
'Back':'Takaisin',
'Page navigation':'Sivunavigointi',
'Voice reply':'Äänivastaus',
'Voice':'Ääni'
},
// Provisional German quick UI labels; native review remains required.
de:{
'Back':'Zurück',
'Page navigation':'Seitennavigation',
'Voice reply':'Sprachantwort',
'Voice':'Stimme'
},
// Provisional Japanese quick UI labels; native review remains required.
ja:{
'Back':'戻る',
'Page navigation':'ページナビゲーション',
'Voice reply':'音声で返信',
'Voice':'音声'
},
// Provisional Thai subscription labels; native review remains required.
th:{
'Back':'กลับ',
'Page navigation':'การนำทางหน้าเว็บ',
'Voice reply':'การตอบกลับด้วยเสียง',
'Voice':'เสียง',
'Business Yearly':'แพ็กเกจธุรกิจรายปี',
'Business Monthly':'แพ็กเกจธุรกิจรายเดือน'
},
// Provisional Zulu quick UI, marketplace and logistics labels; native review remains required.
zu:{
'Back':'Emuva',
'Page navigation':'Ukuzulazula kwamakhasi',
'Voice reply':'Impendulo yezwi',
'Voice':'Izwi',
'GLOBAL AI MARKETPLACE':'Imakethe ye-AI yomhlaba wonke',
'Courier & last mile':'Ukuthumela nokuletha impahla esigabeni sokugcina'
},
// Provisional Korean quick UI labels; native review remains required.
ko:{
'Back':'뒤로',
'Page navigation':'페이지 탐색',
'Voice reply':'음성 답변',
'Voice':'음성'
},
// Provisional Italian quick UI labels; native review remains required.
it:{
'Back':'Indietro',
'Page navigation':'Navigazione tra le pagine',
'Voice reply':'Risposta vocale',
'Voice':'Voce'
},
// Provisional Swahili quick UI labels; native review remains required.
sw:{'Back':'Rudi nyuma','Page navigation':'Urambazaji wa kurasa','Voice reply':'Jibu la sauti','Voice':'Sauti'},
// Provisional Persian quick UI labels; native review remains required.
fa:{'Back':'بازگشت','Page navigation':'پیمایش صفحات','Voice reply':'پاسخ صوتی','Voice':'صدا'},
// Provisional Polish quick UI labels; native review remains required.
pl:{'Back':'Wstecz','Page navigation':'Nawigacja stron','Voice reply':'Odpowiedź głosowa','Voice':'Głos'},
// Provisional Dutch quick UI labels; native review remains required.
nl:{'Back':'Terug','Page navigation':'Paginanavigatie','Voice reply':'Spraakantwoord','Voice':'Stem'},
// Provisional Malay quick UI labels; native review remains required.
ms:{'Back':'Kembali','Page navigation':'Navigasi halaman','Voice reply':'Balasan suara','Voice':'Suara'},
// Provisional Hausa quick UI labels; native review remains required.
ha:{'Back':'Komawa baya','Page navigation':'Kewayawa shafuka','Voice reply':'Amsar murya','Voice':'Murya'},
// Provisional Yoruba quick UI labels; native review remains required.
yo:{'Back':'Pada sẹhin','Page navigation':'Lilọ kiri oju-iwe','Voice reply':'Idahun ohun','Voice':'Ohùn'},
// Provisional Igbo quick UI labels; native review remains required.
ig:{'Back':'Laghachi azụ','Page navigation':'Ịgagharị peeji','Voice reply':'Nzaghachi olu','Voice':'Olu'},
// Provisional Amharic quick UI labels; native review remains required.
am:{'Back':'ተመለስ','Page navigation':'የገጽ አሰሳ','Voice reply':'የድምፅ መልስ','Voice':'ድምፅ'},
// Provisional Hebrew quick UI labels; native review remains required.
he:{'Back':'חזרה','Page navigation':'ניווט בעמודים','Voice reply':'תשובה קולית','Voice':'קול'},
// Provisional Ukrainian quick UI labels; native review remains required.
uk:{'Back':'Назад','Page navigation':'Навігація сторінками','Voice reply':'Голосова відповідь','Voice':'Голос'},
es:{
'Back':'Volver','Page navigation':'Navegación de páginas','Voice reply':'Respuesta de voz','Voice':'Voz'
},zh:{
'Back':'返回','Page navigation':'页面导航','Voice reply':'语音回复','Voice':'语音'
},pt:{
'Back':'Voltar',
'Page navigation':'Navegação de páginas',
'Voice reply':'Resposta por voz',
'Voice':'Voz'
},
// Provisional Indonesian quick UI labels; native review remains required.
id:{
'Back':'Kembali',
'Page navigation':'Navigasi halaman',
'Voice reply':'Balasan suara',
'Voice':'Suara'
},
// Provisional Filipino quick UI labels; native review remains required.
fil:{
'Back':'Bumalik','Page navigation':'Pag-navigate sa pahina','Voice reply':'Sagot sa boses','Voice':'Boses',
'Country / Region':'Bansa / Rehiyon','Language':'Wika','Currency':'Pera',
'OPEN MARKETPLACE →':'Buksan ang pamilihan →',
'GLOBAL AI MARKETPLACE':'Pamilihang pandaigdig na pinapagana ng AI',
'🏙️ City break':'🏙️ Maikling bakasyon sa lungsod',
'GLOBAL AUTO SEARCH':'Pandaigdigang paghahanap ng sasakyan',
'CROSS-BORDER LOGISTICS':'Logistikang tumatawid sa mga hangganan',
'Venue / hotel Wi‑Fi QR':'QR para sa Wi‑Fi ng lugar o hotel',
'Auto Recharge':'Awtomatikong pag-recharge',
'Zero‑Cost Mode':'Mode na walang gastos',
'RFQ / supplier sourcing':'Kahilingan sa presyo / paghahanap ng tagapagtustos'
},
// Provisional Danish quick UI and feature labels; native review remains required.
da:{
'Back':'Tilbage',
'Page navigation':'Sidenavigation',
'Voice reply':'Stemmesvar',
'Voice':'Stemme',
'Find Wi-Fi →':'Søg efter Wi-Fi →',
'Find catering':'Søg efter catering',
'AI Voice Agent':'AI-stemmeassistent'
},
// Provisional Sesotho quick UI, marketplace and logistics labels; native review remains required.
st:{
'Back':'Khutlela morao',
'Page navigation':'Tsamaiso ea maqephe',
'Voice reply':'Karabo ea lentsoe',
'Voice':'Lentsoe',
'Free / Public Wi-Fi Finder':'Sesebelisoa sa ho fumana Wi-Fi ea mahala kapa ea sechaba',
'RFQ / supplier sourcing':'Kopo ea theko / ho fumana barekisi',
'Delivery & Courier':'Phano le litšebeletso tsa ba tsamaisang thepa'
},
// Provisional Romanian travel/business labels; native review remains required.
ro:{
'Back':'Înapoi',
'Page navigation':'Navigarea paginilor',
'Voice reply':'Răspuns vocal',
'Voice':'Voce',
'🏙️ City break':'🏙️ Escapadă urbană',
'Business Monthly':'Plan de afaceri lunar'
},
// Provisional Hungarian quick UI and travel labels; native review remains required.
hu:{
'Back':'Vissza',
'Page navigation':'Oldalnavigáció',
'Voice reply':'Hangos válasz',
'Voice':'Hang',
'← Travel Hub':'← Utazási központ'
},
// Provisional Maltese quick UI and travel labels; native review remains required.
mt:{
'Back':'Lura',
'Page navigation':'Navigazzjoni tal-paġni',
'Voice reply':'Tweġiba bil-vuċi',
'Voice':'Vuċi',
'🏙️ City break':'🏙️ Vjaġġ qasir fil-belt'
},
// Provisional Greek AI label; native review remains required.
el:{
'Back':'Πίσω','Page navigation':'Πλοήγηση σε σελίδα','Voice reply':'Απάντηση με φωνή','Voice':'Φωνή',
'AI Voice Agent':'Φωνητικός βοηθός AI'
},
// Provisional Czech navigation and AI labels; native review remains required.
cs:{
'Back':'Zpět',
'Page navigation':'Navigace stránek',
'Voice reply':'Hlasová odpověď',
'Voice':'Hlas',
'AI Voice Agent':'Hlasový asistent AI'
},
// Provisional Slovak quick UI and AI labels; native review remains required.
sk:{
'Back':'Späť',
'Page navigation':'Navigácia stránok',
'Voice reply':'Hlasová odpoveď',
'Voice':'Hlas',
'AI Voice Agent':'Hlasový asistent AI'
},
// Provisional Swedish quick UI and AI labels; native review remains required.
sv:{
'Back':'Tillbaka',
'Page navigation':'Sidnavigering',
'Voice reply':'Röstsvar',
'Voice':'Röst',
'AI Voice Agent':'AI-röstassistent'
},
// Provisional Norwegian quick UI, AI and business labels; native review remains required.
no:{
'Back':'Tilbake',
'Page navigation':'Sidenavigasjon',
'Voice reply':'Talesvar',
'Voice':'Stemme',
'AI Voice Agent':'AI-stemmeassistent',
'Business Monthly':'Månedlig bedriftsplan'
},
// Provisional Afrikaans quick UI and AI labels; native review remains required.
af:{
'Back':'Terug',
'Page navigation':'Bladsynavigasie',
'Voice reply':'Stemantwoord',
'Voice':'Stem',
'AI Voice Agent':'KI-stemassistent'
},
// Provisional Setswana UI labels; not linguistically certified. Native review remains required.
tn:{
'Back':'Boela kwa morago',
'Page navigation':'Tsamaiso ya ditsebe',
'Voice reply':'Karabo ya lentswe',
'Voice':'Lentswe'
},
// Provisional Hindi quick UI labels; native review remains required.
hi:{
'Back':'वापस',
'Page navigation':'पृष्ठ नेविगेशन',
'Voice reply':'आवाज़ में जवाब',
'Voice':'आवाज़'
},
// Provisional Russian quick UI labels; native review remains required.
ru:{
'Back':'Назад',
'Page navigation':'Навигация по страницам',
'Voice reply':'Голосовой ответ',
'Voice':'Голос'
},
// Provisional Urdu quick UI labels; native review remains required.
ur:{
'Back':'واپس',
'Page navigation':'صفحات پر نیویگیشن',
'Voice reply':'صوتی جواب',
'Voice':'آواز',
'Business Yearly':'سالانہ کاروباری منصوبہ',
'Business Monthly':'ماہانہ کاروباری منصوبہ'
},
// Provisional Vietnamese quick UI labels; native review remains required.
vi:{
'Back':'Quay lại',
'Page navigation':'Điều hướng trang',
'Voice reply':'Trả lời bằng giọng nói',
'Voice':'Giọng nói'
},
// Provisional Bangla quick UI labels; native review remains required.
bn:{
'Back':'পেছনে',
'Page navigation':'পৃষ্ঠা নেভিগেশন',
'Voice reply':'কণ্ঠে উত্তর',
'Voice':'ভয়েস'
},
// Provisional Bulgarian quick UI labels; native review remains required.
bg:{
'Back':'Назад',
'Page navigation':'Навигация по страниците',
'Voice reply':'Гласов отговор',
'Voice':'Глас'
},
// Provisional Croatian quick UI labels; native review remains required.
hr:{
'Back':'Natrag',
'Page navigation':'Navigacija po stranicama',
'Voice reply':'Glasovni odgovor',
'Voice':'Glas'
},
// Provisional Serbian quick UI labels; native review remains required.
sr:{
'Back':'Назад',
'Page navigation':'Навигација по страницама',
'Voice reply':'Гласовни одговор',
'Voice':'Глас'
},
// Provisional Slovenian quick UI labels; native review remains required.
sl:{
'Back':'Nazaj',
'Page navigation':'Navigacija po straneh',
'Voice reply':'Glasovni odgovor',
'Voice':'Glas'
},
// Provisional Lithuanian quick UI labels; native review remains required.
lt:{
'Back':'Atgal',
'Page navigation':'Puslapių naršymas',
'Voice reply':'Atsakymas balsu',
'Voice':'Balsas'
},
// Provisional Latvian quick UI labels; native review remains required.
lv:{
'Back':'Atpakaļ',
'Page navigation':'Lapu navigācija',
'Voice reply':'Balss atbilde',
'Voice':'Balss'
},
// Provisional Estonian quick UI labels; native review remains required.
et:{
'Back':'Tagasi',
'Page navigation':'Lehe navigatsioon',
'Voice reply':'Kõne vastus',
'Voice':'Kõne'
},
// Provisional Catalan quick UI labels; native review remains required.
ca:{
'Back':'Enrere',
'Page navigation':'Navegació de pàgina',
'Voice reply':'Resposta de veu',
'Voice':'Veu'
},
// Provisional Icelandic quick UI labels; native review remains required.
is:{
'Back':'Til baka',
'Page navigation':'Síðuleiðsögn',
'Voice reply':'Raddsvör',
'Voice':'Rödd'
},
// Provisional Albanian quick UI labels; native review remains required.
sq:{
'Back':'Kthehu',
'Page navigation':'Navigimi në faqe',
'Voice reply':'Përgjigje me zë',
'Voice':'Zëri'
},
// Provisional Macedonian quick UI labels; native review remains required.
mk:{
'Back':'Назад',
'Page navigation':'Навигација на страна',
'Voice reply':'Гласен одговор',
'Voice':'Глас'
},
// Provisional Georgian quick UI labels; native review remains required.
ka:{
'Back':'უკან',
'Page navigation':'გვერდის ნავიგაცია',
'Voice reply':'ხმის პასუხი',
'Voice':'ხმა'
},
// Provisional Armenian quick UI labels sourced from the existing candidate pack; native review remains required.
hy:{
'Back':'Վերադարձ',
'Page navigation':'Էջի նավիգացիա',
'Voice reply':'Ձայնային պատասխան',
'Voice':'Ձայն'
},
// Provisional Azerbaijani quick UI labels normalized to Azerbaijani orthography from the existing candidate pack; native review remains required.
az:{
'Back':'Geri',
'Page navigation':'Səhifə naviqasiyası',
'Voice reply':'Səsli cavab',
'Voice':'Səs'
},
// Provisional Kazakh quick UI labels sourced from the existing candidate pack; native review remains required.
kk:{
'Back':'Артқа',
'Page navigation':'Бет навигациясы',
'Voice reply':'Дыбыстық жауап',
'Voice':'Дыбыс'
},
// Provisional Kyrgyz quick UI labels; existing candidate values for these four labels were malformed, so these are conservative local UI wording and require native review.
ky:{
'Back':'Артка',
'Page navigation':'Барак навигациясы',
'Voice reply':'Үн менен жооп',
'Voice':'Үн'
},
// Provisional Uzbek quick UI labels sourced from the existing candidate pack; native review remains required.
uz:{
'Back':'Orqaga',
'Page navigation':'Sahifa navigatsiyasi',
'Voice reply':'Ovoz javobi',
'Voice':'Ovoz'
},
// Provisional Tajik quick UI labels; malformed candidate values were not reused, and native review remains required.
tg:{
'Back':'Бозгашт',
'Page navigation':'Навигатсияи саҳифаҳо',
'Voice reply':'Ҷавоби овозӣ',
'Voice':'Овоз'
},
// Provisional Turkmen quick UI labels; wording is provisional and requires native review.
tk:{
'Back':'Yza',
'Page navigation':'Sahypa navigasiýasy',
'Voice reply':'Sesli jogap',
'Voice':'Ses'
},
// Provisional Nepali quick UI labels. Candidate values for Back/Voice were malformed; these operational labels remain provisional pending native review.
ne:{
'Back':'पछाडि',
'Page navigation':'पृष्ठ नेभिगेसन',
'Voice reply':'आवाजमा जवाफ',
'Voice':'आवाज'
},
// Provisional Sinhala quick UI labels sourced from the existing candidate pack; native review remains required.
si:{
'Back':'ආපසු',
'Page navigation':'පිටු සංචාලනය',
'Voice reply':'හඬ පිළිතුර',
'Voice':'හඬ'
}
};
// Provisional quota-neutral overrides for the exact R125 UI leaks. Native review remains required.
const R125_PROVISIONAL={
fy:{
'GLOBAL AI MARKETPLACE':'WRÂLDWIDE AI-MERKPLAK',
'ENTERTAINMENT · WORLDWIDE':'FERDIVEDAASJE · WRÂLDWIID',
'AI Voice Agent':'AI-stimassistint',
'Business Monthly':'Moanliks bedriuwsplan'
},
lb:{
'OPEN MARKETPLACE →':'MAARTPLAZ OPMAACHEN →',
'GLOBAL AI MARKETPLACE':'WELTWÄITE KI-MAARTPLAZ',
'Import & Export':'Import an Export',
'← Travel Hub':'← Rees-Hub',
'GLOBAL AUTO SEARCH':'WELTWÄIT AUTOSSICH',
'Import, Export & Sourcing':'Import, Export & Beschaffung',
'Business Software':'Geschäftssoftware',
'Home Services':'Hausdéngschter'
},
lo:{
'AI Voice Agent':'ຜູ້ຊ່ວຍສຽງ AI',
'Email/Gmail background autopilot:':'ລະບົບອັດຕະໂນມັດສຳລັບອີເມວ/Gmail ໃນເບື້ອງຫຼັງ:'
},
mg:{
'← Travel Hub':"← Foiben'ny dia",
'Import, Export & Sourcing':'Fanafarana, fanondranana ary fitadiavana mpamatsy',
'AI Voice Agent':'Mpanampy feo AI',
'VERIFY + PAUSE':'Hamarino + Atsaharo',
'Email/Gmail background autopilot:':"Fampandehanana mandeha ho azy any ambadika ho an'ny mailaka/Gmail:"
},
rm:{
'Fashion & Beauty':'Moda e bellezza',
'Safety & etiquette':'Segirezza e cumportament',
'← Travel Hub':'← Center da viadi',
'← Back to search':'← Enavos a la tschertga',
'Shopping & Electronics':'Acquist ed electronica',
'Privacy first':'Protecziun da datas avant tut',
'Check My Phone':'Controllar mes telefon',
'Master controls':'Controlls principals',
'Home Services':'Servetschs per la chasa',
'Utilities & Bills':'Servetschs publics e quintanzas',
'Hotels & Marketplace':'Hotels e martgà'
},
rw:{
'VERIFY + PAUSE':'GENZURA + HAGARIKA'
},
tn:{
'Solar & Energy':'Matla a letsatsi le eneji'
},
tr:{
'Back':'Geri',
'Page navigation':'Sayfa gezintisi',
'Voice reply':'Sesli yanıt',
'Voice':'Ses'
}
};

function api(p){const h=location.hostname;return(h==='seekveraglobal.com'||h==='www.seekveraglobal.com'||h.endsWith('workers.dev'))?p:'https://seekvera-main.seekvera-global.workers.dev'+p}
function norm(v){v=String(v||'').trim().toLowerCase().replace('_','-');if(!v||v==='auto')v=String(navigator.language||'en').toLowerCase();return v.split('-')[0]||'en'}
function lang(){return norm(document.querySelector('#lang')?.value||window.SEEKVERA_LOCALE_STATE?.language||document.documentElement.lang||'en')}
function langName(l){try{return new Intl.DisplayNames(['en'],{type:'language'}).of(l)||l}catch{return l}}
function canonical(s){return String(s||'').replace(/\s+/g,' ').trim()}
function worth(s){s=String(s||'').trim();if(!s||s.length<2||s.length>1200)return false;if(/^SEEKVERA$/i.test(s))return false;if(/^(https?:\/\/|www\.)/i.test(s)||/\b\S+@\S+\.\S+\b/.test(s))return false;if(/^[A-Z0-9]{2,5}$/.test(s))return false;if(/^[\d\s.,:+\-/%$€£₦¥₹]+$/.test(s))return false;return /[A-Za-z\u00C0-\u024F\u0400-\u052F\u0600-\u06FF\u0900-\u097F\u3040-\u30FF\u3400-\u9FFF]/.test(s)}
function skipped(n){const p=n?.parentElement;if(!p||p.closest(SKIP))return true;const s=p.closest?.('select');return !!s&&['country','lang','currency'].includes(s.id)}
function plainKey(s){return String(s||'').trim().replace(/^[^\p{L}\p{N}]+/u,'').replace(/[^\p{L}\p{N})]+$/u,'').trim()}
function canonicalText(n){
 const opt=n?.parentElement?.closest?.('option');if(!opt)return canonical(n?.nodeValue);
 const sel=opt.closest('select');if(!sel||['country','lang','currency'].includes(sel.id))return canonical(n?.nodeValue);
 let src=OPTIONSRC.get(opt)||opt.dataset?.svSource||'';
 if(!src){src=String(n?.nodeValue||opt.textContent||'').trim();if(src){OPTIONSRC.set(opt,src);try{opt.dataset.svSource=src}catch{}if(!opt.hasAttribute('value'))opt.setAttribute('value',src)}}
 return src||String(n?.nodeValue||'').trim();
}
function capture(root=document){
 const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){if(skipped(n))continue;const s=canonicalText(n);if(worth(s)&&!SRC.has(n))SRC.set(n,s)}
 const els=root===document?[...document.querySelectorAll('[placeholder],[aria-label],[title]')]:[...(root.querySelectorAll?.('[placeholder],[aria-label],[title]')||[])];
 for(const el of els){if(el.closest?.(SKIP))continue;let m=ATTRSRC.get(el);if(!m){m={};ATTRSRC.set(el,m)}for(const a of ATTRS){const s=el.getAttribute?.(a)?.trim();if(worth(s)&&!(a in m))m[a]=s}}
}
function k(l,s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return'sv_r32_'+VERSION+'_'+l+'_'+(h>>>0).toString(36)}
const EMBEDDED_TRANSLATION_TERMS=['Auto Recharge','Live marketplace','No stranger chat','Business Software'];
function rawGet(l,s){s=canonical(s);const q=QUICK[l]?.[s]||(typeof R125_PROVISIONAL!=='undefined'?R125_PROVISIONAL[l]?.[s]:'');if(q)return q;const m=MEM.get(l+'\u0000'+s);if(m){const ps=plainKey(s);if(ps!==s&&plainKey(m)===ps){const translated=MEM.get(l+'\u0000'+ps);if(translated&&translated!==ps)return s.replace(ps,translated)}return m;}try{return localStorage.getItem(k(l,s))||''}catch{return''}}
function get(l,s){s=canonical(s);let value=rawGet(l,s);if(!value)return'';for(const term of EMBEDDED_TRANSLATION_TERMS){if(s!==term&&value.includes(term)){const localized=rawGet(l,term);if(localized&&localized!==term)value=value.split(term).join(localized)}}return value}
function put(l,s,v){s=canonical(s);v=String(v||'').trim();if(!v)return;MEM.set(l+'\u0000'+s,v);try{localStorage.setItem(k(l,s),v)}catch{}}
async function loadPack(l){
 l=norm(l);if(l==='en')return true;if(PACKS.has(l))return true;if(PACKING.has(l))return PACKING.get(l);
 const task=(async()=>{try{const r=await fetch('/i18n-r32/'+encodeURIComponent(l)+'.json?v='+VERSION,{cache:'no-cache'});if(!r.ok)throw Error('pack '+r.status);const d=await r.json();const t=d?.translations;if(!t||typeof t!=='object')throw Error('invalid pack');const localizedValues=new Set();for(const [src,v] of Object.entries(t)){const val=String(v||'').trim();if(!val)continue;MEM.set(l+'\u0000'+canonical(src),val);localizedValues.add(canonical(val));const ps=plainKey(src),pv=plainKey(val);if(ps&&pv&&ps!==src&&!MEM.has(l+'\u0000'+ps))MEM.set(l+'\u0000'+ps,pv)}PACK_VALUES.set(l,localizedValues);PACKS.set(l,d);document.documentElement.dataset.seekveraPackReady=l;window.dispatchEvent(new CustomEvent('seekvera:packready',{detail:{language:l}}));return true}catch(e){console.warn('SEEKVERA local language pack unavailable',l,e);return false}finally{PACKING.delete(l)}})();
 PACKING.set(l,task);return task
}
function markAttr(el,a,v){let m=RENDERED_ATTR.get(el);if(!m){m={};RENDERED_ATTR.set(el,m)}m[a]=String(v||'').trim()}
function valid(v,src){v=String(v||'').trim();return !!v&&!/^undefined|null$/i.test(v)&&!/^\[object Object\]$/i.test(v)}
const UI_TRANSLATE_BLOCK_KEY='sv_ui_translate_blocked_r19',UI_TRANSLATE_LOCK_KEY='sv_ui_translate_lock_r19';
let CLOUD_TRANSLATE_BLOCKED=false,CLOUD_TRANSLATE_QUEUE=Promise.resolve();
try{CLOUD_TRANSLATE_BLOCKED=sessionStorage.getItem(UI_TRANSLATE_BLOCK_KEY)==='1'}catch{}
function blockCloudTranslate(){CLOUD_TRANSLATE_BLOCKED=true;try{sessionStorage.setItem(UI_TRANSLATE_BLOCK_KEY,'1')}catch{}}
async function cloudTranslate(l,batch){
 const run=async()=>{
  if(CLOUD_TRANSLATE_BLOCKED)return null;
  let lockToken='';
  try{
   if(sessionStorage.getItem(UI_TRANSLATE_BLOCK_KEY)==='1'){CLOUD_TRANSLATE_BLOCKED=true;return null}
   const held=Number(sessionStorage.getItem(UI_TRANSLATE_LOCK_KEY)||0);
   if(held&&Date.now()-held<20000)return null;
   lockToken=String(Date.now());
   sessionStorage.setItem(UI_TRANSLATE_LOCK_KEY,lockToken);
  }catch{}
  try{
   const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),15000);
   let r;
   try{r=await fetch(api('/api/ui-translate'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:langName(l),strings:batch}),signal:ctl.signal,cache:'no-store'})}
   finally{clearTimeout(to)}
   const d=await r.json().catch(()=>null),reason=[d?.reason,d?.error].filter(Boolean).join(' ');
   if(r.status===429||r.status===503||/(daily_free_ai_limit|provider_rate_limited|all_translation_backends_unavailable|\b429\b|rate.?limit|too many requests)/i.test(reason)){blockCloudTranslate();return null}
   if(r.ok&&Array.isArray(d?.translations)&&d.translations.length===batch.length){const vals=d.translations.map((v,i)=>valid(v,batch[i])?String(v).trim():'');if(vals.some(Boolean))return vals}
  }catch{}
  finally{if(lockToken)try{if(sessionStorage.getItem(UI_TRANSLATE_LOCK_KEY)===lockToken)sessionStorage.removeItem(UI_TRANSLATE_LOCK_KEY)}catch{}}
  return null;
 };
 const task=CLOUD_TRANSLATE_QUEUE.then(run,run);
 CLOUD_TRANSLATE_QUEUE=task.then(()=>null,()=>null);
 return task;
}
function alreadyLocalizedValue(l,s){const language=norm(l),value=canonical(s);if(PACK_VALUES.get(language)?.has(value))return true;if(Object.values(QUICK[language]||{}).some(v=>canonical(v)===value))return true;const provisional=typeof R125_PROVISIONAL!=='undefined'?R125_PROVISIONAL[language]:null;return Object.values(provisional||{}).some(v=>canonical(v)===value)}
async function translate(l,arr){await loadPack(l);const unique=[...new Set(arr.filter(s=>worth(s)&&!get(l,s)&&!alreadyLocalizedValue(l,s)))];if(!unique.length)return false;let changed=false;const groups=[];for(let i=0;i<unique.length;i+=14)groups.push(unique.slice(i,i+14));for(const batch of groups){if(CLOUD_TRANSLATE_BLOCKED)break;const vals=await cloudTranslate(l,batch);if(CLOUD_TRANSLATE_BLOCKED)break;if(vals)batch.forEach((s,j)=>{if(valid(vals[j],s)){put(l,s,vals[j]);changed=true}})}return changed}
function setText(n,src,l){const v=l==='en'?src:(get(l,src)||src);const raw=n.nodeValue||'',t=raw.trim(),next=t?raw.replace(t,v):v;RENDERED_TEXT.set(n,String(next).trim());if(next!==raw)n.nodeValue=next;return l==='en'||!!get(l,src)}
function setAttr(el,a,src,l){const v=l==='en'?src:(get(l,src)||src);markAttr(el,a,v);if(el.getAttribute(a)!==v)el.setAttribute(a,v);return l==='en'||!!get(l,src)}
let seq=0,timer=0,applying=false;const BG_TRANSLATING=new Set();
async function apply(){const my=++seq,l=lang();if(l!=='en'){await loadPack(l);if(my!==seq)return}applying=true;document.documentElement.lang=l;document.documentElement.dir=RTL.has(l)?'rtl':'ltr';capture(document);const need=[];
 for(const [n,src] of entriesText()){if(!n.isConnected)continue;if(l!=='en'&&!get(l,src))need.push(src);setText(n,src,l)}
 for(const [el,m] of entriesAttr()){if(!el.isConnected)continue;for(const [a,src] of Object.entries(m)){if(l!=='en'&&!get(l,src))need.push(src);setAttr(el,a,src,l)}}
 const ai=document.querySelector('#aiMessages .ai-msg.bot:first-child');if(ai&&ai.textContent?.trim()===INITIAL_AI){if(l==='en')ai.textContent=INITIAL_AI;else{const q=get(l,INITIAL_AI);if(q)ai.textContent=q;else need.push(INITIAL_AI)}}
 document.documentElement.dataset.seekveraI18nReady=l;document.documentElement.dataset.seekveraI18nVersion=VERSION;applying=false;
 if(l!=='en'&&need.length&&!BG_TRANSLATING.has(l)){BG_TRANSLATING.add(l);translate(l,need).then(changed=>{if(changed&&lang()===l)schedule(0)}).catch(()=>{}).finally(()=>{BG_TRANSLATING.delete(l)})}}
function entriesText(){const out=[];const w=document.createTreeWalker(document,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){const s=SRC.get(n);if(s&&!skipped(n))out.push([n,s])}return out}
function setAttributeSource(el,a,source){if(!el||!ATTRS.includes(a))return;const src=canonical(source);let m=ATTRSRC.get(el);if(!m){m={};ATTRSRC.set(el,m)}m[a]=src;setAttr(el,a,src,lang());schedule(0)}
function entriesAttr(){const out=[];for(const el of document.querySelectorAll('[placeholder],[aria-label],[title]')){const m=ATTRSRC.get(el);if(m)out.push([el,m])}return out}
function schedule(ms=80){clearTimeout(timer);timer=setTimeout(()=>apply().catch(()=>{}),ms)}
function boot(){capture(document);window.addEventListener('seekvera:locale-change',()=>{schedule(0);setTimeout(()=>schedule(0),250);setTimeout(()=>schedule(0),1000)});document.addEventListener('change',e=>{if(e.target?.id==='country'||e.target?.id==='lang'||e.target?.id==='currency')schedule(20)},true);new MutationObserver(ms=>{if(applying)return;let dirty=false;for(const m of ms){if(m.type==='characterData'){const n=m.target;if(!skipped(n)){const now=String(n.nodeValue||'').trim(),rendered=RENDERED_TEXT.get(n);if(rendered!==undefined&&now===rendered)continue;if(SRC.has(n)){dirty=true;continue}RENDERED_TEXT.delete(n);const src=canonicalText(n);if(worth(src)){SRC.set(n,src);dirty=true}}}else if(m.type==='attributes'){const el=m.target,a=m.attributeName;if(el&&a&&ATTRS.includes(a)&&!el.closest?.(SKIP)){const now=String(el.getAttribute(a)||'').trim(),rendered=RENDERED_ATTR.get(el)?.[a];if(rendered!==undefined&&now===rendered)continue;const known=ATTRSRC.get(el);if(known&&known[a]){dirty=true;continue}const rm=RENDERED_ATTR.get(el);if(rm)delete rm[a];if(worth(now)){let mm=ATTRSRC.get(el);if(!mm){mm={};ATTRSRC.set(el,mm)}mm[a]=now;dirty=true}}}for(const n of m.addedNodes||[]){if(n.nodeType===1){capture(n);dirty=true}else if(n.nodeType===3&&!skipped(n)){const src=canonicalText(n);if(worth(src)){SRC.set(n,src);dirty=true}}}}if(dirty)schedule(PACKS.has(lang())?0:30)}).observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:ATTRS});loadPack(lang()).then(()=>schedule(0));schedule(0);setTimeout(()=>schedule(0),400);setTimeout(()=>schedule(0),1600);setTimeout(()=>schedule(0),4200)}
capture(document);if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
window.SEEKVERA_I18N={lang,apply,schedule,setAttributeSource,t:s=>get(lang(),String(s))||String(s),version:VERSION};window.SEEKVERA_LOCALE_GUARD_R9={apply,schedule,version:VERSION};window.SEEKVERA_I18N_R32={version:VERSION,apply,schedule,lang,loadPack,packReady:l=>PACKS.has(norm(l)),packCount:()=>PACKS.size,t:s=>get(lang(),String(s))||String(s),tFor:(l,s)=>get(norm(l),String(s))||String(s),isLocalizedValue:s=>alreadyLocalizedValue(lang(),s)};
})();