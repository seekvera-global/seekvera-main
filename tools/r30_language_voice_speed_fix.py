from pathlib import Path
import re

VER='20260925-r30'
changed=[]

def write(path,text):
    p=Path(path)
    old=p.read_text(encoding='utf-8')
    if old!=text:
        p.write_text(text,encoding='utf-8')
        changed.append(path)

# 1) Full visible UI translation guard: force it on every country/language change,
# translate AI action links too, speed batch translation, and add instant Arabic
# translations for the exact live strings reported by the user.
p=Path('i18n-ui.js'); s=p.read_text(encoding='utf-8')
s=s.replace("const VERSION='20260925-r19-no-mixed-language';",f"const VERSION='{VER}-no-mixed-language';",1)
s=s.replace(".sv-ai-answer,.sv-ai-actions,[data-no-translate]",".sv-ai-answer,[data-no-translate]",1)
marker='/* R30 instant reported-string translations */'
if marker not in s:
    anchor='window.__SEEKVERA_R9_QUICK=QUICK;'
    addition="""/* R30 instant reported-string translations */
Object.assign(QUICK.ar,{
'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'لا توجد حالياً إعلانات سوق مباشرة معتمدة. لا تنشئ SEEKVERA إعلانات وهمية.',
'Loading approved listings…':'جارٍ تحميل الإعلانات المعتمدة…',
'Live marketplace':'السوق المباشر','Approved real listings only.':'إعلانات حقيقية معتمدة فقط.','OPEN MARKETPLACE →':'افتح السوق ←',
'Find, compare, choose — worldwide.':'ابحث وقارن واختر — حول العالم.','Find, compare, choose — worldwide':'ابحث وقارن واختر — حول العالم',
'Chat · Voice · Camera · Attach':'دردشة · صوت · كاميرا · إرفاق','Online':'متصل','Message SEEKVERA AI…':'راسل ذكاء SEEKVERA…',
'Request anything':'اطلب أي شيء','Tell SEEKVERA what you need anywhere in the world.':'أخبر SEEKVERA بما تحتاج إليه في أي مكان في العالم.',
'About':'حول','Privacy':'الخصوصية','Terms':'الشروط','Contact':'تواصل','Disclosure':'الإفصاح'
});
"""
    if anchor not in s: raise SystemExit('i18n anchor missing')
    s=s.replace(anchor,addition+anchor,1)
old=""" for(let i=0;i<remaining.length;i+=12)await requestBatch(remaining.slice(i,i+12));
 remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 for(let i=0;i<remaining.length;i+=4)await requestBatch(remaining.slice(i,i+4));"""
new=""" const groups=[];for(let i=0;i<remaining.length;i+=12)groups.push(remaining.slice(i,i+12));
 for(let i=0;i<groups.length;i+=4)await Promise.all(groups.slice(i,i+4).map(requestBatch));
 remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 const retry=[];for(let i=0;i<remaining.length;i+=4)retry.push(remaining.slice(i,i+4));
 for(let i=0;i<retry.length;i+=4)await Promise.all(retry.slice(i,i+4).map(requestBatch));"""
if old in s: s=s.replace(old,new,1)
write('i18n-ui.js',s)

# 2) Atomic country coordinator must call the generic visible-text guard too.
p=Path('locale-r15.js'); s=p.read_text(encoding='utf-8')
if 'SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)' not in s:
    s=s.replace("try{window.SEEKVERA_I18N?.apply?.()}catch{}","try{window.SEEKVERA_I18N?.apply?.()}catch{}\n  try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)}catch{}",1)
    s=s.replace("try{window.SEEKVERA_R14_CATEGORIES?.apply?.()}catch{}\n    localizeCountryOptions(state);","try{window.SEEKVERA_R14_CATEGORIES?.apply?.()}catch{}\n    try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)}catch{}\n    localizeCountryOptions(state);",1)
s=s.replace("version:'20260924-r15'",f"version:'{VER}'",1)
write('locale-r15.js',s)

# 3) AI controller refresh also forces the full visible UI pass.
p=Path('r24-ai-controller.js'); s=p.read_text(encoding='utf-8')
s=s.replace("const VERSION='20260925-r24-unified-control';",f"const VERSION='{VER}-unified-control';",1)
if "SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)" not in s:
    s=s.replace("function refresh(){try{window.SEEKVERA_I18N?.apply?.()}catch{}","function refresh(){try{window.SEEKVERA_I18N?.apply?.()}catch{}try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)}catch{}",1)
write('r24-ai-controller.js',s)

# 4) Voice: allow natural pauses while listening and keep TTS chunks short enough
# for Android speechSynthesis to finish instead of cutting mid-answer.
p=Path('voice-ai.js'); s=p.read_text(encoding='utf-8')
s=s.replace('const TTS_RETRY_DELAYS=[240,650,1200];','const TTS_RETRY_DELAYS=[120,350,700,1300];',1)
s=s.replace('const VOICE_SILENCE_MS=1250,VOICE_MAX_MS=30000,VOICE_RMS_THRESHOLD=.016;','const VOICE_SILENCE_MS=2100,VOICE_MAX_MS=45000,VOICE_RMS_THRESHOLD=.014;',1)
s=s.replace("{1,170}(?:[.!?。！？؛،,:;]+|$)","{1,105}(?:[.!?。！？؛،,:;]+|$)",1)
s=s.replace('while(p.length>190){let cut=p.lastIndexOf(\' \',180);if(cut<80)cut=180;','while(p.length>125){let cut=p.lastIndexOf(\' \',115);if(cut<55)cut=115;',1)
s=s.replace("return out.length?out:[s.slice(0,190)]","return out.length?out:[s.slice(0,125)]",1)
write('voice-ai.js',s)

# 5) Faster AI: when the app already supplies the selected country language, do
# not spend a second AI call re-detecting it; in fast chat do not spend a third
# AI call classifying generic intent. Keep the answer concise for fast mode.
p=Path('worker.js'); s=p.read_text(encoding='utf-8')
s=s.replace("const script=scriptLanguage(text);if(script)return script;if(!env.AI)return h&&!/^auto$/i.test(h)?h:'the language used by the user';","const script=scriptLanguage(text);if(script)return script;if(h&&!/^auto$/i.test(h))return h;if(!env.AI)return'the language used by the user';",1)
s=s.replace("const hist=Array.isArray(b.history)?b.history.slice(-12)","const hist=Array.isArray(b.history)?b.history.slice(b.fast?-8:-12)",1)
s=s.replace("const detected=await detectedLanguage(env,m,b.language),c=await classifyIntent(env,contextText),p=","const detected=await detectedLanguage(env,m,b.language),c=b.fast?category(contextText):await classifyIntent(env,contextText),p=",1)
s=s.replace("],520,.14);const rawResponse=", "],b.fast?360:520,.14);const rawResponse=",1)
s=s.replace("const RELEASE='20260924-ai-r17'",f"const RELEASE='{VER}-ai'",1)
write('worker.js',s)

# 6) Cache-bust the changed runtime files on every HTML page so phones do not
# keep the older language/voice/controller code.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    t=p.read_text(encoding='utf-8'); before=t
    t=re.sub(r'i18n-ui\.js\?v=[^\"\']+',f'i18n-ui.js?v={VER}',t)
    t=re.sub(r'voice-ai\.js\?v=[^\"\']+',f'voice-ai.js?v={VER}',t)
    t=re.sub(r'locale-r15\.js\?v=[^\"\']+',f'locale-r15.js?v={VER}',t)
    t=re.sub(r'r24-ai-controller\.js\?v=[^\"\']+',f'r24-ai-controller.js?v={VER}',t)
    if t!=before:
        p.write_text(t,encoding='utf-8'); changed.append(p.name)

print('R30 changed',len(changed),'files')
for x in changed: print(x)
