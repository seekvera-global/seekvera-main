from pathlib import Path
import re

OLD='20260926-r65c-first-voice-auto'
VER='20260926-r66-final-ai-command-language'

controller=r'''(()=>{
'use strict';
if(window.__SEEKVERA_R66_FINAL)return;window.__SEEKVERA_R66_FINAL=true;
const VER='20260926-r66-final-ai-command-language';
const $=s=>document.querySelector(s);
const norm=s=>String(s||'').normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f\u0670]/g,'').replace(/[إأآ]/g,'ا').replace(/ى/g,'ي').replace(/ة/g,'ه').toLowerCase().replace(/[\s\-_]+/g,' ').trim();
function messageLang(t){t=String(t||'');if(/[\u0600-\u06ff]/u.test(t))return'ar';if(/[\u0900-\u097f]/u.test(t))return'hi';if(/[\u4e00-\u9fff]/u.test(t))return'zh';if(/[\u3040-\u30ff]/u.test(t))return'ja';if(/[\uac00-\ud7af]/u.test(t))return'ko';if(/[\u0400-\u04ff]/u.test(t))return'ru';if(/[\u0590-\u05ff]/u.test(t))return'he';if(/[\u0370-\u03ff]/u.test(t))return'el';const n=' '+norm(t)+' ';if(/\b(bonjour|salut|je|vous|merci|comment|besoin|aide|cherche|travail|emploi)\b/.test(n))return'fr';if(/\b(hola|gracias|quiero|busco|trabajo|ayuda|como|puedes)\b/.test(n))return'es';if(/\b(ola|obrigado|quero|procuro|trabalho|ajuda|voce)\b/.test(n))return'pt';if(/\b(hallo|danke|ich|suche|arbeit|hilfe|wie)\b/.test(n))return'de';if(/\b(ciao|grazie|cerco|lavoro|aiuto|come)\b/.test(n))return'it';if(/\b(merhaba|tesekkur|teşekkür|yardim|yardım|arıyorum|istiyorum)\b/.test(n))return'tr';return'en'}
function rememberVoiceFromText(t){const l=messageLang(t);try{if(l&&l!=='en')localStorage.setItem('seekvera_chat_voice_lang',l)}catch{}}
function detect(q){let c={};try{c=window.SEEKVERA_R24_CONTROLLER?.detectControls?.(q)||{}}catch{}const n=norm(q);if(!c.country&&/(worldwide|world wide|global|all countries|all markets|العالم|عالمي|العالمي|كل الدول|جميع الدول|حول العالم)/u.test(n)&&/(change|switch|set|make|use|app|country|market|حول|حوّل|غير|غيّر|حط|خلي|وديني|انقلني|نقلني|take me|move me)/u.test(n))c.country='WW';return c}
function ensureOption(sel,value,label){if(!sel)return;if(![...sel.options].some(o=>o.value===value))sel.add(new Option(label||value,value),0)}
function setScope(scope){document.querySelectorAll('[data-scope]').forEach(b=>b.classList.toggle('active',b.dataset.scope===scope));try{localStorage.setItem('seekvera_scope',scope)}catch{}}
function dispatch(el){try{el?.dispatchEvent(new Event('change',{bubbles:true}))}catch{}}
function apply(c){const api=window.SEEKVERA_LOCALE_R15||null;let changed=false;const cc=String(c?.country||'').toUpperCase(),ll=String(c?.language||'').toLowerCase();if(cc){try{sessionStorage.removeItem('seekvera_ai_intent')}catch{}try{localStorage.setItem('seekvera_country',cc);localStorage.setItem('seekvera_country_explicit','1')}catch{}const ce=$('#country');if(api?.setCountry){try{api.setCountry(cc);changed=true}catch{}}else if(ce){ensureOption(ce,cc,cc==='WW'?'Worldwide':cc);ce.value=cc;dispatch(ce);changed=true}if(cc==='WW')setScope('worldwide');else setScope('country')}
if(ll){try{localStorage.setItem('seekvera_lang',ll);localStorage.setItem('seekvera_language_explicit','1');localStorage.setItem('seekvera_chat_voice_lang',ll)}catch{}if(api?.setLanguage){try{api.setLanguage(ll);changed=true}catch{}}else{const le=$('#lang');if(le){ensureOption(le,ll,ll.toUpperCase());le.value=ll;dispatch(le);changed=true}}}if(changed){try{window.SEEKVERA_I18N?.apply?.()}catch{}try{window.SEEKVERA_R14_CATEGORIES?.apply?.()}catch{}window.dispatchEvent(new CustomEvent('seekvera:ai-control',{detail:{country:cc,language:ll,version:VER}}))}return changed}
function addMsg(role,text){const box=$('#aiMessages');if(!box)return;const d=document.createElement('div');d.className='ai-msg '+(role==='user'?'user':'bot');d.textContent=text;box.appendChild(d);box.scrollTop=box.scrollHeight}
function displayCountry(code){if(code==='WW')return'Worldwide';const e=$('#country');const o=e&&[...e.options].find(x=>x.value===code);return (o?.textContent||code).trim()}
function reply(c,q){const l=messageLang(q),target=c.country?displayCountry(String(c.country).toUpperCase()):String(c.language||'').toUpperCase();if(l==='ar')return c.country==='WW'?'تم. حوّلت التطبيق إلى Worldwide.':`تم. حوّلت التطبيق إلى ${target}.`;if(l==='fr')return c.country==='WW'?"C’est fait. L’application est maintenant en mode Worldwide.":`C’est fait. J’ai changé l’application vers ${target}.`;if(l==='es')return c.country==='WW'?'Listo. La aplicación está ahora en Worldwide.':`Listo. Cambié la aplicación a ${target}.`;if(l==='tr')return c.country==='WW'?'Tamam. Uygulamayı Worldwide moduna aldım.':`Tamam. Uygulamayı ${target} olarak değiştirdim.`;return c.country==='WW'?'Done. The app is now set to Worldwide.':`Done. I changed the app to ${target}.`}
function handleControl(){const input=$('#aiChatInput');const q=String(input?.value||'').trim();if(!q)return false;rememberVoiceFromText(q);const c=detect(q);if(!c.country&&!c.language)return false;apply(c);addMsg('user',q);const text=reply(c,q);addMsg('bot',text);if(input)input.value='';try{window.dispatchEvent(new CustomEvent('seekvera:ai-response',{detail:{text,language:messageLang(q),control:true}}))}catch{}return true}
document.addEventListener('submit',e=>{const f=e.target;if(!(f instanceof HTMLFormElement)||f.id!=='aiChatForm')return;const input=$('#aiChatInput');rememberVoiceFromText(input?.value||'');if(handleControl()){e.preventDefault();e.stopImmediatePropagation()}},true);
window.SEEKVERA_R66_FINAL={version:VER,detect,apply,messageLang};
})();
'''
Path('r66-final-controller.js').write_text(controller,encoding='utf-8')

p=Path('worker-r31.js');s=p.read_text(encoding='utf-8')
s=s.replace(OLD,VER)
s=s.replace("AbortSignal.timeout(1800)","AbortSignal.timeout(6000)")
for name in ('r31-ui-polish.js','r24-ai-controller.js','voice-ai.js','superapp.js','r60-runtime-guard.js','navigation.js'):
    s=s.replace(name+'?v='+OLD,name+'?v='+VER)
p.write_text(s,encoding='utf-8')

for name in ('voice-ai.js','r24-ai-controller.js','r31-ui-polish.js','superapp.js','r60-runtime-guard.js','navigation.js','sw.js'):
    p=Path(name);x=p.read_text(encoding='utf-8').replace(OLD,VER);p.write_text(x,encoding='utf-8')
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'):continue
    x=p.read_text(encoding='utf-8').replace(OLD,VER)
    if 'r66-final-controller.js' not in x:
        x=re.sub(r'</body>',f'<script src="/r66-final-controller.js?v={VER}" data-no-i18n="1"></script></body>',x,flags=re.I,count=1)
    p.write_text(x,encoding='utf-8')
print('R66 final AI command/language patch applied')
