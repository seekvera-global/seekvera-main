from pathlib import Path
import re

VER='20260929-r117-strict-reply-language'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",s,count=1)

# Recognize the user's exact Lebanese/Arabic employment phrasing too.
old="|عم دور على شغل|بدي شغل|بدور على شغل|دوام|"
new="|عم دور على شغل|عم بدور على شغل|بدي شغل|بدور على شغل|ندور على شغل|دورلي على شغل|ساعدني دور على شغل|ساعديني دور على شغل|ساعديني ندور على شغل|دوام|"
if old in s:
    s=s.replace(old,new,1)
elif 'ساعديني ندور على شغل' not in s:
    raise SystemExit('R117 employment anchor missing')

helper=r'''
function replyScript(text){
 const t=String(text||'');
 if(/[\u0600-\u06ff]/u.test(t))return'arabic';
 if(/[\u0900-\u097f]/u.test(t))return'devanagari';
 if(/[\u0980-\u09ff]/u.test(t))return'bengali';
 if(/[\u0a00-\u0a7f]/u.test(t))return'gurmukhi';
 if(/[\u0a80-\u0aff]/u.test(t))return'gujarati';
 if(/[\u0b80-\u0bff]/u.test(t))return'tamil';
 if(/[\u0c00-\u0c7f]/u.test(t))return'telugu';
 if(/[\u0d00-\u0d7f]/u.test(t))return'malayalam';
 if(/[\u0d80-\u0dff]/u.test(t))return'sinhala';
 if(/[\u0e00-\u0e7f]/u.test(t))return'thai';
 if(/[\u0e80-\u0eff]/u.test(t))return'lao';
 if(/[\u1000-\u109f]/u.test(t))return'myanmar';
 if(/[\u1200-\u137f]/u.test(t))return'ethiopic';
 if(/[\u1780-\u17ff]/u.test(t))return'khmer';
 if(/[\u10a0-\u10ff]/u.test(t))return'georgian';
 if(/[\u0530-\u058f]/u.test(t))return'armenian';
 if(/[\u0370-\u03ff]/u.test(t))return'greek';
 if(/[\u0590-\u05ff]/u.test(t))return'hebrew';
 if(/[\u3040-\u30ff]/u.test(t))return'japanese';
 if(/[\uac00-\ud7af]/u.test(t))return'korean';
 if(/[\u4e00-\u9fff]/u.test(t))return'han';
 if(/[\u0400-\u052f]/u.test(t))return'cyrillic';
 if(/[A-Za-zÀ-ÖØ-öø-ÿ]/u.test(t))return'latin';
 return''
}
function expectedReplyScripts(language){
 const l=languageCode(language);
 if(['ar','fa','ur','ps','ku'].includes(l))return['arabic'];
 if(['hi','mr','ne'].includes(l))return['devanagari'];
 if(l==='bn')return['bengali'];if(l==='pa')return['gurmukhi'];if(l==='gu')return['gujarati'];if(l==='ta')return['tamil'];if(l==='te')return['telugu'];if(l==='ml')return['malayalam'];if(l==='si')return['sinhala'];
 if(l==='th')return['thai'];if(l==='lo')return['lao'];if(l==='my')return['myanmar'];if(['am','ti'].includes(l))return['ethiopic'];if(l==='km')return['khmer'];if(l==='ka')return['georgian'];if(l==='hy')return['armenian'];if(l==='el')return['greek'];if(l==='he')return['hebrew'];
 if(l==='ja')return['japanese','han'];if(l==='zh')return['han'];if(l==='ko')return['korean'];if(['ru','uk','bg','sr','mk','be'].includes(l))return['cyrillic'];
 return['latin']
}
function confidentLatinLanguage(text){
 const t=' '+String(text||'').toLowerCase().replace(/[^a-zà-öø-ÿğışçñ¿¡ðþæœ]+/gu,' ')+' ';
 if(/[ðþ]/u.test(t)||/\b(hvað|þú|það|ertu|erum|leita|þarf|aðstoð|vinna|vinnu)\b/u.test(t))return'is';
 if(/[ğış]/u.test(t)||/\b(merhaba|nasılsın|istiyorum|arıyorum|havaalanı|yakın|teşekkür)\b/u.test(t))return'tr';
 if(/[ãõ]/u.test(t)||/\b(olá|obrigad|procuro|preciso|aeroporto|perto)\b/u.test(t))return'pt';
 if(/[ñ¿¡]/u.test(t)||/\b(hola|quiero|busco|necesito|gracias|aeropuerto|cerca)\b/u.test(t))return'es';
 if(/[äöüß]/u.test(t)||/\b(ich|suche|möchte|danke|flughafen|nähe)\b/u.test(t))return'de';
 if(/\b(bonjour|merci|cherche|voudrais|besoin|aéroport|près|comment allez)\b/u.test(t))return'fr';
 if(/\b(ciao|buongiorno|grazie|cerco|voglio|bisogno|aeroporto|vicino)\b/u.test(t))return'it';
 if(/[đơư]/u.test(t)||/\b(xin chào|cảm ơn|tôi muốn|tôi cần|sân bay)\b/u.test(t))return'vi';
 if(/\b(habari|asante|nataka|nahitaji|hoteli|uwanja wa ndege)\b/u.test(t))return'sw';
 if(/\b(selamat|terima kasih|saya ingin|saya perlu|bandara|dekat)\b/u.test(t))return'id';
 if(/\b(hello|thank you|i need|i want|i am looking|how are you|please tell me|what kind|can you help)\b/u.test(t))return'en';
 return''
}
function translationRequest(message){return /\btranslate\b|\btranslation\b|ترجم|ترجمة|ترجمي|traduire|traducción|traducir|übersetz|traduz|çevir|перевед|翻译|翻訳|번역/iu.test(String(message||''))}
function replyMatchesLanguage(reply,language,message=''){
 const text=clean(reply,5000),l=languageCode(language)||messageLanguage(message,'');if(!text)return false;
 if(translationRequest(message))return true;
 const script=replyScript(text),expected=expectedReplyScripts(l);
 if(script&&script!=='latin')return expected.includes(script);
 if(!expected.includes('latin'))return false;
 const guessed=confidentLatinLanguage(text);return !guessed||guessed===l
}
function guardedReply(reply,language,message=''){const text=clean(reply,5000);return replyMatchesLanguage(text,language,message)?text:''}
function languageSafeHistory(h,target){
 if(!Array.isArray(h))return'';
 return h.slice(-18).filter(x=>x?.role!=='assistant'||replyMatchesLanguage(x?.content,target,'')).map(x=>`${x?.role==='assistant'?'assistant':'user'}: ${clean(x?.content,1000)}`).filter(Boolean).join('\n').slice(-10000)
}
'''
anchor='function safetyReply(language){'
if 'function replyMatchesLanguage(' not in s:
    if anchor not in s: raise SystemExit('R117 helper anchor missing')
    s=s.replace(anchor,helper+'\n'+anchor,1)

# Target language is decided from the actual latest user message, not the model's self-reported language.
s=s.replace("const selected=clean(body?.country,120)||'Worldwide',history=historyText(body?.history);",
            "const selected=clean(body?.country,120)||'Worldwide',targetLanguage=messageLanguage(message,body?.language),history=languageSafeHistory(body?.history,targetLanguage);",1)

old="const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=messageLanguage(message,obj.languageCode),meta=metaConversation(message),cat=(act.isAction||conversationOnly(message)||meta)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));\n   let reply=act.isAction?actionReply(language,act.cc,act.ll):clean(obj.reply,5000);if(meta&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);"
new="const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=targetLanguage,declared=languageCode(obj.languageCode),meta=metaConversation(message),cat=(act.isAction||conversationOnly(message)||meta)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));\n   if(declared&&declared!==language&&!translationRequest(message))throw Error('model language mismatch');\n   let reply=act.isAction?actionReply(language,act.cc,act.ll):guardedReply(obj.reply,language,message);if(!reply)throw Error('reply language mismatch');if(meta&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);"
if old not in s: raise SystemExit('R117 primary model block anchor missing')
s=s.replace(old,new,1)

old2="const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=messageLanguage(message,obj.languageCode),meta=metaConversation(message),cat=(act.isAction||conversationOnly(message)||meta)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));\n         let reply=act.isAction?actionReply(language,act.cc,act.ll):clean(obj.reply,5000);if(meta&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);\n         return{ok:true,response:reply,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'pollinations-private-conversation-fallback',fastPath:'r114-real-ai-fallback',liveData:false}"
new2="const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=targetLanguage,declared=languageCode(obj.languageCode),meta=metaConversation(message),cat=(act.isAction||conversationOnly(message)||meta)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));\n         let reply=act.isAction?actionReply(language,act.cc,act.ll):guardedReply(obj.reply,language,message);if(declared&&declared!==language&&!translationRequest(message))reply='';if(meta&&reply&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);\n         if(reply)return{ok:true,response:reply,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'pollinations-private-conversation-fallback',fastPath:'r117-language-guard-fallback',liveData:false}"
if old2 not in s: raise SystemExit('R117 backup structured block anchor missing')
s=s.replace(old2,new2,1)

old3="const plain=clean(raw,5000);if(plain){const language=messageLanguage(message,''),meta=metaConversation(message),cat=(conversationOnly(message)||meta)?'general':(category(message)==='jobs'&&!employmentIntent(message)?'general':category(message));return{ok:true,response:plain,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:null,languageAction:null,model:'pollinations-private-conversation-plain',fastPath:'r114-natural-plain-fallback',liveData:false}}"
new3="const plain=guardedReply(raw,targetLanguage,message);if(plain){const language=targetLanguage,meta=metaConversation(message),cat=(conversationOnly(message)||meta)?'general':(category(message)==='jobs'&&!employmentIntent(message)?'general':category(message));return{ok:true,response:plain,language,category:cat,route:cat==='general'?null:(ROUTES[cat]||ROUTES.marketplace),countryAction:null,languageAction:null,model:'pollinations-private-conversation-plain',fastPath:'r117-language-guard-plain',liveData:false}}"
if old3 not in s: raise SystemExit('R117 plain fallback anchor missing')
s=s.replace(old3,new3,1)

# Make the contract explicit to the model, especially for Arabic and other non-Latin scripts.
needle='Reply in the SAME language and script as the latest user message unless the user explicitly requests another reply language.'
replacement=needle+' The reply text itself MUST visibly use that language/script; never translate Arabic speech into Icelandic, English, or another language, and never claim one languageCode while writing in another language.'
if needle in s and replacement not in s:s=s.replace(needle,replacement,1)

# Mark health for live verification.
s=s.replace("r105:true,","r117:true,r117Runtime:'strict-reply-language-contract-and-history-sanitizer',r105:true,",1)

p.write_text(s,encoding='utf-8')
print('R117 strict reply language guard applied')
