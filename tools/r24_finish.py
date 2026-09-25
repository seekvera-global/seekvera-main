from pathlib import Path
import re

ROOT=Path('.')
LANGS=['en','ar','fr','zh','es','hi','pt','de','ja','ko','id','tr','ru','ur','bn','vi','it','sw','th','fa','pl','nl','ms','fil','ha','yo','ig','am','he','el','uk','ro','cs','sk','hu','sv','no','da','fi','bg','hr','sr','sl','lt','lv','et','ca','eu','gl','is','sq','mk','ka','hy','az','kk','uz','ky','tg','tk','ne','si','ta','te','ml','mr','gu','pa','km','lo','my','mn','zu','af','be','bs','dz','ti','fo','kl','rw','sm','to','so','ps','dv','mt','mg','ga','cy','mi','fy','lb','rm','ku','xh','st','tn']

# 1) Make the live AI obey the language of the latest message, not the current country/UI.
p=ROOT/'worker.js'; s=p.read_text(encoding='utf-8')
old=("When the app has an explicit selected language, reply in that selected language; when language is Auto, detect the latest user message and reply in that same language and script. "
     "Country or location must never override the selected or detected language. If the user explicitly asks inside the message for a different reply language, use that requested language. "
     "Never default to English merely because the country, interface or browser is English.")
new=("Always identify the language of the latest user message and reply in that same language and script. The selected interface language is only a context hint and a tiebreaker for truly ambiguous very short text; it must not override a clear user-message language. "
     "Country or location must never override the detected user-message language. If the user explicitly asks inside the message for a different reply language, use that requested language. "
     "Never default to English merely because the country, interface or browser is English.")
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R24 worker message-language prompt anchor missing')

# 2) Add machine-readable language control alongside the already-supported country control.
control_old="const control='APP CONTROL: If and only if the latest user message explicitly asks to set, change, switch or select the SEEKVERA app country or market, append exactly one machine token [[COUNTRY:XX]] where XX is the ISO 3166-1 alpha-2 country code. The token is exempt from LANGUAGE LOCK. Never append it for searches, travel, hotels, jobs, comparisons or statements that merely mention a country. Understand this control request in any language. Examples: switch my country to France -> [[COUNTRY:FR]]; حطلي الدولة اليابان -> [[COUNTRY:JP]]; mets mon pays sur Canada -> [[COUNTRY:CA]].';"
control_new="const control='APP CONTROL: Only when the latest user message explicitly asks to set, change, switch or select the SEEKVERA app country/market and/or interface language, append machine control tokens. For country use [[COUNTRY:XX]] where XX is the ISO 3166-1 alpha-2 code. For interface language use [[LANG:xx]] where xx is the SEEKVERA language code. If both are explicitly requested, append both tokens. These tokens are exempt from LANGUAGE LOCK. Never append them for ordinary searches, travel, hotels, jobs, comparisons or statements that merely mention a place or language. Understand app-control requests in any language. Examples: switch my country to France -> [[COUNTRY:FR]]; حطلي الدولة اليابان -> [[COUNTRY:JP]]; change the app to Hindi -> [[LANG:hi]]; غيري التطبيق للهندي -> [[LANG:hi]].';"
if control_old in s:s=s.replace(control_old,control_new,1)
elif control_new not in s:raise SystemExit('R24 worker app-control prompt anchor missing')

if 'languageAction=langMatch?' not in s:
    start=s.find("const rawResponse=String(r.response||'');const countryMatch=")
    if start<0:raise SystemExit('R24 worker response parser start missing')
    old_return="return j(request,{ok:true,response,model:r.model,language:detected,category:c,route:route(c),countryAction,liveData:false})"
    end=s.find(old_return,start)
    if end<0:raise SystemExit('R24 worker response parser return missing')
    end+=len(old_return)
    parser="const rawResponse=String(r.response||'');const countryMatch=rawResponse.match(/\\[\\[COUNTRY:([A-Z]{2})\\]\\]/i),langMatch=rawResponse.match(/\\[\\[LANG:([a-z]{2,3})\\]\\]/i);const response=rawResponse.replace(/\\s*\\[\\[COUNTRY:[A-Z]{2}\\]\\]\\s*/ig,' ').replace(/\\s*\\[\\[LANG:[a-z]{2,3}\\]\\]\\s*/ig,' ').replace(/\\s{2,}/g,' ').trim();const countryAction=countryMatch?{type:'set-country',code:countryMatch[1].toUpperCase()}:null,languageAction=langMatch?{type:'set-language',code:langMatch[1].toLowerCase()}:null;return j(request,{ok:true,response,model:r.model,language:detected,category:c,route:route(c),countryAction,languageAction,liveData:false})"
    s=s[:start]+parser+s[end:]
p.write_text(s,encoding='utf-8')

# 3) Harden the browser controller: short ISO codes must only match as standalone tokens,
# and an unqualified command such as Arabic "غيري للهندي" must prefer language over country.
p=ROOT/'r24-ai-controller.js'; c=p.read_text(encoding='utf-8')
old="function findName(text,entries){const t=' '+norm(text)+' ';for(const[name,code]of entries){if(name.length<2)continue;if(t.includes(' '+name+' ')||t.includes(name))return code}return''}"
new="function findName(text,entries){const t=' '+norm(text)+' ';for(const[name,code]of entries){if(name.length<2)continue;if(name.length<=3){if(t.includes(' '+name+' '))return code;continue}if(t.includes(name))return code}return''}"
if old in c:c=c.replace(old,new,1)
elif new not in c:raise SystemExit('R24 controller findName anchor missing')
old="if(!language&&(mentionsLang||!mentionsCountry))language=findName(text,buildLanguageNames());if(!country&&(mentionsCountry||!mentionsLang))country=findName(text,buildCountryNames());if(language&&country){const li=t.lastIndexOf(norm(language)),ci=t.lastIndexOf(norm(country));void li;void ci}return{language:language||'',country:country||''}"
new="if(!language&&mentionsLang)language=findName(text,buildLanguageNames());if(!country&&mentionsCountry)country=findName(text,buildCountryNames());if(!mentionsLang&&!mentionsCountry){if(!language)language=findName(text,buildLanguageNames());if(!language&&!country)country=findName(text,buildCountryNames())}return{language:language||'',country:country||''}"
if old in c:c=c.replace(old,new,1)
elif new not in c:raise SystemExit('R24 controller inference anchor missing')
p.write_text(c,encoding='utf-8')

# 4) Service worker: always network-first the controller and cache it for offline fallback.
p=ROOT/'sw.js'; w=p.read_text(encoding='utf-8')
if "'./r24-ai-controller.js'" not in w:
    w=w.replace("'./r20-final-guard.js'","'./r20-final-guard.js','./r24-ai-controller.js'",1)
if 'r24-ai-controller|' not in w:
    w=w.replace('(?:i18n-ui|voice-ai|global-ui|superapp|navigation|locale-r15|','(?:r24-ai-controller|i18n-ui|voice-ai|global-ui|superapp|navigation|locale-r15|',1)
p.write_text(w,encoding='utf-8')

# 5) Load the unified controller on every application HTML page.
tag='<script src="r24-ai-controller.js?v=20260925-r24-control1" data-no-i18n="1"></script>'
injected=0
for p in sorted(ROOT.glob('*.html')):
    if p.name.lower().startswith('google'):continue
    h=p.read_text(encoding='utf-8')
    if 'r24-ai-controller.js' in h:continue
    if '</body>' not in h.lower():continue
    pos=h.lower().rfind('</body>')
    h=h[:pos]+tag+'\n'+h[pos:]
    p.write_text(h,encoding='utf-8');injected+=1

# Integrity.
w=(ROOT/'worker.js').read_text(encoding='utf-8')
c=(ROOT/'r24-ai-controller.js').read_text(encoding='utf-8')
sw=(ROOT/'sw.js').read_text(encoding='utf-8')
assert 'languageAction=langMatch?' in w
assert 'Always identify the language of the latest user message' in w
assert '[[LANG:xx]]' in w
assert "const VERSION='20260925-r24-unified-control'" in c
assert len(LANGS)==98
assert './r24-ai-controller.js' in sw and 'r24-ai-controller|' in sw
pages=[p for p in ROOT.glob('*.html') if not p.name.lower().startswith('google') and '</body>' in p.read_text(encoding='utf-8').lower()]
missing=[p.name for p in pages if 'r24-ai-controller.js' not in p.read_text(encoding='utf-8')]
assert not missing,missing
print(f'R24 PATCH PASS — 98 languages, {len(pages)} app pages, {injected} newly injected')
