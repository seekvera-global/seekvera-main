from pathlib import Path


def patch_i18n():
    p=Path('i18n-ui.js'); s=p.read_text(encoding='utf-8')
    s=s.replace("const VERSION='20260925-r19-no-mixed-language';","const VERSION='20260925-r30-no-mixed-language-fast';",1)
    marker="Object.assign(QUICK.hi,{"
    if "R30 screenshot/core translations" not in s:
        extra="""// R30 screenshot/core translations: instant while universal translation fills the rest.\nObject.assign(QUICK.ar,{\n'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'لا توجد حالياً إعلانات سوق مباشرة معتمدة. SEEKVERA لا ينشئ إعلانات وهمية.',\n'No approved live marketplace listings are available right now':'لا توجد حالياً إعلانات سوق مباشرة معتمدة',\n'SEEKVERA does not generate fake listings':'SEEKVERA لا ينشئ إعلانات وهمية',\n'Find, compare, choose — worldwide.':'ابحث، قارن، واختر — حول العالم.',\n'Chat · Voice · Camera · Attach':'دردشة · صوت · كاميرا · إرفاق',\n'Online':'متصل',\n'Loading approved listings…':'جارٍ تحميل الإعلانات المعتمدة…'\n});\n"""
        if marker not in s: raise SystemExit('i18n quick marker missing')
        s=s.replace(marker,extra+marker,1)
    old=""" let remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 for(let i=0;i<remaining.length;i+=12)await requestBatch(remaining.slice(i,i+12));
 remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 for(let i=0;i<remaining.length;i+=4)await requestBatch(remaining.slice(i,i+4));
 return out
}"""
    new=""" let remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 const parallel=async(list,size)=>{for(let i=0;i<list.length;i+=size*4){const jobs=[];for(let j=i;j<Math.min(list.length,i+size*4);j+=size)jobs.push(requestBatch(list.slice(j,j+size)));await Promise.all(jobs)}};
 await parallel(remaining,12);
 remaining=arr.filter(src=>!out.has(src)&&!cached(l,src));
 await parallel(remaining,4);
 return out
}"""
    if new not in s:
        if old not in s: raise SystemExit('i18n sequential batch anchor missing')
        s=s.replace(old,new,1)
    old2="else if(l!=='en'&&node.parentElement?.closest?.('.r5-tile-body small,.r5-section-head p,.r5-ai-note,.r5-foot small'))node.nodeValue=node.nodeValue.replace(node.nodeValue.trim(),'…')"
    new2="else if(l!=='en'&&node.parentElement?.closest?.('header,main,footer,nav,.sv-modal'))node.nodeValue=node.nodeValue.replace(node.nodeValue.trim(),'…')"
    if new2 not in s:
        if old2 not in s: raise SystemExit('i18n leak guard anchor missing')
        s=s.replace(old2,new2,1)
    p.write_text(s,encoding='utf-8')


def patch_voice():
    p=Path('voice-ai.js'); s=p.read_text(encoding='utf-8')
    s=s.replace("const TTS_RETRY_DELAYS=[240,650,1200];","const TTS_RETRY_DELAYS=[120,350,800,1500];",1)
    old="function splitSpeech(t){const s=cleanSpeech(t);if(!s)return[];const parts=s.match(/[^.!?。！？؛،,:;]{1,170}(?:[.!?。！？؛،,:;]+|$)/g)||[];const out=[];for(const p0 of parts){let p=p0.trim();while(p.length>190){let cut=p.lastIndexOf(' ',180);if(cut<80)cut=180;out.push(p.slice(0,cut).trim());p=p.slice(cut).trim()}if(p)out.push(p)}return out.length?out:[s.slice(0,190)]}"
    new="function splitSpeech(t){const s=cleanSpeech(t);if(!s)return[];const parts=s.match(/[^.!?。！？؟]{1,520}(?:[.!?。！？؟]+|$)/g)||[s];const out=[];let buf='';const push=p=>{p=String(p||'').trim();if(p)out.push(p)};for(const raw of parts){let p=raw.trim();if(!p)continue;if(buf&&(buf+' '+p).length<=420){buf+=' '+p;continue}if(buf){push(buf);buf=''}while(p.length>460){let cut=p.lastIndexOf(' ',440);if(cut<180)cut=440;push(p.slice(0,cut));p=p.slice(cut).trim()}buf=p}push(buf);return out.length?out:[s]}"
    if new not in s:
        if old not in s: raise SystemExit('voice split anchor missing')
        s=s.replace(old,new,1)
    s=s.replace("u.onend=()=>{finished=true;if(token===speakToken)play(index+1,0)}","u.onend=()=>{finished=true;if(token===speakToken)setTimeout(()=>play(index+1,0),90)}",1)
    p.write_text(s,encoding='utf-8')


def patch_worker():
    p=Path('worker.js'); s=p.read_text(encoding='utf-8')
    s=s.replace("const RELEASE='20260924-ai-r17'","const RELEASE='20260925-ai-r30-fast-voice-language'",1)
    s=s.replace("async function ai(env,messages,max=320,temp=.2){","async function ai(env,messages,max=320,temp=.2,preferFast=false){",1)
    old="const order=/Safety Gate|moderation|safety review/i.test(first)?[PRIMARY,FALLBACK,LIGHT,FASTCHAT]:quality?[FALLBACK,PRIMARY,LIGHT,FASTCHAT]:[FALLBACK,PRIMARY,LIGHT,FASTCHAT];"
    new="const order=/Safety Gate|moderation|safety review/i.test(first)?[FASTCHAT,FALLBACK,LIGHT,PRIMARY]:preferFast?[FASTCHAT,FALLBACK,LIGHT,PRIMARY]:quality?[FALLBACK,FASTCHAT,PRIMARY,LIGHT]:[FALLBACK,FASTCHAT,LIGHT,PRIMARY];"
    if new not in s:
        if old not in s: raise SystemExit('AI model order anchor missing')
        s=s.replace(old,new,1)
    old="const detected=await detectedLanguage(env,m,b.language),c=await classifyIntent(env,contextText),p="
    new="const [detected,c]=await Promise.all([detectedLanguage(env,m,b.language),b.fast?Promise.resolve(category(contextText)):classifyIntent(env,contextText)]),p="
    if new not in s:
        if old not in s: raise SystemExit('AI parallel detection anchor missing')
        s=s.replace(old,new,1)
    old="],520,.14);const rawResponse="
    new="],b.fast?360:520,b.fast?0.08:0.14,Boolean(b.fast));const rawResponse="
    if new not in s:
        if old not in s: raise SystemExit('AI fast call anchor missing')
        s=s.replace(old,new,1)
    s=s.replace("aiResilience:'r17-message-language-auto-glm-first'","aiResilience:'r30-fastchat-first-parallel-language'",1)
    p.write_text(s,encoding='utf-8')


patch_i18n(); patch_voice(); patch_worker()
print('R30 runtime patches ready')
