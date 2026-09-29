from pathlib import Path
import re

VER='20260929-r120-fast-multilingual-actions'

# --- Worker fast path ---
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+'",f"const RELEASE='{VER}'",s,count=1)

# A valid same-script reply is more trustworthy than the model's declared language metadata.
s=s.replace("if(declared&&declared!==language&&!translationRequest(message))throw Error('model language mismatch');","if(declared&&declared!==language&&!translationRequest(message)&&!replyMatchesLanguage(obj.reply,language,message))throw Error('model language mismatch');",1)
s=s.replace("let reply=act.isAction?actionReply(language,act.cc,act.ll):guardedReply(obj.reply,language,message);if(declared&&declared!==language&&!translationRequest(message))reply='';","let reply=act.isAction?actionReply(language,act.cc,act.ll):guardedReply(obj.reply,language,message);if(declared&&declared!==language&&!translationRequest(message)&&!replyMatchesLanguage(obj.reply,language,message))reply='';",1)

anchor='export default{async fetch(request,env,ctx){'
helper=r'''const FAST_DIRECT_LANGS=new Set(['ar','en','fr','es','de','tr','pt','it','vi','id','sw','ru','hi','zh','ja','ko','bn','fa','ur']);
function fastRouteReply(language){
 const r={
  ar:'أكيد. فهمت طلبك وعم بفتح لك القسم المناسب مباشرة.',
  en:'Got it. I understand your request and I’m opening the right section now.',
  fr:'Compris. J’ouvre directement la section adaptée à votre demande.',
  es:'Entendido. Voy a abrir directamente la sección adecuada para tu solicitud.',
  de:'Verstanden. Ich öffne jetzt direkt den passenden Bereich.',
  tr:'Anladım. Uygun bölümü şimdi doğrudan açıyorum.',
  pt:'Entendi. Vou abrir diretamente a seção certa para o seu pedido.',
  it:'Capito. Apro subito la sezione giusta per la tua richiesta.',
  vi:'Đã hiểu. Tôi đang mở ngay mục phù hợp với yêu cầu của bạn.',
  id:'Mengerti. Saya langsung membuka bagian yang tepat untuk permintaan Anda.',
  sw:'Nimekuelewa. Ninafungua moja kwa moja sehemu inayofaa kwa ombi lako.',
  ru:'Понял. Я сразу открываю подходящий раздел для вашего запроса.',
  hi:'समझ गया। मैं आपके अनुरोध के लिए सही सेक्शन सीधे खोल रहा हूँ।',
  zh:'明白了。我现在直接打开适合你请求的栏目。',
  ja:'わかりました。ご希望に合うセクションをすぐに開きます。',
  ko:'알겠습니다. 요청에 맞는 섹션을 바로 열겠습니다.',
  bn:'বুঝেছি। আপনার অনুরোধের জন্য সঠিক বিভাগটি এখনই খুলছি।',
  fa:'متوجه شدم. بخش مناسب درخواست شما را مستقیم باز می‌کنم.',
  ur:'سمجھ گیا۔ میں آپ کی درخواست کے لیے مناسب سیکشن فوراً کھول رہا ہوں۔'
 };
 return r[language]||''
}
function fastActionResult(message,body){
 const language=messageLanguage(message,body?.language),act=actionState(message,'','',body?.clientControls);
 if(act.isAction){
  return{ok:true,response:actionReply(language,act.cc,act.ll),language,category:'general',route:null,countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model:'seekvera-r120-direct-control',fastPath:'r120-direct-control',liveData:false}
 }
 const cat=directCategoryIntent(message,'general');
 if(cat!=='general'&&FAST_DIRECT_LANGS.has(language)){
  const response=fastRouteReply(language)||usefulFallback(message,language,cat);
  return{ok:true,response,language,category:cat,route:ROUTES[cat]||ROUTES.marketplace,countryAction:null,languageAction:null,model:'seekvera-r120-direct-intent',fastPath:'r120-direct-intent',liveData:false}
 }
 return null
}

'''
if 'function fastActionResult(' not in s:
    if anchor not in s:raise SystemExit('R120 export anchor missing')
    s=s.replace(anchor,helper+anchor,1)

needle="const reason=blocked(message);if(reason){const language=messageLanguage(message,body?.language);return json(request,{ok:true,blocked:true,reviewRequired:true,response:safetyReply(language),language,reason,category:'general',route:null,countryAction:null,languageAction:null,model:'seekvera-r105-safety'},200)}\n   if(env.AI){const d=await runStructured(env,body);if(d)return json(request,d,200)}"
replacement="const reason=blocked(message);if(reason){const language=messageLanguage(message,body?.language);return json(request,{ok:true,blocked:true,reviewRequired:true,response:safetyReply(language),language,reason,category:'general',route:null,countryAction:null,languageAction:null,model:'seekvera-r105-safety'},200)}\n   const quick=fastActionResult(message,body);if(quick)return json(request,quick,200);\n   if(env.AI){const d=await runStructured(env,body);if(d)return json(request,d,200)}"
if needle in s:s=s.replace(needle,replacement,1)
elif 'const quick=fastActionResult(message,body)' not in s:raise SystemExit('R120 API quick path anchor missing')

# Health marker
if 'r120:true' not in s:
    s=s.replace("r119b:true,r119bRuntime:'language-independent-voice-direct-intent-atomic-controls'", "r120:true,r120Runtime:'instant-controls-direct-intent-language-independent-voice',r119b:true,r119bRuntime:'language-independent-voice-direct-intent-atomic-controls'",1)
p.write_text(s,encoding='utf-8')
print('R120 worker patched')

# --- Frontend: faster routing while preserving voice on destination ---
p=Path('r31-ui-polish.js')
r=p.read_text(encoding='utf-8')
r=re.sub(r'const VERSION = "[^"]+";', 'const VERSION = "20260929-r120-fast-multilingual-actions";', r, count=1)
r=r.replace('setTimeout(go, 650);','setTimeout(go, 180);',1)
old="window.addEventListener(\n      \"seekvera:tts-start\",\n      () => {\n        started = true;\n      },\n      { once: true },\n    );"
new="window.addEventListener(\n      \"seekvera:tts-start\",\n      () => {\n        started = true;\n        setTimeout(move, 320);\n      },\n      { once: true },\n    );"
if old in r:r=r.replace(old,new,1)
elif 'setTimeout(move, 320);' not in r:raise SystemExit('R120 voice route anchor missing')
r=r.replace('}, 1800);','}, 950);',1)
r=r.replace('setTimeout(move, 9000);','setTimeout(move, 3500);',1)
p.write_text(r,encoding='utf-8')
print('R120 frontend patched')

# Voice mode/cache identity
p=Path('voice-ai.js');v=p.read_text(encoding='utf-8');v=re.sub(r"window\.__seekveraVoiceMode='[^']+'","window.__seekveraVoiceMode='20260929-r120-language-independent-voice'",v,count=1);p.write_text(v,encoding='utf-8')
p=Path('worker-r31.js');w=p.read_text(encoding='utf-8');w=re.sub(r'r31-ui-polish\\.js\\?v=[A-Za-z0-9._-]+','r31-ui-polish.js?v=20260929-r120-fast-multilingual-actions',w);w=re.sub(r'r31-ui-polish\.js\?v=[A-Za-z0-9._-]+','r31-ui-polish.js?v=20260929-r120-fast-multilingual-actions',w);w=re.sub(r'voice-ai\\.js\\?v=[A-Za-z0-9._-]+','voice-ai.js?v=20260929-r120-language-independent-voice',w);w=re.sub(r'voice-ai\.js\?v=[A-Za-z0-9._-]+','voice-ai.js?v=20260929-r120-language-independent-voice',w);p.write_text(w,encoding='utf-8')
p=Path('sw.js');sw=p.read_text(encoding='utf-8');sw=re.sub(r"const CACHE='[^']+';","const CACHE='seekvera-r120-fast-multilingual-actions';",sw,count=1);p.write_text(sw,encoding='utf-8')
print('R120 cache patched')
