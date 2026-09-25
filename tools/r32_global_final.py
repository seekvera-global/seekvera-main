from pathlib import Path
import re

VER='20260925-r32-global-final'
changed=[]

def write(path,text):
    p=Path(path); old=p.read_text(encoding='utf-8') if p.exists() else ''
    if old!=text:
        p.write_text(text,encoding='utf-8'); changed.append(path)

# Replace the old layered translation file with one deterministic universal runtime.
write('i18n-ui.js',Path('r32-i18n.js').read_text(encoding='utf-8'))

# Locale coordinator keeps the same 248-country source of truth but advertises R32.
p=Path('locale-r15.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"version:'[^']+'",f"version:'{VER}'",s,count=1)
write('locale-r15.js',s)

# The older deterministic R14 layer still runs on the homepage after R32 and can overwrite
# a few critical labels/direction values. Keep it aligned so it cannot re-introduce English
# or force Pashto back to LTR after the universal pack has already localized the page.
p=Path('locale-r14.js'); s=p.read_text(encoding='utf-8')
old=s
s,n=re.subn(r"(fil:\[(?:`[^`]*`,){18})`Live marketplace`",r"\1`Aktuwal na pamilihan`",s,count=1)
if n!=1 and 'Aktuwal na pamilihan' not in s: raise SystemExit('Filipino R14 live-marketplace anchor missing')
s=s.replace("const RTL=new Set(['ar','fa','ur','he','dv']);","const RTL=new Set(['ar','fa','ur','he','ps','dv']);",1)
if "const RTL=new Set(['ar','fa','ur','he','ps','dv']);" not in s: raise SystemExit('R14 RTL anchor missing')
write('locale-r14.js',s)

# AI: never answer a simple greeting in English when another country language is selected.
p=Path('worker-r31.js'); s=p.read_text(encoding='utf-8')
old="function instantGreeting(language){const x=language.toLowerCase();if(x==='arabic')return'أهلاً! أنا مساعد SEEKVERA. قل لي ماذا تحتاج وسأساعدك بسرعة وأوصلك للقسم المناسب.';if(x==='french')return'Bonjour ! Je suis l’assistant SEEKVERA. Dites-moi ce dont vous avez besoin et je vous guiderai rapidement.';if(x==='chinese')return'你好！我是 SEEKVERA 助手。告诉我你需要什么，我会快速帮你找到合适的栏目。';if(x==='hindi')return'नमस्ते! मैं SEEKVERA सहायक हूँ। बताइए आपको क्या चाहिए, मैं जल्दी सही सेक्शन तक पहुँचने में मदद करूँगा।';return'Hi! I’m the SEEKVERA assistant. Tell me what you need and I’ll quickly help you find the right section.'}"
new="function instantGreeting(language){const x=language.toLowerCase();if(x==='english')return'Hi! I’m the SEEKVERA assistant. Tell me what you need and I’ll quickly help you find the right section.';if(x==='arabic')return'أهلاً! أنا مساعد SEEKVERA. قل لي ماذا تحتاج وسأساعدك بسرعة وأوصلك للقسم المناسب.';if(x==='french')return'Bonjour ! Je suis l’assistant SEEKVERA. Dites-moi ce dont vous avez besoin et je vous guiderai rapidement.';if(x==='chinese')return'你好！我是 SEEKVERA 助手。告诉我你需要什么，我会快速帮你找到合适的栏目。';if(x==='hindi')return'नमस्ते! मैं SEEKVERA सहायक हूँ। बताइए आपको क्या चाहिए, मैं जल्दी सही सेक्शन तक पहुँचने में मदद करूँगा।';return''}"
if old in s:s=s.replace(old,new,1)
else: raise SystemExit('instantGreeting anchor missing')
old="if(simple(m))return json(req,{ok:true,response:instantGreeting(language),model:'seekvera-local-instant',language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath:'r31-local-instant'});"
new="if(simple(m)){const greeting=instantGreeting(language);if(greeting)return json(req,{ok:true,response:greeting,model:'seekvera-local-instant',language,category:cat,route:ROUTE[cat]||ROUTE.general,countryAction:null,languageAction:null,liveData:false,fastPath:'r32-local-instant'});}"
if old in s:s=s.replace(old,new,1)
else: raise SystemExit('simple greeting anchor missing')
anchor="async function runModel(env,md,messages,maxTokens){"
helper="""async function localizedFallback(env,language,cat){const base=fallbackGuide(language==='Arabic'?'Arabic':'English',cat);if(language==='English'||language==='Arabic')return base;try{const r=await Promise.race([runModel(env,FAST,[{role:'system',content:`Translate the user-interface help sentence into ${language}. Return only the translation.`},{role:'user',content:base}],140),(async()=>{await sleep(1800);throw Error('fallback translate timeout')})()]);if(r?.text)return r.text}catch{}return'…'}\n"""
if helper.strip() not in s:
    if anchor not in s: raise SystemExit('runModel anchor missing')
    s=s.replace(anchor,helper+anchor,1)
old="const response=got?.text||fallbackGuide(language,cat),model=got?.model||'seekvera-latency-fallback';"
new="const response=got?.text||await localizedFallback(env,language,cat),model=got?.model||'seekvera-r32-localized-fallback';"
if old in s:s=s.replace(old,new,1)
else: raise SystemExit('fallback response anchor missing')
s=s.replace("text=text.replace(/2026-09-25 · R20/g,'2026-09-25 · R31C');","text=text.replace(/2026-09-25 · R(?:20|31C|32)/g,'2026-09-25 · R32');",1)
s=s.replace("h.set('x-seekvera-release','r31c')","h.set('x-seekvera-release','r32-global-final')",1)
s=s.replace("r31Runtime:'atomic-locale-localized-currency-fast-voice-smart-ai-r31c'","r31Runtime:'atomic-locale-localized-currency-fast-voice-smart-ai-r31c',r32:true,r32Runtime:'248-country-full-ui-language-lock-global-final'",1)
write('worker-r31.js',s)

# Bust every page and PWA cache so old phones cannot keep R19/R20 translation files.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    t=p.read_text(encoding='utf-8'); before=t
    t=re.sub(r'i18n-ui\.js\?v=[^\"\']+',f'i18n-ui.js?v={VER}',t)
    t=re.sub(r'sw\.js\?v=[^\"\']+',f'sw.js?v={VER}',t)
    if p.name=='index.html':
        t=re.sub(r'2026-09-25 · R(?:20|31C|32)','2026-09-25 · R32',t)
    if t!=before: p.write_text(t,encoding='utf-8'); changed.append(p.name)

p=Path('sw.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"const CACHE='[^']+'",f"const CACHE='seekvera-r32-global-final-20260925'",s,count=1)
write('sw.js',s)

print('R32 changed',len(changed),'files')
for x in changed: print(x)
