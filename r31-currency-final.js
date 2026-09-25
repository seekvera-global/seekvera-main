(()=>{'use strict';
if(window.__SEEKVERA_R31_CURRENCY_FINAL)return;window.__SEEKVERA_R31_CURRENCY_FINAL=true;
const EXTRA={SLE:{en:'Sierra Leonean Leone',ar:'ليون سيراليوني',fr:'leone sierra-léonais'},ZWG:{en:'Zimbabwe Gold',ar:'ذهب زيمبابوي',fr:'or du Zimbabwe'}};
function lang(){return String(document.querySelector('#lang')?.value||document.documentElement.lang||'en').toLowerCase().split(/[-_]/)[0]||'en'}
function viaNumberFormat(code,l){try{const p=new Intl.NumberFormat(l,{style:'currency',currency:code,currencyDisplay:'name',maximumFractionDigits:0}).formatToParts(1);const x=p.find(v=>v.type==='currency')?.value?.trim();if(x&&x.toUpperCase()!==code)return x}catch{}return''}
function patch(){const r=window.SEEKVERA_R31;if(!r?.currencyLabel){setTimeout(patch,40);return}if(r.__currencyFinal)return;r.__currencyFinal=true;const original=r.currencyLabel.bind(r);r.currencyLabel=(code,l=lang())=>{code=String(code||'').toUpperCase();const a=original(code,l);if(a&&a.toUpperCase()!==code)return a;const b=viaNumberFormat(code,l);if(b)return b;return EXTRA[code]?.[l]||EXTRA[code]?.en||code};
 const relabel=()=>{const e=document.querySelector('#currency');if(!e)return;for(const o of e.options){const code=String(o.value||'').toUpperCase();if(!/^[A-Z]{3}$/.test(code))continue;const x=r.currencyLabel(code,lang());if(x&&o.textContent!==x)o.textContent=x}};relabel();document.addEventListener('change',e=>{if(e.target?.id==='country'||e.target?.id==='lang'||e.target?.id==='currency')setTimeout(relabel,0)},true);setTimeout(relabel,250);setTimeout(relabel,800)}
patch();
})();