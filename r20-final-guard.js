/* SEEKVERA R20 final multilingual UI + mobile stability guard */
(()=>{'use strict';
if(window.__SEEKVERA_R20_FINAL_GUARD)return;window.__SEEKVERA_R20_FINAL_GUARD=true;
const VERSION='20260925-r20c';
const EN_DESC=new Set([
'Buy, sell and compare worldwide','Trips, transport and stays','Search flight routes','Search stays worldwide','Places and experiences','Homes, land and rentals','Vehicles, parts and auto','Local and global careers','Products and deals','Food, cafes and dining','Everyday skilled help','Machines and equipment','Boats and marine listings','Factories and suppliers','Freight, cargo and delivery','POS, accounting and SaaS','Apps and digital tools','Domains, hosting and websites','Power and energy solutions','Schools, courses and skills','Clinics, labs and pharmacies','Licensed provider discovery','Movies, music and family','Trusted media and official sources','Play inside SEEKVERA','Internet, SIM and eSIM','Public Wi‑Fi discovery','Sourcing and business missions','Nearby daily needs','Share and install SEEKVERA','Business plans and promotion'
]);
const SKIP_EN=new Set(['SEEKVERA','AI','QR','Wi‑Fi','SIM','eSIM','POS','SaaS']);
const EXTRA_TITLES={
eu:['Merkatua','Bidaiak','Hegaldiak','Hotelak','Turismoa','Higiezinak','Autoak','Lanpostuak','Erosketak','Jatetxeak eta janaria','Tokiko zerbitzuak','Ekipamendua eta makineria','Itsasontziak eta itsasoa','Inportazioa eta esportazioa','Bidalketa eta logistika','Enpresa-softwarea','Softwarea','Webguneak eta hostinga','Eguzki-energia','Hezkuntza','Osasuna','Dirua eta aseguruak','Aisialdia','Albisteak eta komunikabideak','Jokoak','Konektibitatea','Doako Wi‑Fi','AI akordio-agentea','Egunerokoa','Eskaneatu / QR','Sustapena / Negozioa'],
gl:['Mercado','Viaxes','Voos','Hoteis','Turismo','Inmobles','Coches','Emprego','Compras','Restaurantes e comida','Servizos locais','Equipos e maquinaria','Barcos e mariña','Importación e exportación','Envíos e loxística','Software empresarial','Software','Sitios web e aloxamento','Solar e enerxía','Educación','Saúde','Diñeiro e seguros','Lecer','Novas e medios','Xogos','Conectividade','Wi‑Fi gratis','Axente de acordos con IA','Vida diaria','Escanear / QR','Promoción / Negocio'],
te:['మార్కెట్','ప్రయాణం','విమానాలు','హోటళ్లు','పర్యాటకం','ఆస్తి','కార్లు','ఉద్యోగాలు','షాపింగ్','రెస్టారెంట్లు మరియు ఆహారం','స్థానిక సేవలు','పరికరాలు మరియు యంత్రాలు','పడవలు మరియు సముద్రం','దిగుమతి మరియు ఎగుమతి','రవాణా మరియు లాజిస్టిక్స్','వ్యాపార సాఫ్ట్‌వేర్','సాఫ్ట్‌వేర్','వెబ్‌సైట్లు మరియు హోస్టింగ్','సౌర మరియు శక్తి','విద్య','ఆరోగ్యం','డబ్బు మరియు బీమా','వినోదం','వార్తలు మరియు మీడియా','ఆటలు','కనెక్టివిటీ','ఉచిత Wi‑Fi','AI డీల్ ఏజెంట్','రోజువారీ','స్కాన్ / QR','ప్రచారం / వ్యాపారం'],
ml:['വിപണി','യാത്ര','വിമാനങ്ങൾ','ഹോട്ടലുകൾ','ടൂറിസം','സ്വത്ത്','കാറുകൾ','ജോലികൾ','ഷോപ്പിംഗ്','റസ്റ്റോറന്റുകളും ഭക്ഷണവും','പ്രാദേശിക സേവനങ്ങൾ','ഉപകരണങ്ങളും യന്ത്രങ്ങളും','ബോട്ടുകളും സമുദ്രവും','ഇറക്കുമതിയും കയറ്റുമതിയും','ഷിപ്പിംഗും ലോജിസ്റ്റിക്സും','ബിസിനസ് സോഫ്റ്റ്‌വെയർ','സോഫ്റ്റ്‌വെയർ','വെബ്‌സൈറ്റുകളും ഹോസ്റ്റിംഗും','സൗരോർജവും ഊർജവും','വിദ്യാഭ്യാസം','ആരോഗ്യം','പണവും ഇൻഷുറൻസും','വിനോദം','വാർത്തകളും മാധ്യമങ്ങളും','ഗെയിമുകൾ','കണക്റ്റിവിറ്റി','സൗജന്യ Wi‑Fi','AI ഡീൽ ഏജന്റ്','ദൈനംദിനം','സ്കാൻ / QR','പ്രമോഷൻ / ബിസിനസ്'],
mr:['बाजार','प्रवास','उड्डाणे','हॉटेल्स','पर्यटन','मालमत्ता','कार आणि वाहने','नोकऱ्या','खरेदी','रेस्टॉरंट्स आणि अन्न','स्थानिक सेवा','उपकरणे आणि यंत्रसामग्री','नौका आणि सागरी','आयात आणि निर्यात','वाहतूक आणि लॉजिस्टिक्स','व्यवसाय सॉफ्टवेअर','सॉफ्टवेअर','वेबसाइट्स आणि होस्टिंग','सौर आणि ऊर्जा','शिक्षण','आरोग्य','पैसे आणि विमा','मनोरंजन','बातम्या आणि मीडिया','खेळ','कनेक्टिव्हिटी','मोफत Wi‑Fi','AI डील एजंट','दैनंदिन','स्कॅन / QR','प्रचार / व्यवसाय'],
gu:['બજાર','પ્રવાસ','ફ્લાઇટ્સ','હોટેલ્સ','પર્યટન','મિલકત','કાર અને વાહનો','નોકરીઓ','ખરીદી','રેસ્ટોરાં અને ખોરાક','સ્થાનિક સેવાઓ','ઉપકરણો અને મશીનો','નૌકા અને સમુદ્રી','આયાત અને નિકાસ','શિપિંગ અને લોજિસ્ટિક્સ','વ્યવસાય સોફ્ટવેર','સોફ્ટવેર','વેબસાઇટ્સ અને હોસ્ટિંગ','સૌર અને ઊર્જા','શિક્ષણ','આરોગ્ય','પૈસા અને વીમો','મનોરંજન','સમાચાર અને મીડિયા','રમતો','કનેક્ટિવિટી','મફત Wi‑Fi','AI ડીલ એજન્ટ','દૈનિક','સ્કેન / QR','પ્રમોશન / બિઝનેસ'],
pa:['ਮਾਰਕੀਟ','ਯਾਤਰਾ','ਉਡਾਣਾਂ','ਹੋਟਲ','ਸੈਰ-ਸਪਾਟਾ','ਜਾਇਦਾਦ','ਕਾਰਾਂ ਅਤੇ ਵਾਹਨ','ਨੌਕਰੀਆਂ','ਖਰੀਦਦਾਰੀ','ਰੈਸਟੋਰੈਂਟ ਅਤੇ ਖਾਣਾ','ਸਥਾਨਕ ਸੇਵਾਵਾਂ','ਉਪਕਰਣ ਅਤੇ ਮਸ਼ੀਨਰੀ','ਕਿਸ਼ਤੀਆਂ ਅਤੇ ਸਮੁੰਦਰੀ','ਆਯਾਤ ਅਤੇ ਨਿਰਯਾਤ','ਸ਼ਿਪਿੰਗ ਅਤੇ ਲਾਜਿਸਟਿਕਸ','ਕਾਰੋਬਾਰੀ ਸਾਫਟਵੇਅਰ','ਸਾਫਟਵੇਅਰ','ਵੈੱਬਸਾਈਟਾਂ ਅਤੇ ਹੋਸਟਿੰਗ','ਸੂਰਜੀ ਅਤੇ ਊਰਜਾ','ਸਿੱਖਿਆ','ਸਿਹਤ','ਪੈਸਾ ਅਤੇ ਬੀਮਾ','ਮਨੋਰੰਜਨ','ਖ਼ਬਰਾਂ ਅਤੇ ਮੀਡੀਆ','ਖੇਡਾਂ','ਕਨੈਕਟੀਵਿਟੀ','ਮੁਫ਼ਤ Wi‑Fi','AI ਡੀਲ ਏਜੰਟ','ਰੋਜ਼ਾਨਾ','ਸਕੈਨ / QR','ਪ੍ਰਚਾਰ / ਕਾਰੋਬਾਰ'],
ps:['بازار','سفر','الوتنې','هوټلونه','ګرځندوی','ملکیت','موټرونه','دندې','پېرود','رستورانتونه او خواړه','ځايي خدمتونه','وسایل او ماشینونه','کښتۍ او سمندر','واردات او صادرات','لېږد او لوژستیک','سوداګریز سافټویر','سافټویر','وېبپاڼې او کوربه‌توب','لمریزه انرژي','زده کړه','روغتیا','پیسې او بیمه','تفریح','خبرونه او رسنۍ','لوبې','اړیکه','وړیا Wi‑Fi','د AI معاملې استازی','ورځنی','سکین / QR','ترویج / سوداګري'],
ga:['Margadh','Taisteal','Eitiltí','Óstáin','Turasóireacht','Maoin','Carranna','Poist','Siopadóireacht','Bialanna agus bia','Seirbhísí áitiúla','Trealamh agus innealra','Báid agus muirí','Iompórtáil agus easpórtáil','Loingseoireacht agus lóistíocht','Bogearraí gnó','Bogearraí','Suíomhanna gréasáin agus óstáil','Grianfhuinneamh agus fuinneamh','Oideachas','Sláinte','Airgead agus árachas','Siamsaíocht','Nuacht agus meáin','Cluichí','Nascacht','Wi‑Fi saor in aisce','Gníomhaire margaí AI','Laethúil','Scan / QR','Cur chun cinn / Gnó'],
cy:['Marchnad','Teithio','Hedfan','Gwestai','Twristiaeth','Eiddo','Ceir','Swyddi','Siopa','Bwytai a bwyd','Gwasanaethau lleol','Offer a pheiriannau','Cychod a morol','Mewnforio ac allforio','Cludo a logisteg','Meddalwedd busnes','Meddalwedd','Gwefannau a gwesteio','Solar ac ynni','Addysg','Iechyd','Arian ac yswiriant','Adloniant','Newyddion a chyfryngau','Gemau','Cysylltedd','Wi‑Fi am ddim','Asiant bargen AI','Bob dydd','Sgan / QR','Hyrwyddo / Busnes'],
mi:['Mākete','Haerenga','Rererangi','Hōtera','Tāpoi','Whenua me ngā rawa','Waka','Mahi','Hokohoko','Wharekai me te kai','Ratonga ā-rohe','Taputapu me ngā mīhini','Waka moana','Kawemai me te kaweake','Tuku me te rautaki kawe','Pūmanawa pakihi','Pūmanawa','Paetukutuku me te manaaki','Pūngao rā me te pūngao','Mātauranga','Hauora','Moni me te inihua','Whakangahau','Rongo me te pāpāho','Kēmu','Hononga','Wi‑Fi kore utu','Kaihoko kirimana AI','Ia rā','Matawai / QR','Whakatairanga / Pakihi'],
fy:['Merkplak','Reizen','Flechten','Hotels','Toerisme','Ûnreplik guod','Auto’s','Banen','Winkeljen','Restaurants en iten','Lokale tsjinsten','Apparatuer en masines','Boaten en maritym','Ymport en eksport','Ferstjoering en logistyk','Bedriuwssoftware','Software','Websiden en hosting','Sinne-enerzjy','Underwiis','Sûnens','Jild en fersekering','Ferdivedaasje','Nijs en media','Spultsjes','Ferbining','Fergees Wi‑Fi','AI-dealagent','Deistich','Scan / QR','Promoasje / Bedriuw'],
lb:['Maartplaz','Reesen','Flich','Hoteler','Tourismus','Immobilien','Autoen','Aarbechtsplazen','Shopping','Restauranten an Iessen','Lokal Servicer','Ausrüstung a Maschinnen','Booter a Maritim','Import an Export','Versand a Logistik','Business-Software','Software','Websäiten an Hosting','Solar an Energie','Educatioun','Gesondheet','Suen an Assurance','Ënnerhalung','Noriichten a Medien','Spiller','Konnektivitéit','Gratis Wi‑Fi','AI-Deal-Agent','Alldag','Scannen / QR','Promotioun / Business'],
rm:['Martgà','Viadis','Sgols','Hotels','Turissem','Immobiglias','Autos','Lavurs','Cumpras','Restaurants e mangiar','Servetschs locals','Equipament e maschinas','Bartgas e maritim','Import ed export','Spediziun e logistica','Software da fatschenta','Software','Paginas web e hosting','Solar ed energia','Furmaziun','Sanadad','Daners ed assicuranzas','Divertiment','Novitads e medias','Gieus','Connectivitad','Wi‑Fi gratuit','Agent da cunvegnas AI','Mintgadi','Scannar / QR','Promoziun / Fatschenta'],
ku:['Bazaar','Rêwîtî','Firîn','Otêl','Geştûgerî','Emlak','Erebe','Kar','Kirîn','Xwaringeh û xwarin','Xizmetên herêmî','Amûr û makîne','Keştî û derya','Import û eksport','Şandin û lojîstîk','Nermalava karsaziyê','Nermalav','Malper û hostîng','Roj û enerji','Perwerde','Tenduristî','Pere û sîgorta','Şahî','Nûçe û medya','Lîstik','Girêdan','Wi‑Fi belaş','Nûnerê danûstandinê AI','Rojane','Scan / QR','Pêşvebirin / Karsazî'],
xh:['Imarike','Ukuhamba','Iinqwelomoya','Iihotele','Ukhenketho','Ipropati','Iimoto','Imisebenzi','Ukuthenga','Iindawo zokutyela nokutya','Iinkonzo zasekuhlaleni','Izixhobo noomatshini','Izikhitshane nolwandle','Ukungenisa nokuthumela ngaphandle','Ukuthumela nelogistics','Isoftware yeshishini','Isoftware','Iiwebhusayithi ne-hosting','Ilanga namandla','Imfundo','Impilo','Imali ne-inshurensi','Ulonwabo','Iindaba nemidiya','Imidlalo','Uqhagamshelwano','Wi‑Fi yasimahla','Ummeli wezivumelwano AI','Yonke imihla','Skena / QR','Khuthaza / Ishishini'],
st:['Mmaraka','Maeto','Difofane','Dihotele','Bohahlaudi','Thepa','Dikoloi','Mesebetsi','Ho reka','Direschorente le dijo','Ditshebeletso tsa lehae','Disebediswa le metjhini','Dikepe le lewatle','Kenyo le thomello','Thomello le lojistiki','Software ya kgwebo','Software','Diwebosaete le hosting','Letsatsi le matla','Thuto','Bophelo','Chelete le inshorense','Boithabiso','Ditaba le media','Dipapadi','Khokahano','Wi‑Fi ya mahala','Moemedi wa ditumellano AI','Letsatsi le letsatsi','Skena / QR','Phatlalatsa / Kgwebo'],
tn:['Mmaraka','Maeto','Diphfofo','Dihotele','Bojanala','Dithoto','Dikoloi','Ditiro','Go reka','Diresetšhurente le dijo','Ditirelo tsa selegae','Didirisiwa le metšhine','Mekoro le lewatle','Thomelontle le thomeloteng','Thomelo le lojistiki','Software ya kgwebo','Software','Diwebosaete le hosting','Letsatsi le maatla','Thuto','Botsogo','Madi le inshorense','Boitlosobodutu','Dikgang le media','Metshameko','Kgokagano','Wi‑Fi ya mahala','Moemedi wa ditumalano AI','Letsatsi le letsatsi','Skena / QR','Tshweletso / Kgwebo']
};
const sourceText=new WeakMap();
let timer=0;
function lang(){let v=document.querySelector('.sv-controls select#lang,select#lang.sv-select')?.value||localStorage.getItem('seekvera_lang')||document.documentElement.lang||navigator.language||'en';if(v==='auto')v=navigator.language||'en';return String(v).toLowerCase().split(/[-_]/)[0]||'en'}
function remember(root=document){const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){const p=n.parentElement;if(!p||p.closest('script,style,noscript,code,pre,svg,#aiMessages,#aiResult,.ai-msg,.sv-ai-answer,.sv-ai-actions,#liveListings'))continue;const s=(n.nodeValue||'').trim();if(s&&!sourceText.has(n))sourceText.set(n,s)}}
function fillMissingTitles(){const d=window.SEEKVERA_R14_CATEGORIES?.data;if(!d)return;for(const [k,v] of Object.entries(EXTRA_TITLES))if(!d[k])d[k]=v}
function titleData(){fillMissingTitles();return window.SEEKVERA_R14_CATEGORIES?.data||null}
function fixCategories(){
 const l=lang(),data=titleData(),tiles=[...document.querySelectorAll('#categories .r5-tile')];
 if(l!=='en'&&data?.[l]){for(let i=0;i<tiles.length&&i<data[l].length;i++){const b=tiles[i].querySelector('.r5-tile-body>b');if(b&&data[l][i])b.textContent=data[l][i]}}
 for(const tile of tiles){
  const small=tile.querySelector('.r5-tile-body>small');if(!small)continue;
  const t=(small.textContent||'').trim();
  const unresolved=l!=='en'&&(!t||t==='…'||EN_DESC.has(t));
  small.hidden=unresolved;small.classList.toggle('sv-r20-untranslated',unresolved);
  if(unresolved)small.setAttribute('aria-hidden','true');else small.removeAttribute('aria-hidden');
 }
}
function fixStaticLeaks(){
 const l=lang();if(l==='en')return;
 document.querySelectorAll('.r5-section-head,.r5-ai-note,.r5-foot,.r5-kicker,.r5-scope,.r5-right-box').forEach(root=>{
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){
   const original=sourceText.get(n),now=(n.nodeValue||'').trim();if(!original||!now||now!==original||SKIP_EN.has(now))continue;
   if(!/[A-Za-z]{3}/.test(now))continue;
   if(EN_DESC.has(now)){n.nodeValue='';continue}
  }
 });
}
function injectStyle(){let s=document.getElementById('svR20FinalStyle');if(s)return s;s=document.createElement('style');s.id='svR20FinalStyle';s.textContent=`
html,body{overflow-x:hidden!important}
#categories .r5-grid{align-items:stretch!important}
#categories .r5-tile{min-width:0!important;width:100%!important;height:100%!important;overflow:hidden!important;contain:layout paint!important}
#categories .r5-tile-body{min-width:0!important;overflow:hidden!important;padding:7px 8px!important}
#categories .r5-tile-body>b,#categories .r5-tile-body>small{max-width:100%!important;overflow-wrap:anywhere!important;word-break:normal!important;hyphens:auto!important}
#categories .r5-tile-body>b{font-size:clamp(10.5px,3.1vw,14px)!important;line-height:1.18!important;display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;overflow:hidden!important;min-height:2.36em!important}
#categories .r5-tile-body>small{font-size:clamp(9px,2.45vw,11px)!important;line-height:1.22!important;display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;overflow:hidden!important;min-height:2.44em!important}
#categories .r5-tile-body>small[hidden],#categories .sv-r20-untranslated{display:none!important;min-height:0!important}
#aiChat,.sv-unified-chat{overflow:hidden!important;overscroll-behavior:contain!important;overflow-anchor:none!important}
#aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{height:auto!important;min-height:86px!important;max-height:170px!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;overflow-anchor:none!important;scroll-behavior:auto!important}
#aiChat .ai-msg,.sv-unified-chat .ai-msg{overflow-wrap:anywhere!important;word-break:break-word!important;max-width:94%!important}
@media(max-width:780px){
 #aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{height:auto!important;min-height:82px!important;max-height:128px!important}
 #aiChatSpeaker,.sv-global-speaker{width:46px!important;min-width:46px!important;max-width:46px!important;height:46px!important;min-height:46px!important}
 #categories .r5-tile-body{min-height:48px!important}
}
@media(max-width:390px){#aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{max-height:118px!important}}
`;document.head.appendChild(s);return s}
function keepStyleAuthoritative(){const s=injectStyle();if(s?.parentNode===document.head&&document.head.lastElementChild!==s)document.head.appendChild(s)}
function apply(){fillMissingTitles();keepStyleAuthoritative();fixCategories();fixStaticLeaks();document.documentElement.dataset.svR20='ready'}
function schedule(ms=60){clearTimeout(timer);timer=setTimeout(apply,ms)}
function bind(){remember(document);fillMissingTitles();injectStyle();schedule(0);schedule(250);schedule(900);document.addEventListener('change',e=>{if(e.target?.id==='lang'||e.target?.id==='country'){schedule(30);schedule(350);schedule(1000)}},true);window.addEventListener('seekvera:languagechange',()=>schedule(40));window.addEventListener('seekvera:countrychange',()=>schedule(40));window.addEventListener('pageshow',()=>schedule(50));new MutationObserver(ms=>{let dirty=false;for(const m of ms){if(m.type==='characterData'||m.addedNodes?.length){dirty=true;for(const n of m.addedNodes||[])if(n.nodeType===1)remember(n)}}if(dirty)schedule(90)}).observe(document.documentElement,{subtree:true,childList:true,characterData:true})}
if(document.readyState==='loading'){remember(document);document.addEventListener('DOMContentLoaded',bind,{once:true})}else bind();
window.SEEKVERA_R20_FINAL={version:VERSION,apply,schedule,descriptions:[...EN_DESC],extraLanguages:Object.keys(EXTRA_TITLES)};
})();
