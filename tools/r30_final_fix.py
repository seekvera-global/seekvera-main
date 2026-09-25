from pathlib import Path
import re

VER='20260925-r30-final'
changed=[]

def write(path,text):
    p=Path(path); old=p.read_text(encoding='utf-8')
    if old!=text:
        p.write_text(text,encoding='utf-8'); changed.append(path)

# i18n: self-heal guard, translate dynamic action text, parallelize missing translations,
# add instant Arabic strings reported by the user, and never leave English visible in a
# non-English UI if an online translation is still pending/unavailable.
p=Path('i18n-ui.js'); s=p.read_text(encoding='utf-8')
s=s.replace("if(window.__seekveraLocaleGuardR9)return;window.__seekveraLocaleGuardR9=true;","if(window.__seekveraLocaleGuardR9&&window.SEEKVERA_LOCALE_GUARD_R9)return;window.__seekveraLocaleGuardR9=true;",1)
s=re.sub(r"const VERSION='20260925-r(?:19-no-mixed-language|30[^']*)';",f"const VERSION='{VER}-no-mixed-language';",s,count=1)
s=s.replace(".sv-ai-answer,.sv-ai-actions,[data-no-translate]",".sv-ai-answer,[data-no-translate]",1)
marker='/* R30 FINAL instant reported-string translations */'
if marker not in s:
    anchor='window.__SEEKVERA_R9_QUICK=QUICK;'
    addition="""/* R30 FINAL instant reported-string translations */
Object.assign(QUICK.ar,{
'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'لا توجد حالياً إعلانات سوق مباشرة معتمدة. لا تنشئ SEEKVERA إعلانات وهمية.',
'No approved live marketplace listings are available right now':'لا توجد حالياً إعلانات سوق مباشرة معتمدة.',
'SEEKVERA does not generate fake listings':'لا تنشئ SEEKVERA إعلانات وهمية.',
'Loading approved listings…':'جارٍ تحميل الإعلانات المعتمدة…','Live marketplace':'السوق المباشر','Approved real listings only.':'إعلانات حقيقية معتمدة فقط.','OPEN MARKETPLACE →':'افتح السوق ←',
'Find, compare, choose — worldwide.':'ابحث وقارن واختر — حول العالم.','Find, compare, choose — worldwide':'ابحث وقارن واختر — حول العالم',
'Chat · Voice · Camera · Attach':'دردشة · صوت · كاميرا · إرفاق','Online':'متصل','Message SEEKVERA AI…':'راسل ذكاء SEEKVERA…',
'Request anything':'اطلب أي شيء','Tell SEEKVERA what you need anywhere in the world.':'أخبر SEEKVERA بما تحتاج إليه في أي مكان في العالم.',
'About':'حول','Privacy':'الخصوصية','Terms':'الشروط','Contact':'تواصل','Disclosure':'الإفصاح'
});
"""
    if anchor not in s: raise SystemExit('i18n quick anchor missing')
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
old2="else if(l!=='en'&&node.parentElement?.closest?.('.r5-tile-body small,.r5-section-head p,.r5-ai-note,.r5-foot small'))node.nodeValue=node.nodeValue.replace(node.nodeValue.trim(),'…')"
new2="else if(l!=='en'&&node.parentElement?.closest?.('header,main,footer,nav,.sv-modal'))node.nodeValue=node.nodeValue.replace(node.nodeValue.trim(),'…')"
if old2 in s: s=s.replace(old2,new2,1)
write('i18n-ui.js',s)

# Atomic country coordinator: country must drive language/currency and force the complete UI pass.
p=Path('locale-r15.js'); s=p.read_text(encoding='utf-8')
if 'SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)' not in s:
    s=s.replace("try{window.SEEKVERA_I18N?.apply?.()}catch{}","try{window.SEEKVERA_I18N?.apply?.()}catch{}\n  try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)}catch{}",1)
    s=s.replace("try{window.SEEKVERA_R14_CATEGORIES?.apply?.()}catch{}\n    localizeCountryOptions(state);","try{window.SEEKVERA_R14_CATEGORIES?.apply?.()}catch{}\n    try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)}catch{}\n    localizeCountryOptions(state);",1)
s=re.sub(r"version:'20260924-r15'",f"version:'{VER}'",s,count=1)
write('locale-r15.js',s)

# AI controller: every programmatic country/language change also refreshes the visible translator.
p=Path('r24-ai-controller.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"const VERSION='20260925-r24-unified-control';",f"const VERSION='{VER}-unified-control';",s,count=1)
if "SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)" not in s:
    s=s.replace("function refresh(){try{window.SEEKVERA_I18N?.apply?.()}catch{}","function refresh(){try{window.SEEKVERA_I18N?.apply?.()}catch{}try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(0)}catch{}",1)
write('r24-ai-controller.js',s)

# Voice: allow a natural pause while listening, make Android TTS segments safer, and add a
# short gap before the next segment so the device speech engine does not drop it.
p=Path('voice-ai.js'); s=p.read_text(encoding='utf-8')
s=s.replace('const TTS_RETRY_DELAYS=[240,650,1200];','const TTS_RETRY_DELAYS=[120,350,700,1300];',1)
s=s.replace('const VOICE_SILENCE_MS=1250,VOICE_MAX_MS=30000,VOICE_RMS_THRESHOLD=.016;','const VOICE_SILENCE_MS=2100,VOICE_MAX_MS=45000,VOICE_RMS_THRESHOLD=.014;',1)
s=s.replace("{1,170}(?:[.!?。！？؛،,:;]+|$)","{1,105}(?:[.!?。！？؛،,:;]+|$)",1)
s=s.replace("while(p.length>190){let cut=p.lastIndexOf(' ',180);if(cut<80)cut=180;","while(p.length>125){let cut=p.lastIndexOf(' ',115);if(cut<55)cut=115;",1)
s=s.replace("return out.length?out:[s.slice(0,190)]","return out.length?out:[s.slice(0,125)]",1)
s=s.replace("u.onend=()=>{finished=true;if(token===speakToken)play(index+1,0)}","u.onend=()=>{finished=true;if(token===speakToken)setTimeout(()=>play(index+1,0),90)}",1)
write('voice-ai.js',s)

# Base worker remains the safe fallback behind worker-r30; keep its non-fast fallback leaner too.
p=Path('worker.js'); s=p.read_text(encoding='utf-8')
s=s.replace("const script=scriptLanguage(text);if(script)return script;if(!env.AI)return h&&!/^auto$/i.test(h)?h:'the language used by the user';","const script=scriptLanguage(text);if(script)return script;if(h&&!/^auto$/i.test(h))return h;if(!env.AI)return'the language used by the user';",1)
s=s.replace("const hist=Array.isArray(b.history)?b.history.slice(-12)","const hist=Array.isArray(b.history)?b.history.slice(b.fast?-8:-12)",1)
s=s.replace("const detected=await detectedLanguage(env,m,b.language),c=await classifyIntent(env,contextText),p=","const detected=await detectedLanguage(env,m,b.language),c=b.fast?category(contextText):await classifyIntent(env,contextText),p=",1)
s=s.replace("],520,.14);const rawResponse=", "],b.fast?360:520,.14);const rawResponse=",1)
write('worker.js',s)

# Force all phones/browsers off old JS and service-worker caches.
p=Path('sw.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"const CACHE='[^']+';",f"const CACHE='seekvera-r30-final-20260925';",s,count=1)
s=s.replace("'./r24-ai-controller.js'","'./r24-ai-controller.js','./r30-runtime.js'",1) if "'./r30-runtime.js'" not in s else s
s=s.replace("x-seekvera-release','r23-stable'","x-seekvera-release','r30-final'",1)
write('sw.js',s)

for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    t=p.read_text(encoding='utf-8'); before=t
    for name in ['i18n-ui','voice-ai','locale-r15','r24-ai-controller']:
        t=re.sub(rf'{re.escape(name)}\.js\?v=[^\"\']+',f'{name}.js?v={VER}',t)
    t=re.sub(r'sw\.js\?v=[^\"\']+',f'sw.js?v={VER}',t)
    if t!=before:
        p.write_text(t,encoding='utf-8'); changed.append(p.name)

print('R30 FINAL changed',len(changed),'files')
for x in changed: print(x)
