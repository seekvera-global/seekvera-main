from pathlib import Path

p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=s.replace("const RELEASE='20260927-r83-unified-multilingual-voice-ai';","const RELEASE='20260927-r84-natural-chat-guard';",1)

anchor='function employmentIntent(message)'
helper=r'''function metaConversation(message){
 const s=String(message||'').toLowerCase();
 return /(?:\b(?:i am|i'm|im|you are|you're|are you|can you|do you)\b.{0,45}\b(?:speaking|speak|understand|hear|listening|language|voice|arabic|english|french|turkish|spanish|german)\b)|(?:(?:أنا|انا|إنت|انت|عم|صرت|صار|هلأ|هلق|هون|هنا).{0,45}(?:بحكي|بتحكي|احكي|تفهم|بتفهم|سامع|تسمع|صوت|لغة|عربي|العربي|إنجليزي|انجليزي|فرنسي|تركي))|(?:parle|parles|comprends|écoute|langue).{0,30}(?:français|arabe|anglais|langue)?|(?:sprich|versteh|sprache).{0,30}|(?:habla|hablas|entiend|idioma).{0,30}|(?:konuş|anlıyor|anliyor|dil).{0,30}|(?:говор|понима|язык).{0,30}|(?:说|听懂|语言)|(?:話|言語)|(?:말|이해|언어)/iu.test(s)
}
function metaReply(message,language){
 const l=languageCode(language)||messageLanguage(message,'');
 const r={
  ar:'إيه، فهمتك. فيك تحكي معي بالعربي أو بأي لغة بشكل طبيعي، وما رح حوّلك على أي قسم إلا لما تطلب شي محدد.',
  en:'Yes, I understand you. Speak naturally in any language; I’ll stay in the conversation until you ask for something specific.',
  fr:'Oui, je vous comprends. Parlez naturellement dans n’importe quelle langue ; je resterai dans la conversation jusqu’à ce que vous demandiez quelque chose de précis.',
  es:'Sí, te entiendo. Habla con naturalidad en cualquier idioma; seguiré conversando hasta que pidas algo concreto.',
  de:'Ja, ich verstehe dich. Sprich ganz natürlich in jeder Sprache; ich bleibe im Gespräch, bis du etwas Bestimmtes möchtest.',
  tr:'Evet, seni anlıyorum. İstediğin dilde doğal konuş; belirli bir şey isteyene kadar sohbet içinde kalacağım.',
  ru:'Да, я вас понимаю. Говорите естественно на любом языке; я останусь в разговоре, пока вы не попросите что-то конкретное.',
  zh:'可以，我听得懂。你可以自然地用任何语言和我说话；只有当你提出明确需求时，我才会带你去相应栏目。',
  ja:'はい、理解できます。どの言語でも自然に話してください。具体的な依頼があるまでは会話を続けます。',
  ko:'네, 이해해요. 어떤 언어로든 자연스럽게 말씀하세요. 구체적인 요청을 하기 전까지는 대화를 계속할게요.',
  hi:'हाँ, मैं समझता हूँ। आप किसी भी भाषा में स्वाभाविक रूप से बोलें; जब तक आप कोई खास चीज़ नहीं माँगते, मैं बातचीत में ही रहूँगा।',
  pt:'Sim, eu entendo. Fale naturalmente em qualquer idioma; continuarei na conversa até você pedir algo específico.',
  it:'Sì, ti capisco. Parla naturalmente in qualsiasi lingua; resterò nella conversazione finché non chiederai qualcosa di specifico.'
 };
 return r[l]||r.en
}
function routeLikeReply(text){return /(?:take|send|move|route|redirect).{0,35}(?:section|department)|(?:section|department).{0,35}(?:now|direct)|(?:قسم|القسم).{0,35}(?:مباشر|الأنسب|المناسب|وديك|أوصلك|انقلك|أنقلك)/iu.test(String(text||''))}
'''
if 'function metaConversation(message)' not in s:
    i=s.find(anchor)
    if i<0: raise SystemExit('employmentIntent anchor missing')
    s=s[:i]+helper+s[i:]

old="const act=actionState(message,d?.countryAction?.code,d?.languageAction?.code,body?.clientControls),language=act.isAction?messageLanguage(message,d.language):normalizedLanguage(d.language,message),chat=conversationOnly(message),cat=chat?'general':(category(d.category)==='jobs'&&!employmentIntent(message)?'general':category(d.category)),response=act.isAction?actionReply(language,act.cc,act.ll):chat?conversationalFallback(message,language):clean(d.response,5000);"
new="const act=actionState(message,d?.countryAction?.code,d?.languageAction?.code,body?.clientControls),language=act.isAction?messageLanguage(message,d.language):normalizedLanguage(d.language,message),meta=metaConversation(message),chat=conversationOnly(message)||meta,cat=chat?'general':(category(d.category)==='jobs'&&!employmentIntent(message)?'general':category(d.category)),response=act.isAction?actionReply(language,act.cc,act.ll):meta?metaReply(message,language):chat?conversationalFallback(message,language):clean(d.response,5000);"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('degraded fallback anchor missing')

old="const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=act.isAction?messageLanguage(message,obj.languageCode):(languageCode(obj.languageCode)||normalizedLanguage('',message)),cat=conversationOnly(message)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));\n   return{ok:true,response:act.isAction?actionReply(language,act.cc,act.ll):clean(obj.reply,5000),language,category:cat,route:ROUTES[cat]||ROUTES.general,countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model,fastPath:act.isAction?'r76-verified-action-first':'r76-single-structured-ai',liveData:false}"
new="const act=actionState(message,obj.countryAction,obj.languageAction,body?.clientControls),language=act.isAction?messageLanguage(message,obj.languageCode):(languageCode(obj.languageCode)||normalizedLanguage('',message)),meta=metaConversation(message),cat=(conversationOnly(message)||meta)?'general':(category(obj.category)==='jobs'&&!employmentIntent(message)?'general':category(obj.category));\n   let reply=act.isAction?actionReply(language,act.cc,act.ll):clean(obj.reply,5000);if(meta&&(routeLikeReply(reply)||category(obj.category)!=='general'))reply=metaReply(message,language);\n   return{ok:true,response:reply,language,category:cat,route:ROUTES[cat]||ROUTES.general,countryAction:act.cc?{type:'set-country',code:act.cc}:null,languageAction:act.ll?{type:'set-language',code:act.ll}:null,model,fastPath:act.isAction?'r76-verified-action-first':meta?'r84-meta-conversation-guard':'r76-single-structured-ai',liveData:false}"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('structured response anchor missing')

prompt_anchor='- countryAction: the ISO-3166 alpha-2 code for ANY country in the world, or WW,'
if 'Language/voice meta-conversation rule:' not in s:
    i=s.find(prompt_anchor)
    if i<0: raise SystemExit('prompt anchor missing')
    extra="- Language/voice meta-conversation rule: if the user says they are speaking a language, asks whether you understand/hear them, comments on which language you are speaking, or simply tests conversation (for example: ‘صرت بتحكي عربي هون’, ‘I am speaking Arabic now’, ‘Can you understand French?’), category MUST be general. Reply naturally to what they said. Never say you will send them to a section unless they actually ask for a marketplace task.\\\n"
    s=s[:i]+extra+s[i:]

p.write_text(s,encoding='utf-8')
print('R84_PATCH_OK')
