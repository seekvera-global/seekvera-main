from pathlib import Path
import re

# Final AI-only hardening: keep locale R15 intact, fix AI country commands and mobile layout.
p = Path('navigation.js')
s = p.read_text(encoding='utf-8')
s = s.replace('/* SEEKVERA universal navigation + worldwide locale/voice hardening R12 */','/* SEEKVERA universal navigation + worldwide AI stability R16 */',1)

# Remove the legacy delayed locale repaint from the navigation layer. R15 is the locale owner.
s = s.replace("  try{window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(20)}catch{}\n","")

anchor = "function normalizeText(s){return String(s||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().replace(/[’'`´]/g,'').replace(/[^\\p{L}\\p{N}]+/gu,' ').trim()}"
if 'function hardenAIUI()' not in s:
    ai = r'''
function ensureAIStableStyles(){
  if(document.getElementById('svR16AIStableStyles'))return;
  const st=document.createElement('style');st.id='svR16AIStableStyles';st.textContent=`
#aiChat,.sv-unified-chat{max-width:100%!important;min-width:0!important;overflow:hidden!important;contain:layout style!important}
#aiChat *, .sv-unified-chat *{box-sizing:border-box}
#aiChat .sv-chat-head,.sv-unified-chat .sv-chat-head{display:grid!important;grid-template-columns:minmax(0,1fr) auto 48px!important;align-items:center!important;gap:8px!important;min-width:0!important}
#aiChat .sv-chat-head>div,.sv-unified-chat .sv-chat-head>div{min-width:0!important;overflow:hidden!important}
#aiChat .sv-chat-head b,.sv-unified-chat .sv-chat-head b{display:block!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}
#aiChat .sv-chat-head small,.sv-unified-chat .sv-chat-head small{display:block!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;max-width:100%!important}
#aiChat .sv-chat-head>span,.sv-unified-chat .sv-chat-head>span{white-space:nowrap!important;min-width:0!important}
#aiChatSpeaker,.sv-global-speaker{width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important;min-height:48px!important;padding:0!important;overflow:hidden!important;white-space:nowrap!important;font-size:0!important;line-height:1!important;display:inline-flex!important;align-items:center!important;justify-content:center!important}
#aiChatSpeaker::before,.sv-global-speaker::before{content:'🔊';font-size:22px!important;line-height:1!important}
#aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{height:220px!important;min-height:220px!important;max-height:220px!important;overflow-y:auto!important;overflow-x:hidden!important;scroll-behavior:auto!important;overscroll-behavior:contain!important}
#aiChat .ai-msg,.sv-unified-chat .ai-msg{max-width:min(92%,560px)!important;min-width:0!important;overflow-wrap:anywhere!important;word-break:normal!important;white-space:pre-wrap!important}
#aiChat .sv-chat-form,.sv-unified-chat .sv-chat-form{display:grid!important;grid-template-columns:44px minmax(0,1fr) 44px 44px 50px!important;gap:7px!important;align-items:center!important;min-width:0!important;width:100%!important}
#aiChat .sv-chat-form input,.sv-unified-chat .sv-chat-form input{min-width:0!important;width:100%!important;max-width:100%!important;direction:auto!important;text-align:start!important}
#aiChatAttach,#aiChatCamera,#aiChatMic,#aiChat .sv-chat-form .send,.sv-unified-chat .sv-chat-form .attach,.sv-unified-chat .sv-chat-form .camera,.sv-unified-chat .sv-chat-form .mic,.sv-unified-chat .sv-chat-form .send{width:44px!important;min-width:44px!important;max-width:44px!important;height:44px!important;min-height:44px!important;padding:0!important;overflow:hidden!important;white-space:nowrap!important;font-size:0!important;line-height:1!important;display:inline-flex!important;align-items:center!important;justify-content:center!important}
#aiChat .sv-chat-form .send,.sv-unified-chat .sv-chat-form .send{width:50px!important;min-width:50px!important;max-width:50px!important}
#aiChatAttach::before,.sv-unified-chat .sv-chat-form .attach::before{content:'📎';font-size:20px!important}
#aiChatCamera::before,.sv-unified-chat .sv-chat-form .camera::before{content:'📷';font-size:20px!important}
#aiChatMic::before,.sv-unified-chat .sv-chat-form .mic::before{content:'🎤';font-size:20px!important}
#aiChat .sv-chat-form .send::before,.sv-unified-chat .sv-chat-form .send::before{content:'➤';font-size:22px!important}
#aiActions,.sv-ai-actions{display:flex!important;position:static!important;clear:both!important;flex-wrap:wrap!important;gap:8px!important;align-items:center!important;min-width:0!important;max-width:100%!important;padding:8px 12px 12px!important;overflow:visible!important}
#aiActions>* ,.sv-ai-actions>*{max-width:100%!important;min-width:0!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important}
#aiChat,#aiChat *,.sv-unified-chat,.sv-unified-chat *{animation:none!important}
html.sv-r15-applying #aiChat,html.sv-r15-applying #aiChat *{transition:none!important}
@media(max-width:600px){
 #aiChat .sv-chat-head,.sv-unified-chat .sv-chat-head{grid-template-columns:minmax(0,1fr) auto 44px!important;padding:10px!important;gap:6px!important}
 #aiChatSpeaker,.sv-global-speaker{width:44px!important;min-width:44px!important;max-width:44px!important;height:44px!important;min-height:44px!important}
 #aiChat .sv-chat-messages,.sv-unified-chat .sv-chat-messages{height:230px!important;min-height:230px!important;max-height:230px!important;padding:10px!important}
 #aiChat .sv-chat-form,.sv-unified-chat .sv-chat-form{grid-template-columns:minmax(0,1fr) 42px 42px 48px!important;gap:6px!important;padding:8px!important}
 #aiChatAttach,.sv-unified-chat .sv-chat-form .attach{display:none!important}
 #aiChatCamera,#aiChatMic,.sv-unified-chat .sv-chat-form .camera,.sv-unified-chat .sv-chat-form .mic{width:42px!important;min-width:42px!important;max-width:42px!important;height:42px!important;min-height:42px!important}
 #aiChat .sv-chat-form .send,.sv-unified-chat .sv-chat-form .send{width:48px!important;min-width:48px!important;max-width:48px!important;height:42px!important;min-height:42px!important}
 #aiChat .sv-chat-head small,.sv-unified-chat .sv-chat-head small{font-size:9px!important}
 #aiChat .sv-chat-head>span,.sv-unified-chat .sv-chat-head>span{font-size:10px!important}
}
@media(max-width:370px){
 #aiChat .sv-chat-head,.sv-unified-chat .sv-chat-head{grid-template-columns:minmax(0,1fr) 42px!important}
 #aiChat .sv-chat-head>span,.sv-unified-chat .sv-chat-head>span{display:none!important}
}
`;
  document.head.appendChild(st);
}
function fixAIControlButtons(){
  const defs=[['aiChatAttach','📎'],['aiChatCamera','📷'],['aiChatMic','🎤']];
  for(const [id,emoji] of defs){const b=document.getElementById(id);if(!b)continue;b.setAttribute('data-no-i18n','1');b.setAttribute('data-no-translate','1');if((b.textContent||'').trim()!==emoji)b.textContent=emoji;}
  const sp=document.getElementById('aiChatSpeaker');if(sp){sp.setAttribute('data-no-i18n','1');sp.setAttribute('data-no-translate','1');if(!/[🔊🔈🔇]/u.test(sp.textContent||''))sp.textContent='🔊';}
  const send=document.querySelector('#aiChatForm .send,#aiChat .sv-chat-form .send');if(send){send.setAttribute('data-no-i18n','1');send.setAttribute('data-no-translate','1');if((send.textContent||'').trim()!=='➤')send.textContent='➤';}
  const brand=document.querySelector('#aiChat .sv-chat-head b');if(brand){brand.setAttribute('data-no-i18n','1');brand.setAttribute('data-no-translate','1');if(!/SEEKVERA\s+AI/i.test(brand.textContent||''))brand.textContent='✨ SEEKVERA AI';}
  const input=document.getElementById('aiChatInput');if(input){input.setAttribute('dir','auto');input.style.minWidth='0';}
}
function hardenAIUI(){
  ensureAIStableStyles();fixAIControlButtons();
  const chat=document.getElementById('aiChat');if(!chat||chat.dataset.r16Observed==='1')return;
  chat.dataset.r16Observed='1';
  const mo=new MutationObserver(ms=>{for(const m of ms){const t=m.target?.nodeType===1?m.target:m.target?.parentElement;if(t?.closest?.('#aiChatSpeaker,#aiChatAttach,#aiChatCamera,#aiChatMic,#aiChatForm .send,#aiChat .sv-chat-head b')){queueMicrotask(fixAIControlButtons);break}}});
  mo.observe(chat,{subtree:true,childList:true,characterData:true});
}
'''
    if anchor not in s:
        raise SystemExit('R16 AI insertion anchor not found')
    s = s.replace(anchor, ai + '\n' + anchor, 1)

# Make the navigation locale pass finish with a single AI layout normalization.
if 'translateStaticAI();\n  hardenAIUI();' not in s:
    s = s.replace('  translateStaticAI();\n}', '  translateStaticAI();\n  hardenAIUI();\n}', 1)

# Country command: resolve the country first, then accept direct natural commands such as
# "switch to Lebanon", "Lebanon", and speech-recognition variants like "Up Control, Lebanon".
pat = re.compile(r"function isCountryCommand\(text\)\{.*?\n\}\nfunction countryNames", re.S)
new_cmd = r'''function isCountryCommand(text,code=''){
  const raw=String(text||''),s=normalizeText(raw);
  let direct=false;
  if(code){
    const names=countryNames(code),hasTarget=names.some(n=>n.length>=2&&(s===n||(' '+s+' ').includes(' '+n+' ')));
    const latin=/\b(?:set|switch|change|choose|select|go|move|use|open|control|app|market|country|region|take|put)\b/.test(s);
    const native=/(?:حط|حطلي|اختار|اختر|غير|غيرلي|حول|حوللي|انتقل|اذهب|استخدم|غيّر|حوّل|बदल|चुन|जाओ|देश|ملک|بدل|منتخب|смени|сменить|выбери|установи|cambia|elige|selecciona|change|choisis|wechsle|wähle|mudar|trocar|seç|degistir|imposta|scegli)/u.test(raw);
    const short=s.split(/\s+/).filter(Boolean).length<=3;
    direct=hasTarget&&(latin||native||short);
  }
  return direct
    || /\b(?:set|switch|change|choose|select)\b.{0,35}\b(?:country|region)\b/.test(s)
    || /(?:حط|حطلي|اختار|اختر|غير|غيرلي|حول|حوللي).{0,30}(?:الدولة|دولة|البلد|بلد)/u.test(raw)
    || /\b(?:mets?|change|passe|choisis?)\b.{0,35}\b(?:pays|region)\b/.test(s)
    || /\b(?:cambia|cambiar|pon|elige|selecciona)\b.{0,35}\b(?:pais|region)\b/.test(s)
    || /\b(?:ander|wechsle|wahle|setze)\b.{0,35}\b(?:land|region)\b/.test(s)
    || /\b(?:mudar|muda|trocar|troca|escolher|escolha)\b.{0,35}\b(?:pais|regiao)\b/.test(s)
    || /\b(?:degistir|sec|seç)\b.{0,35}\b(?:ulke|ülke|bolge|bölge)\b/.test(s)
    || /(?:смени|сменить|выбери|выбрать|установи).{0,35}(?:стран|регион)/u.test(raw)
    || /\b(?:cambia|imposta|scegli)\b.{0,35}\b(?:paese|regione)\b/.test(s)
    || /(?:ملک|ملک کو|ملک بدل).{0,30}(?:بدل|منتخب|چن)/u.test(raw)
    || hasCountryTerm(text);
}
function countryNames'''
s2, n = pat.subn(new_cmd, s, count=1)
if n != 1 and "function isCountryCommand(text,code='')" not in s:
    raise SystemExit('R16 country command function patch failed')
s = s2

old = "    if(!text||!isCountryCommand(text))return;\n    const code=resolveCountry(text);if(!code)return;"
new = "    if(!text)return;\n    const code=resolveCountry(text);if(!code||!isCountryCommand(text,code))return;"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('R16 AI submit condition anchor missing')

s = s.replace("m.dataset.noTranslate='1';m.textContent='🌍 '+name+' ✓';","m.dataset.noTranslate='1';m.dataset.noI18n='1';m.textContent='🌍 '+name+' ✓';",1)
s = s.replace("function init(){stripDuplicateDepartments();buildNav();bindLocaleControls();bindAICountryControl();scheduleLocalePass()}","function init(){stripDuplicateDepartments();buildNav();hardenAIUI();bindLocaleControls();bindAICountryControl();scheduleLocalePass()}",1)
p.write_text(s,encoding='utf-8')

# Cache bust the navigation runtime everywhere, and protect icon-only controls before translation runs.
for hp in Path('.').glob('*.html'):
    if hp.name.lower().startswith('google'):
        continue
    t=hp.read_text(encoding='utf-8')
    t=re.sub(r'navigation\.js\?v=[^"\']+','navigation.js?v=20260924-r16',t)
    t=re.sub(r"sw\.js\?v=[^'\"]+","sw.js?v=20260924-r16",t)
    if hp.name=='index.html':
        for id_ in ['aiChatSpeaker','aiChatAttach','aiChatCamera','aiChatMic']:
            t=t.replace(f'id="{id_}"',f'id="{id_}" data-no-i18n="1" data-no-translate="1"',1)
        t=t.replace('class="send" type="submit"','class="send" data-no-i18n="1" data-no-translate="1" type="submit"',1)
        t=t.replace('<b>✨ SEEKVERA AI</b>','<b data-no-i18n="1" data-no-translate="1">✨ SEEKVERA AI</b>',1)
        t=re.sub(r'Release 2026-09-24 · Worldwide R\d+','Release 2026-09-24 · Worldwide R16',t)
    hp.write_text(t,encoding='utf-8')

sp=Path('sw.js'); sw=sp.read_text(encoding='utf-8')
sw=re.sub(r"const CACHE='[^']+';","const CACHE='seekvera-r16-ai-stable-20260924';",sw,count=1)
sp.write_text(sw,encoding='utf-8')

print('R16 AI FINAL PATCH APPLIED')