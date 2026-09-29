from pathlib import Path
import re

VER='20260929-r119b-language-independent-action-ai'

# Worker
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,count=1)

# Spoken language must not be forced from UI/browser language when native shadow is Latin.
s,n=re.subn(r"const strongHint=nativeFamily&&nativeFamily!='latin'\?nativeLang:\(nativeText&&nativeConfidence>=\.60\?softHint:''\);","const strongHint=nativeFamily&&nativeFamily!=='latin'?nativeLang:'';",s,count=1)
if not n and "const strongHint=nativeFamily&&nativeFamily!=='latin'?nativeLang:'';" not in s:
    raise SystemExit('R119B strongHint anchor missing')

# Explicit actionable intent wins over an AI classification of general.
anchor='async function degradedFallback(request,env,ctx,body,message){'
helper=r'''function directCategoryIntent(message,modelCategory='general'){
 const s=String(message||'').toLowerCase().trim();
 if(employmentIntent(message))return'jobs';
 const action=/(?:\b(?:find|search|show|open|take me|go to|book|reserve|buy|sell|rent|need|want|looking for|look for|apply for|help me find|help me get)\b|دوريني|دورلي|ندور|عم دور|بدور|ابحث|أبحث|فتش|فتشي|بدي|اريد|أريد|احتاج|أحتاج|افتح|افتحي|وديني|ودّيني|خذني|خدني|احجز|احجزي|اشتري|بيع|استأجر|استاجر|ساعدني|ساعديني|cherche|chercher|trouve|trouver|ouvre|réserve|reserver|acheter|vendre|louer|besoin|veux|busco|buscar|abre|quiero|necesito|reservar|comprar|vender|alquilar|procuro|procurar|abra|quero|preciso|alugar|suche|finden|öffne|offne|brauche|möchte|mochte|buchen|kaufen|verkaufen|mieten|arıyorum|ara|bul|aç|istiyorum|rezerv|satın|kirala|найди|найти|ищу|открой|нужен|хочу|забронируй|купить|продать|аренд|找|搜索|打开|带我|我想|我需要|预订|购买|出售|租|探して|検索|開いて|連れて|欲しい|必要|予約|購入|売|借|찾아|검색|열어|데려|원해|필요|예약|구매|판매|임대|खोज|ढूंढ|खोल|चाहिए|चाहता|बुक|खरीद|बेच|किराए)/iu.test(s);
 if(!action)return category(modelCategory);
 const rules=[
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
 return category(modelCategory)
}

'''
if 'function directCategoryIntent(' not in s:
    if anchor not in s: raise SystemExit('R119B helper anchor missing')
    s=s.replace(anchor,helper+anchor,1)

# degraded fallback
old="requested=category(body?.conversationIntent||message),cat=(act.isAction||chat)?'general':(requested==='jobs'&&!employmentIntent(message)?'general':requested)"
new="requested=directCategoryIntent(message,category(body?.conversationIntent||'general')),cat=(act.isAction||chat)?'general':requested"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R119B degraded category anchor missing')

# model + pollinations structured paths; tolerate current employment override syntax.
oldcat="meta=metaConversation(message),cat=(act.isAction||conversationOnly(message)||meta)?'general':employmentIntent(message)?'jobs':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));"
newcat="meta=metaConversation(message),modelCat=category(obj.category),cat=(act.isAction||conversationOnly(message)||meta)?'general':directCategoryIntent(message,modelCat);"
count=s.count(oldcat)
if count:s=s.replace(oldcat,newcat)
elif newcat not in s:raise SystemExit('R119B model category anchor missing')

# plain fallback should also respect explicit user intent.
s=s.replace("cat=(conversationOnly(message)||meta)?'general':(category(message)==='jobs'&&!employmentIntent(message)?'general':category(message));", "cat=(conversationOnly(message)||meta)?'general':directCategoryIntent(message,'general');",1)

needle="Conversation-first rule: use general for greetings, small talk, questions, explanations, language/voice talk, corrections, incomplete requests, and every clarification turn. Choose a marketplace category only when the user's current goal is genuinely actionable and belongs there (find/search/book/buy/sell/apply/compare/use)."
extra=" A clear command such as ‘find me a job’, ‘دوريني على شغل’, ‘find me a hotel’, ‘show me cars’, or the equivalent in any language is actionable immediately: choose its category even if city, date or budget is not known yet."
if needle in s and extra.strip() not in s:s=s.replace(needle,needle+extra,1)

s=s.replace("setTimeout(()=>reject(Error('model timeout')),4200)","setTimeout(()=>reject(Error('model timeout')),3000)")
s=s.replace("setTimeout(()=>resolve(null),4500)","setTimeout(()=>resolve(null),3300)")
s=s.replace("setTimeout(()=>ctl.abort(),2200)","setTimeout(()=>ctl.abort(),1400)")

# Expose unique release/health marker.
if 'r119b:true' not in s:
    marker="r119:true,r119Runtime:"
    i=s.find(marker)
    if i>=0:s=s[:i]+"r119b:true,r119bRuntime:'language-independent-voice-direct-intent-atomic-controls',"+s[i:]
    else:raise SystemExit('R119B health anchor missing')

p.write_text(s,encoding='utf-8')
print('R119B worker patched',count,'structured paths')

# Voice engine
p=Path('voice-ai.js')
v=p.read_text(encoding='utf-8')
v=re.sub(r"window\.__seekveraVoiceMode='[^']+'","window.__seekveraVoiceMode='20260929-r119b-language-independent-voice'",v,count=1)
v=v.replace('const VOICE_SILENCE_MS=2300','const VOICE_SILENCE_MS=1800',1)
old="const inferred=languageFromTranscript(native,selectedLang()),hint=codeOf(inferred)||codeOf(selectedLang())||codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'');"
new="const ns=transcriptScript(native),inferred=languageFromTranscript(native,''),hint=(ns&&ns!=='latin')?codeOf(inferred):'';"
if old in v:v=v.replace(old,new,1)
elif new not in v:raise SystemExit('R119B voice hint anchor missing')
old="if(!transcriptPoor(nt)&&ns&&ns!=='latin'&&ws&&ws!==ns)return{text:nt,language:languageFromTranscript(nt,current),engine:'native-script-rescue'};\n  // For Latin-script languages"
new="if(!transcriptPoor(nt)&&ns&&ns!=='latin'&&ws&&ws!==ns)return{text:nt,language:languageFromTranscript(nt,current),engine:'native-script-rescue'};\n  // UI/native recognizers can hallucinate Latin text for non-Latin speech; a clear server non-Latin transcript wins.\n  if(ws&&ws!=='latin'&&ns==='latin'&&!transcriptPoor(wt))return whisper;\n  // For Latin-script languages"
if old in v:v=v.replace(old,new,1)
elif 'a clear server non-Latin transcript wins' not in v:raise SystemExit('R119B hybrid anchor missing')
v=v.replace("const language=languageFromTranscript(nt,selectedLang());","const language=languageFromTranscript(nt,'');",1)
p.write_text(v,encoding='utf-8')
print('R119B voice patched')

# Frontend intent + speed
p=Path('r31-ui-polish.js')
r=p.read_text(encoding='utf-8')
r=re.sub(r'const VERSION = "[^"]+";', 'const VERSION = "20260929-r119b-language-independent-action-ai";', r, count=1)
r=r.replace('عم دور على شغل|بدي شغل|دوام','عم دور على شغل|دوريني على شغل|دورلي على شغل|ندور على شغل|ساعديني ندور على شغل|ساعدني دور على شغل|بدي شغل|دوام',1)
start=r.find('  async function fetchAI(payload) {');end=r.find('\n  function categoryTitle(cat)',start)
if start<0 or end<0:raise SystemExit('R119B fetchAI boundary missing')
newfetch=r'''  async function fetchAI(payload) {
    const urls=[...new Set([location.origin+"/api/ai","https://seekvera-main.seekvera-global.workers.dev/api/ai"])];
    const attempt=async url=>{const c=new AbortController(),t=setTimeout(()=>c.abort(),4200);try{const x=await fetch(url,{method:"POST",headers:{"content-type":"application/json","cache-control":"no-store"},body:JSON.stringify(payload),signal:c.signal,cache:"no-store"});const d=await x.json().catch(()=>({}));if(!x.ok||!d?.response)throw Error(d?.error||"HTTP "+x.status);return d}finally{clearTimeout(t)}};
    try{return await Promise.any(urls.map(attempt))}catch{throw Error("AI unavailable")}
  }'''
r=r[:start]+newfetch+r[end:]
old='let finalCat =\n        guessed && guessed !== "general" ? guessed : d?.category || guessed;'
new='let finalCat =\n        guessed && guessed !== "general" ? guessed : (d?.category && d.category !== "general" ? d.category : intent(q));'
if old in r:r=r.replace(old,new,1)
elif new not in r:raise SystemExit('R119B finalCat anchor missing')
p.write_text(r,encoding='utf-8')
print('R119B frontend patched')

# Cache bust
p=Path('worker-r31.js');w=p.read_text(encoding='utf-8')
w=re.sub(r'r31-ui-polish\\.js\\?v=[A-Za-z0-9._-]+','r31-ui-polish.js?v=20260929-r119b-language-independent-action-ai',w)
w=re.sub(r'r31-ui-polish\.js\?v=[A-Za-z0-9._-]+','r31-ui-polish.js?v=20260929-r119b-language-independent-action-ai',w)
w=re.sub(r'voice-ai\\.js\\?v=[A-Za-z0-9._-]+','voice-ai.js?v=20260929-r119b-language-independent-voice',w)
w=re.sub(r'voice-ai\.js\?v=[A-Za-z0-9._-]+','voice-ai.js?v=20260929-r119b-language-independent-voice',w)
p.write_text(w,encoding='utf-8')
p=Path('sw.js');sw=p.read_text(encoding='utf-8');sw=re.sub(r"const CACHE='[^']+';","const CACHE='seekvera-r119b-language-independent-action-ai';",sw,count=1);p.write_text(sw,encoding='utf-8')
print('R119B cache patched')
