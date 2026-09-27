from pathlib import Path
import re

VER='20260927-r88-live-voice-speaker-final'

# Reuse the tested voice-side edits from R88. That script intentionally stops
# at the old worker fallback anchor on current main; by then voice-ai.js is already written.
try:
    exec(Path('tools/r88_voice_speaker_final.py').read_text(encoding='utf-8'),{})
except SystemExit as e:
    if 'R87 pollinations return anchor missing' not in str(e):
        raise

# Finish the worker edits robustly against current R87 source.
p=Path('worker-r76.js')
w=p.read_text(encoding='utf-8')
w=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",w,count=1)

old="for(const model of [ASR_PRIMARY,ASR_PRIMARY,ASR_FALLBACK]){try{\n   const r=await env.AI.run(model,base),text=clean(r?.text||r?.result?.text||r?.result||'',5000);"
new="for(const model of [ASR_PRIMARY,ASR_FALLBACK]){try{\n   const r=await Promise.race([env.AI.run(model,base),new Promise((_,reject)=>setTimeout(()=>reject(Error('asr timeout')),8000))]),text=clean(r?.text||r?.result?.text||r?.result||'',5000);"
if old in w:
    w=w.replace(old,new,1)
elif "for(const model of [ASR_PRIMARY,ASR_FALLBACK])" not in w:
    raise SystemExit('R88b ASR loop missing')

old="if(br.ok){const obj=parseJSON(await br.text());if(obj&&clean(obj.reply,5000)){"
new="if(br.ok){const raw=await br.text(),obj=parseJSON(raw);if(obj&&clean(obj.reply,5000)){"
if old in w:
    w=w.replace(old,new,1)
elif "const raw=await br.text(),obj=parseJSON(raw)" not in w:
    raise SystemExit('R88b pollinations raw anchor missing')

if "r88-natural-plain-fallback" not in w:
    close="     }}\n   }finally{clearTimeout(to)}"
    plain="     }}\n     const plain=clean(raw,5000);if(plain){const language=messageLanguage(message,''),meta=metaConversation(message),cat=(conversationOnly(message)||meta)?'general':(category(message)==='jobs'&&!employmentIntent(message)?'general':category(message));return{ok:true,response:plain,language,category:cat,route:ROUTES[cat]||ROUTES.general,countryAction:null,languageAction:null,model:'pollinations-private-conversation-plain',fastPath:'r88-natural-plain-fallback',liveData:false}}\n   }finally{clearTimeout(to)}"
    if close not in w: raise SystemExit('R88b pollinations close anchor missing')
    w=w.replace(close,plain,1)

needle="r87:true,r87Runtime:'latest-message-language-plus-real-ai-fallback',"
if "r88:true" not in w:
    if needle not in w: raise SystemExit('R88b health anchor missing')
    w=w.replace(needle,"r88:true,r88Runtime:'fast-auto-asr-server-first-tts-natural-fallback',"+needle,1)
p.write_text(w,encoding='utf-8')

# Cache-bust home voice bundle and SW.
p=Path('index.html')
h=p.read_text(encoding='utf-8')
h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
h=re.sub(r'voice-ai\.js\?v=[^"\s]+',f'voice-ai.js?v={VER}',h,count=1)
h=re.sub(r'r31-ui-polish\.js\?v=[^"\s]+',f'r31-ui-polish.js?v={VER}',h,count=1)
h=re.sub(r'sw\.js\?v=[^"\s]+',f'sw.js?v={VER}',h,count=1)
p.write_text(h,encoding='utf-8')

p=Path('sw.js')
sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1)
p.write_text(sw,encoding='utf-8')

print('R88b final voice/speaker patch applied')
