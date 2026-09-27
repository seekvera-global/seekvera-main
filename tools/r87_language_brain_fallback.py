from pathlib import Path
import re

VER='20260927-r87-language-independent-ai-brain'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const RELEASE='20260927-r86-true-multilingual-conversation-voice';",f"const RELEASE='{VER}';",1)

# The latest user message decides reply language, never the selected UI language/country.
s=s.replace("language=act.isAction?messageLanguage(message,d.language):normalizedLanguage(d.language,message)","language=messageLanguage(message,d.language)",1)
s=s.replace("language=act.isAction?messageLanguage(message,obj.languageCode):(languageCode(obj.languageCode)||normalizedLanguage('',message))","language=messageLanguage(message,obj.languageCode)",1)

# Add a real conversational model fallback when the Workers AI allocation/model is unavailable.
old=" }catch{}}\n return null;\n}\n\nexport default{async fetch(request,env,ctx){"
backup=r''' }catch{}}
 // Keep a real conversational AI fallback instead of dropping immediately to fixed keyword templates.
 try{
   const backupPrompt=messages.map(x=>String(x?.role||'user').toUpperCase()+': '+String(x?.content||'')).join('\n').slice(-14000);
   const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),9000);
   try{
     const br=await fetch('https://text.pollinations.ai/'+encodeURIComponent(backupPrompt)+'?model=openai&private=true',{headers:{'accept':'text/plain','user-agent':'SEEKVERA/1.0'},signal:ctl.signal});
     if(br.ok){const obj=parseJSON(await br.text());if(obj&&clean(obj.reply,5000)){
       const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=messageLanguage(message,obj.languageCode),meta=metaConversation(message),cat=(conversationOnly(message)||meta)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));
       let reply=act.isAction?actionReply(language,act.cc,act.ll):clean(obj.reply,5000);if(meta&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);
       return{ok:true,response:reply,language,category:cat,route:ROUTES[cat]||ROUTES.general,countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'pollinations-private-conversation-fallback',fastPath:'r87-real-ai-fallback',liveData:false}
     }}
   }finally{clearTimeout(to)}
 }catch{}
 return null;
}

export default{async fetch(request,env,ctx){'''
if old not in s: raise SystemExit('runStructured ending anchor missing')
s=s.replace(old,backup,1)

# Update health marker/version wording.
s=s.replace("r86Runtime:'conversation-first-multilingual-ai'","r86Runtime:'conversation-first-multilingual-ai',r87:true,r87Runtime:'latest-message-language-plus-real-ai-fallback'",1)
p.write_text(s,encoding='utf-8')

# Cache-bust the page marker while preserving R86 voice asset version.
p=Path('index.html')
h=p.read_text(encoding='utf-8')
h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
p.write_text(h,encoding='utf-8')
