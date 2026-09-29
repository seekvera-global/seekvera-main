from pathlib import Path
import re

VER='20260929-r113-ai-reliability'

def rw(name, fn):
    p=Path(name)
    s=p.read_text(encoding='utf-8')
    n=fn(s)
    if n==s:
        print(name, 'no-change')
    else:
        p.write_text(n,encoding='utf-8')
        print(name, 'patched')


def patch_worker(s):
    s=re.sub(r"const RELEASE='[^']+'", f"const RELEASE='{VER}'", s, count=1)
    a=s.index('async function degradedFallback(request,env,ctx,body,message){')
    b=s.index('\nasync function runStructured(env,body){',a)
    degraded="""async function degradedFallback(request,env,ctx,body,message){
 const act=actionState(message,'','',body?.clientControls),language=messageLanguage(message,body?.language),meta=metaConversation(message),chat=conversationOnly(message)||meta,requested=category(body?.conversationIntent||message),cat=(act.isAction||chat)?'general':(requested==='jobs'&&!employmentIntent(message)?'general':requested),response=act.isAction?actionReply(language,act.cc,act.ll):meta?metaReply(message,language):chat?conversationalFallback(message,language):usefulFallback(message,language,cat);
 return json(request,{ok:true,response,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'seekvera-r113-instant-local-fallback',fastPath:'r113-bounded-fallback',liveData:false},200)
}
"""
    s=s[:a]+degraded+s[b:]
    fn=s.index('async function runStructured(env,body){')
    start=s.index(' for(const model of [PRIMARY,FALLBACK]){try{',fn)
    end=s.index(' // Keep a real conversational AI fallback',start)
    model_block=""" const modelAttempt=async model=>{
   const r=await Promise.race([env.AI.run(model,{messages,temperature:.2,max_tokens:760}),new Promise((_,reject)=>setTimeout(()=>reject(Error('model timeout')),4200))]),text=modelText(r),obj=parseJSON(text);if(!obj||!clean(obj.reply,5000))throw Error('invalid structured response');
   const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=messageLanguage(message,obj.languageCode),meta=metaConversation(message),cat=(act.isAction||conversationOnly(message)||meta)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));
   let reply=act.isAction?actionReply(language,act.cc,act.ll):clean(obj.reply,5000);if(meta&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);
   return{ok:true,response:reply,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model,fastPath:act.isAction?'r113-verified-action-first':meta?'r113-meta-conversation-guard':'r113-bounded-structured-ai',liveData:false}
 };
 try{const winner=await Promise.race([Promise.any([PRIMARY,FALLBACK].map(modelAttempt)),new Promise(resolve=>setTimeout(()=>resolve(null),4500))]);if(winner)return winner}catch(_){}
"""
    s=s[:start]+model_block+s[end:]
    backup_start=s.index(' // Keep a real conversational AI fallback',fn)
    backup_end=s.index('\n return null;\n}',backup_start)
    backup=""" // Keep a real conversational AI fallback, but never let it stall the UI.
 try{
   const backupPrompt=messages.map(x=>String(x?.role||'user').toUpperCase()+': '+String(x?.content||'')).join('\\n').slice(-14000);
   const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),2200);
   try{
     const br=await fetch('https://text.pollinations.ai/'+encodeURIComponent(backupPrompt)+'?model=openai&private=true',{headers:{'accept':'text/plain','user-agent':'SEEKVERA/1.0'},signal:ctl.signal});
     if(br.ok){
       const raw=await br.text(),obj=parseJSON(raw);
       if(obj&&clean(obj.reply,5000)){
         const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=messageLanguage(message,obj.languageCode),meta=metaConversation(message),cat=(act.isAction||conversationOnly(message)||meta)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));
         let reply=act.isAction?actionReply(language,act.cc,act.ll):clean(obj.reply,5000);if(meta&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);
         return{ok:true,response:reply,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'pollinations-private-conversation-fallback',fastPath:'r113-real-ai-fallback',liveData:false}
       }
       const plain=clean(raw,5000);if(plain){const language=messageLanguage(message,''),meta=metaConversation(message),cat=(conversationOnly(message)||meta)?'general':(category(message)==='jobs'&&!employmentIntent(message)?'general':category(message));return{ok:true,response:plain,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:null,languageAction:null,model:'pollinations-private-conversation-plain',fastPath:'r113-natural-plain-fallback',liveData:false}}
     }
   }finally{clearTimeout(to)}
 }catch(_){}
"""
    s=s[:backup_start]+backup+s[backup_end:]
    return s


def patch_super(s):
    s=re.sub(r'const RELEASE = "[^"]+";',f'const RELEASE = "{VER}";',s,count=1)
    s=s.replace('timer = setTimeout(() => controller.abort(), 18000);','timer = setTimeout(() => controller.abort(), 7500);')
    return s


def patch_r31(s):
    s=re.sub(r'const VERSION = "[^"]+";',f'const VERSION = "{VER}";',s,count=1)
    s=s.replace('t = setTimeout(() => c.abort(), 18000);','t = setTimeout(() => c.abort(), 7200);')
    return s


def patch_voice(s):
    s=s.replace("window.__seekveraVoiceMode='hybrid-native-whisper-r103'",f"window.__seekveraVoiceMode='{VER}'")
    s=s.replace("const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),10000)","const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),4500)")
    old="""  const token=++speakToken,android=/Android/i.test(navigator.userAgent);
  if(android){serverSpeakSequence(chunks,lastLocale,token).then(ok=>{if(!ok&&token===speakToken&&!muted)nativeSpeak(chunks,token)});return}
  if(nativeSpeak(chunks,token))return;
  serverSpeakSequence(chunks,lastLocale,token)
"""
    new="""  const token=++speakToken;
  if(nativeSpeak(chunks,token))return;
  serverSpeakSequence(chunks,lastLocale,token)
"""
    if old not in s and new not in s:
        raise SystemExit('voice speak strategy anchor missing')
    s=s.replace(old,new,1)
    s=s.replace("const arm=()=>{clearTimeout(watchdog);watchdog=setTimeout(fallback,4200)};","const arm=()=>{clearTimeout(watchdog);watchdog=setTimeout(fallback,/Android/i.test(navigator.userAgent)?1900:3200)};")
    return s


def patch_sw(s):
    return re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,count=1)


def patch_index(s):
    for name in ['superapp.js','voice-ai.js','r31-ui-polish.js']:
        s=re.sub(re.escape(name)+r'\?v=[^"\']+',name+'?v='+VER,s)
    s=re.sub(r'sw\.js\?v=[^"\']+', 'sw.js?v='+VER, s)
    return s

rw('worker-r76.js',patch_worker)
rw('superapp.js',patch_super)
rw('r31-ui-polish.js',patch_r31)
rw('voice-ai.js',patch_voice)
rw('sw.js',patch_sw)
rw('index.html',patch_index)
