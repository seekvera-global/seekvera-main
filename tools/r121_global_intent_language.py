from pathlib import Path
import re

VER='20260929-r121-global-intent-language'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,count=1)

# Replace action detector with natural imperative variants across major language families.
f0=s.index("function directCategoryIntent(message")
a=s.index(" const action=",f0)
b=s.index(";\n if(!action)",a)
new_action=r''' const action=/(?:\b(?:find|search|show|open|take me|go to|book|reserve|buy|sell|rent|need|want|looking for|look for|apply for|help me find|help me get)\b|دوريني|دورلي|ندور|عم دور|بدور|ابحث|أبحث|فتش|فتشي|بدي|اريد|أريد|احتاج|أحتاج|افتح|افتحي|وديني|ودّيني|خذني|خدني|احجز|احجزي|اشتري|بيع|استأجر|استاجر|ساعدني|ساعديني|cherch(?:e|er|ez)|trouv(?:e|er|ez)(?:-moi)?|montre(?:z|-moi)?|ouvre(?:z)?|réserve|reserver|achet(?:e|er)|vend(?:s|re)|lou(?:e|er)|besoin|veux|búscame|buscame|busca|buscar|encuéntrame|encuentrame|encuentra|muéstrame|muestrame|muestra|abre|llévame|llevame|quiero|necesito|reservar|comprar|vender|alquilar|procure|procurar|encontre|mostre|abra|quero|preciso|alugar|finde|finden|suche|such|zeige|zeig|öffne|offne|brauche|möchte|mochte|buchen|kaufen|verkaufen|mieten|trova|cerca|apri|mostra|voglio|cerco|bisogno|arıyorum|ariyorum|bana|ara|bul|göster|goster|aç|ac|istiyorum|rezerv|satın|kirala|найди|найти|ищу|открой|покажи|нужен|хочу|забронируй|купить|продать|аренд|找|搜索|打开|带我|我想|我需要|预订|购买|出售|租|探して|検索|開いて|連れて|見せて|欲しい|必要|予約|購入|売|借|찾아|검색|열어|데려|보여|원해|필요|예약|구매|판매|임대|खोज|ढूंढ|ढूँढ|खोल|दिखा|चाहिए|चाहता|बुक|खरीद|बेच|किराए|tìm|tim|tìm kiếm|mở|mở|hãy tìm|hay tim|cari|carikan|buka|tunjukkan|tolong|ingin|butuh|tafuta|fungua|onyesha|nataka|nahitaji|খুঁজ|খোঁজ|দেখাও|খুল|পাই|پیدا|باز کن|بگرد|می.?خواهم|میخوام|تلاش|ڈھونڈ|ڈھونڈو|کھولو|دکھاؤ|چاہیے)/iu.test(s)'''
s=s[:a]+new_action+s[b+1:]

# Add explicit Jobs keyword rule for languages not fully covered by old employmentIntent.
rules_anchor=" const rules=[\n"
jobs_rule=r" ['jobs',/(?:\bjob|jobs|career|vacancy|employment|work\b|وظيف|وظائف|وظايف|شغل|فرصة عمل|emploi|travail|trabajo|empleo|trabalho|emprego|lavoro|arbeit|stelle|stellen|iş|kariyer|работ|ваканси|工作|职位|求人|仕事|채용|일자리|직업|नौकरी|रोजगार|काम|việc làm|công việc|viec lam|pekerjaan|kerja|kazi|ajira|চাকরি|কাজ|کار|شغل|نوکری|کام)/iu],\n"
if jobs_rule.strip() not in s:
    if rules_anchor not in s:raise SystemExit('R121 rules anchor missing')
    s=s.replace(rules_anchor,rules_anchor+jobs_rule,1)

# Fast-path language detection cannot rely on the UI language. Add natural command clues.
fast_anchor="const FAST_DIRECT_LANGS=new Set("
helper=r'''function fastCommandLanguage(message,suggested=''){
 const t=String(message||''),s=t.toLowerCase();
 if(/[\u0600-\u06ff]/u.test(t))return messageLanguage(t,suggested);
 if(/[\u0900-\u097f]/u.test(t))return'hi';if(/[\u0980-\u09ff]/u.test(t))return'bn';if(/[\u3040-\u30ff]/u.test(t))return'ja';if(/[\u4e00-\u9fff]/u.test(t))return'zh';if(/[\uac00-\ud7af]/u.test(t))return'ko';if(/[\u0400-\u052f]/u.test(t))return'ru';
 if(/[đăơư]/iu.test(t)||/(?:tìm|việc làm|công việc|khách sạn|xe hơi|giúp tôi|hãy)/iu.test(s))return'vi';
 if(/[ğışİçöü]/u.test(t)||/\b(?:bana|bul|arıyorum|ariyorum|istiyorum|iş|otel|araba|ev)\b/iu.test(s))return'tr';
 if(/(?:búscame|buscame|busca|encuéntrame|encuentrame|muéstrame|muestrame|quiero|necesito|trabajo|empleo|coche)/iu.test(s))return'es';
 if(/(?:trouve|cherch|montre|ouvre|je veux|besoin|emploi|travail|voiture|hôtel)/iu.test(s))return'fr';
 if(/(?:procure|encontre|mostre|quero|preciso|trabalho|emprego|carro|hotel)/iu.test(s))return'pt';
 if(/(?:finde|suche|zeige|öffne|offne|ich möchte|ich mochte|brauche|arbeit|stelle|wohnung)/iu.test(s))return'de';
 if(/(?:trova|cerca|apri|mostra|voglio|bisogno|lavoro|macchina|albergo)/iu.test(s))return'it';
 if(/(?:carikan|cari|buka|tunjukkan|tolong|pekerjaan|kerja|mobil|rumah)/iu.test(s))return'id';
 if(/(?:tafuta|fungua|onyesha|nataka|nahitaji|kazi|ajira|gari|nyumba)/iu.test(s))return'sw';
 return messageLanguage(t,suggested)
}

'''
if 'function fastCommandLanguage(' not in s:
    i=s.find(fast_anchor)
    if i<0:raise SystemExit('R121 fast language anchor missing')
    s=s[:i]+helper+s[i:]
s=s.replace("const language=messageLanguage(message,body?.language),act=actionState(message,'','',body?.clientControls);","const language=fastCommandLanguage(message,body?.language),act=actionState(message,'','',body?.clientControls);",1)

# Expose release marker.
if 'r121:true' not in s:
    s=s.replace("r120:true,r120Runtime:'instant-controls-direct-intent-language-independent-voice'","r121:true,r121Runtime:'global-command-inflections-and-fast-language-detection',r120:true,r120Runtime:'instant-controls-direct-intent-language-independent-voice'",1)
p.write_text(s,encoding='utf-8')

# Frontend deterministic intent gets the same common inflections.
p=Path('r31-ui-polish.js');r=p.read_text(encoding='utf-8');r=re.sub(r'const VERSION = "[^"]+";','const VERSION = "20260929-r121-global-intent-language";',r,count=1)
# Extend category patterns with phrases that appear in real commands.
r=r.replace('job|jobs|career|vacancy|employment|hiring|looking for work|need work|find work|', 'job|jobs|career|vacancy|employment|hiring|looking for work|need work|find work|việc làm|công việc|pekerjaan|kerja|kazi|ajira|চাকরি|কাজ|کار|نوکری|',1)
r=r.replace('car|cars|vehicle|auto|', 'car|cars|vehicle|auto|coche|voiture|wagen|araba|машин|汽车|車|자동차|कार|गाड़ी|mobil|gari|',1)
p.write_text(r,encoding='utf-8')

# Cache identity
p=Path('worker-r31.js');w=p.read_text(encoding='utf-8');w=re.sub(r'r31-ui-polish\\.js\\?v=[A-Za-z0-9._-]+','r31-ui-polish.js?v=20260929-r121-global-intent-language',w);w=re.sub(r'r31-ui-polish\.js\?v=[A-Za-z0-9._-]+','r31-ui-polish.js?v=20260929-r121-global-intent-language',w);p.write_text(w,encoding='utf-8')
p=Path('sw.js');sw=p.read_text(encoding='utf-8');sw=re.sub(r"const CACHE='[^']+';","const CACHE='seekvera-r121-global-intent-language';",sw,count=1);p.write_text(sw,encoding='utf-8')
print('R121 patched')
