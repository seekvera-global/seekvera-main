from pathlib import Path
import re

VER='20260929-r118-universal-language-resolution'
p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",s,count=1)

# Portuguese greeting with accented final letter must not miss JS ASCII word-boundary rules.
old="if(/[ãõ]/iu.test(t)||/\\b(olá|ola|preciso|procuro|obrigado|obrigada|aeroporto|perto)\\b/iu.test(s))return'pt';"
new="if(s.includes('olá')||/[ãõ]/iu.test(t)||/\\b(ola|preciso|procuro|obrigado|obrigada|aeroporto|perto)\\b/iu.test(s))return'pt';"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R118 Portuguese detector anchor missing')

# Strong English cues must override a bad model language label on ordinary English text.
needle="if(/\\b(selamat|terima kasih|saya|ingin|cari|butuh|bandara|dekat)\\b/iu.test(s))return pick(['id','ms'],'id');\n return q||'en';"
replace="if(/\\b(selamat|terima kasih|saya|ingin|cari|butuh|bandara|dekat)\\b/iu.test(s))return pick(['id','ms'],'id');\n if(/\\b(hello|hi|hey|how are you|i need|i want|i am looking|i'm looking|can you help|please help|thank you|thanks|what kind|which city|near the airport)\\b/iu.test(s))return'en';\n return q||'en';"
if needle in s:s=s.replace(needle,replace,1)
elif 'near the airport' not in s:raise SystemExit('R118 English detector anchor missing')

# For ambiguous Latin-script languages, let the model's declared language act as a hint.
# Strong scripts and strong lexical cues still override it, so Arabic can never become Icelandic.
old="language=targetLanguage,declared=languageCode(obj.languageCode),meta=metaConversation(message)"
new="language=messageLanguage(message,obj.languageCode||targetLanguage),declared=languageCode(obj.languageCode),meta=metaConversation(message)"
count=s.count(old)
if count<2:raise SystemExit(f'R118 model language anchors missing: {count}')
s=s.replace(old,new,2)

# The language contract compares the model declaration only after resolving the actual message language.
# Add explicit runtime marker for production verification.
s=s.replace("r117:true,r117Runtime:'strict-reply-language-contract-and-history-sanitizer',",
            "r118:true,r118Runtime:'script-first-plus-model-hint-language-resolution',r117:true,r117Runtime:'strict-reply-language-contract-and-history-sanitizer',",1)

p.write_text(s,encoding='utf-8')
print('R118 universal language resolution applied')
