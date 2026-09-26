from pathlib import Path

# Add common colloquial country aliases while retaining Intl.DisplayNames for every profile/language.
p=Path('r24-ai-controller.js');s=p.read_text(encoding='utf-8')
anchor="const AR_COUNTRIES={"
if 'const COUNTRY_ALIASES=' not in s:
    # insert after the AR_COUNTRIES declaration line
    pos=s.find("\nconst norm=",s.find(anchor))
    if pos<0: raise SystemExit('R24 alias insertion point missing')
    aliases="\nconst COUNTRY_ALIASES={US:['america','usa','u.s.a','united states of america'],GB:['uk','u.k.','england','britain','great britain'],AE:['uae','u.a.e.','emirates'],KR:['south korea','korea'],KP:['north korea'],CZ:['czech republic'],CI:[\"cote d'ivoire\",'ivory coast'],CD:['dr congo','drc','congo kinshasa'],CG:['congo brazzaville']};"
    s=s[:pos]+aliases+s[pos:]
old="const m=new Map();for(const c of codes)add(m,c,c);for(const[c,names]of Object.entries(AR_COUNTRIES))for(const n of names)add(m,n,c);"
new="const m=new Map();for(const c of codes)add(m,c,c);for(const[c,names]of Object.entries(AR_COUNTRIES))for(const n of names)add(m,n,c);for(const[c,names]of Object.entries(COUNTRY_ALIASES))for(const n of names)add(m,n,c);"
if old in s:s=s.replace(old,new,1)
elif new not in s: raise SystemExit('R24 country name map anchor missing')
p.write_text(s,encoding='utf-8')

# Country/language actions should still produce a real AI response in the language the user is speaking.
p=Path('r31-ui-polish.js');s=p.read_text(encoding='utf-8')
anchor="function arabicText(q=''){return /[\\u0600-\\u06ff]/u.test(String(q||''))||lang()==='ar'}"
extra=anchor+"\nfunction conversationLang(q=''){const t=String(q||'');if(/[\\u0600-\\u06ff]/u.test(t))return'ar';if(/[\\u0900-\\u097f]/u.test(t))return'hi';if(/[\\u0980-\\u09ff]/u.test(t))return'bn';if(/[\\u4e00-\\u9fff]/u.test(t))return'zh';if(/[\\u3040-\\u30ff]/u.test(t))return'ja';if(/[\\uac00-\\ud7af]/u.test(t))return'ko';if(/[\\u0590-\\u05ff]/u.test(t))return'he';if(/[\\u0370-\\u03ff]/u.test(t))return'el';if(/[\\u0e00-\\u0e7f]/u.test(t))return'th';if(/[\\u1200-\\u137f]/u.test(t))return'am';if(/[\\u0400-\\u04ff]/u.test(t))return String(lang()||'ru').match(/^(uk|bg|sr|mk|be|ru)$/)?lang():'ru';return lang()||'en'}"
if 'function conversationLang(' not in s:
    if anchor not in s: raise SystemExit('conversationLang anchor missing')
    s=s.replace(anchor,extra,1)
old="const input=document.querySelector('#aiChatInput');if(input)input.value='';appendMsg('user',q);try{window.SEEKVERA_CHAT?.save?.()}catch{}const ctl=controlResult(q);if(ctl){const reply=controlReply(ctl,q);appendMsg('bot',reply);window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:reply,language:ctl.language||lang()}}));submitting=false;return}const pending=appendMsg('bot',thinkingText(),'thinking');"
new="const input=document.querySelector('#aiChatInput');if(input)input.value='';appendMsg('user',q);try{window.SEEKVERA_CHAT?.save?.()}catch{}const spokenLanguage=conversationLang(q),ctl=controlResult(q);if(ctl){const pending=appendMsg('bot',thinkingText(),'thinking');try{const h=history(),d=await fetchAI({message:q,country:countryName(),countryCode:country(),language:spokenLanguage,uiLanguage:lang(),scope:country()==='WW'?'worldwide':'country',fast:true,history:h,controlAction:ctl});const reply=String(d?.response||controlReply(ctl,q)).trim();if(pending){pending.textContent=reply;pending.classList.remove('thinking')}window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:reply,language:spokenLanguage}}))}catch(e){const reply=controlReply(ctl,q);if(pending){pending.textContent=reply;pending.classList.remove('thinking')}window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text:reply,language:spokenLanguage}}))}finally{try{window.SEEKVERA_CHAT?.save?.()}catch{}submitting=false}return}const pending=appendMsg('bot',thinkingText(),'thinking');"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('R31 control branch anchor missing')
p.write_text(s,encoding='utf-8')

# Tell the backend the control action already happened, so its reply confirms rather than re-instructs.
p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
old="const system=`You are SEEKVERA AI inside a worldwide marketplace app. Reply ONLY in ${language}. Market: ${market}. Be natural, practical and concise (normally under 120 words)."
new="const controlNote=b?.controlAction&&(b.controlAction.country||b.controlAction.language)?` The app control was already executed successfully: ${b.controlAction.country?'country='+b.controlAction.country:''} ${b.controlAction.language?'language='+b.controlAction.language:''}. Confirm that naturally and briefly; do not tell the user to do it manually.`:'';const system=`You are SEEKVERA AI inside a worldwide marketplace app. Reply ONLY in ${language}. Market: ${market}.${controlNote} Be natural, practical and concise (normally under 120 words)."
if old in s:s=s.replace(old,new,1)
elif 'const controlNote=' not in s:raise SystemExit('worker control-note anchor missing')
p.write_text(s,encoding='utf-8')
print('R61B conversational controls patched')
