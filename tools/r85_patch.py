from pathlib import Path
import re

VER='20260927-r85-visible-i18n-chat-guard'

# superapp.js: guard language/voice meta-conversation on the client.
p=Path('superapp.js')
s=p.read_text(encoding='utf-8')
s=s.replace('const RELEASE = "20260927-r83-unified-multilingual-voice-ai";', f'const RELEASE = "{VER}";', 1)
anchor='  let routeTimer = 0;\n'
helper=r'''  function metaConversationClient(q = "") {
    const t = String(q || "").toLowerCase();
    return /(?:\b(?:i am|i'm|im|you are|you're|are you|can you|do you)\b.{0,50}\b(?:speaking|speak|understand|hear|listening|language|voice|arabic|english|french|turkish|spanish|german)\b)|(?:(?:أنا|انا|إنت|انت|عم|صرت|صار|هلأ|هلق|هون|هنا).{0,50}(?:بحكي|بتحكي|احكي|تفهم|بتفهم|سامع|تسمع|صوت|لغة|عربي|العربي|إنجليزي|انجليزي|فرنسي|تركي))|(?:parle|parles|comprends|écoute|langue).{0,35}|(?:sprich|versteh|sprache).{0,35}|(?:habla|hablas|entiend|idioma).{0,35}|(?:konuş|anlıyor|anliyor|dil).{0,35}|(?:говор|понима|язык).{0,35}|(?:说|听懂|语言)|(?:話|言語)|(?:말|이해|언어)/iu.test(t);
  }
  function routeLikeReplyClient(text = "") {
    return /(?:take|send|move|route|redirect).{0,40}(?:section|department)|(?:section|department).{0,40}(?:now|direct)|(?:قسم|القسم).{0,40}(?:مباشر|الأنسب|المناسب|وديك|أوصلك|انقلك|أنقلك)/iu.test(String(text || ""));
  }
  function safeMetaReply(q = "") {
    const t=String(q||"");
    if(/[\u0600-\u06ff]/u.test(t)) return "إيه، فهمتك. كفّي احكي معي طبيعي بالعربي أو بأي لغة، وما رح حوّلك على أي قسم إلا لما تطلب شي محدد.";
    if(/[\u4e00-\u9fff]/u.test(t)) return "可以，我听得懂。你可以自然地继续说；只有当你提出明确需求时，我才会带你去相应栏目。";
    if(/[\u3040-\u30ff]/u.test(t)) return "はい、理解できます。自然に話し続けてください。具体的な依頼があるまでは会話を続けます。";
    if(/[\uac00-\ud7af]/u.test(t)) return "네, 이해해요. 자연스럽게 계속 말씀하세요. 구체적인 요청이 있을 때만 해당 섹션으로 안내할게요.";
    if(/[\u0900-\u097f]/u.test(t)) return "हाँ, मैं समझता हूँ। स्वाभाविक रूप से बोलते रहें; किसी खास अनुरोध पर ही मैं संबंधित सेक्शन में ले जाऊँगा।";
    if(/[\u0400-\u052f]/u.test(t)) return "Да, я вас понимаю. Продолжайте говорить естественно; к разделу я перейду только по конкретному запросу.";
    if(/\b(?:bonjour|français|francais|parle|comprends|langue)\b/i.test(t)) return "Oui, je vous comprends. Continuez naturellement ; je ne vous enverrai vers une section que lorsque vous demanderez quelque chose de précis.";
    if(/\b(?:hola|español|espanol|habla|entiendo|idioma)\b/i.test(t)) return "Sí, te entiendo. Sigue hablando con naturalidad; solo te llevaré a una sección cuando pidas algo concreto.";
    if(/\b(?:merhaba|türkçe|turkce|konuş|anlıyor|anliyor)\b/i.test(t)) return "Evet, seni anlıyorum. Doğal konuşmaya devam et; yalnızca belirli bir şey istediğinde ilgili bölüme götüreceğim.";
    if(/\b(?:hallo|deutsch|sprich|versteh|sprache)\b/i.test(t)) return "Ja, ich verstehe dich. Sprich einfach natürlich weiter; erst bei einer konkreten Anfrage gehe ich mit dir in den passenden Bereich.";
    return "Yes, I understand you. Keep talking naturally in any language; I’ll only take you to a section when you ask for something specific.";
  }
'''
if 'function metaConversationClient' not in s:
    if anchor not in s:
        raise SystemExit('superapp routeTimer anchor missing')
    s=s.replace(anchor, anchor+helper, 1)
old='      const finalCat = d.category ? d.category : localCat;'
new='''      const metaChat = metaConversationClient(q),
        finalCat = metaChat ? "general" : (d.category ? d.category : localCat);
      if (metaChat && routeLikeReplyClient(reply)) reply = safeMetaReply(q);'''
if old in s:
    s=s.replace(old,new,1)
elif 'finalCat = metaChat ? "general"' not in s:
    raise SystemExit('superapp finalCat anchor missing')
p.write_text(s,encoding='utf-8')

# index.html: load the visible i18n synchronizer and bust client caches.
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('data-release="20260927-r82-reply-before-navigation"', f'data-release="{VER}"', 1)
s=s.replace('superapp.js?v=20260927-r83-unified-multilingual-voice-ai', f'superapp.js?v={VER}', 1)
s=s.replace('sw.js?v=20260927-r83-unified-multilingual-voice-ai', f'sw.js?v={VER}', 1)
script=f'    <script src="r85-visible-i18n.js?v={VER}" defer></script>\n'
mark='    <script src="locale-r14-categories.js?v=20260924-r14" defer></script>\n'
if 'r85-visible-i18n.js' not in s:
    if mark not in s:
        raise SystemExit('index i18n insertion anchor missing')
    s=s.replace(mark, script+mark, 1)
p.write_text(s,encoding='utf-8')

# sw.js: force old static caches to be replaced.
p=Path('sw.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"const RELEASE='[^']+';", f"const RELEASE='{VER}';", s, count=1)
p.write_text(s,encoding='utf-8')
