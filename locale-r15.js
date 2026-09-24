/* SEEKVERA R15 atomic locale coordinator.
   One source of truth: country, language and currency always move together.
   Country selection -> that country's default language/currency.
   Language selection -> canonical country for that language + its currency.
   Currency selection -> canonical country for that currency + that country's language.
   Worldwide -> English + USD. */
(()=>{'use strict';
if(window.__SEEKVERA_LOCALE_R15)return;window.__SEEKVERA_LOCALE_R15=true;

const PROFILES=Object.fromEntries(`AF:fa,AFN;AL:sq,ALL;DZ:ar,DZD;AS:en,USD;AD:ca,EUR;AO:pt,AOA;AI:en,XCD;AQ:en,USD;AG:en,XCD;AR:es,ARS;AM:hy,AMD;AW:nl,AWG;AU:en,AUD;AT:de,EUR;AZ:az,AZN;BS:en,BSD;BH:ar,BHD;BD:bn,BDT;BB:en,BBD;BY:be,BYN;BE:nl,EUR;BZ:en,BZD;BJ:fr,XOF;BM:en,BMD;BT:dz,BTN;BO:es,BOB;BQ:nl,USD;BA:bs,BAM;BW:en,BWP;BV:no,NOK;BR:pt,BRL;IO:en,USD;BN:ms,BND;BG:bg,BGN;BF:fr,XOF;BI:fr,BIF;CV:pt,CVE;KH:km,KHR;CM:fr,XAF;CA:en,CAD;KY:en,KYD;CF:fr,XAF;TD:fr,XAF;CL:es,CLP;CN:zh,CNY;CX:en,AUD;CC:en,AUD;CO:es,COP;KM:fr,KMF;CD:fr,CDF;CG:fr,XAF;CK:en,NZD;CR:es,CRC;CI:fr,XOF;HR:hr,EUR;CU:es,CUP;CW:nl,ANG;CY:el,EUR;CZ:cs,CZK;DK:da,DKK;DJ:fr,DJF;DM:en,XCD;DO:es,DOP;EC:es,USD;EG:ar,EGP;SV:es,USD;GQ:es,XAF;ER:ti,ERN;EE:et,EUR;SZ:en,SZL;ET:am,ETB;FK:en,FKP;FO:fo,DKK;FJ:en,FJD;FI:fi,EUR;FR:fr,EUR;GF:fr,EUR;PF:fr,XPF;TF:fr,EUR;GA:fr,XAF;GM:en,GMD;GE:ka,GEL;DE:de,EUR;GH:en,GHS;GI:en,GIP;GR:el,EUR;GL:kl,DKK;GD:en,XCD;GP:fr,EUR;GU:en,USD;GT:es,GTQ;GG:en,GBP;GN:fr,GNF;GW:pt,XOF;GY:en,GYD;HT:fr,HTG;HM:en,AUD;VA:it,EUR;HN:es,HNL;HK:zh,HKD;HU:hu,HUF;IS:is,ISK;IN:hi,INR;ID:id,IDR;IR:fa,IRR;IQ:ar,IQD;IE:en,EUR;IM:en,GBP;IL:he,ILS;IT:it,EUR;JM:en,JMD;JP:ja,JPY;JE:en,GBP;JO:ar,JOD;KZ:kk,KZT;KE:sw,KES;KI:en,AUD;KP:ko,KPW;KR:ko,KRW;KW:ar,KWD;KG:ky,KGS;LA:lo,LAK;LV:lv,EUR;LB:ar,LBP;LS:en,LSL;LR:en,LRD;LY:ar,LYD;LI:de,CHF;LT:lt,EUR;LU:fr,EUR;MO:zh,MOP;MG:mg,MGA;MW:en,MWK;MY:ms,MYR;MV:dv,MVR;ML:fr,XOF;MT:mt,EUR;MH:en,USD;MQ:fr,EUR;MR:ar,MRU;MU:en,MUR;YT:fr,EUR;MX:es,MXN;FM:en,USD;MD:ro,MDL;MC:fr,EUR;MN:mn,MNT;ME:sr,EUR;MS:en,XCD;MA:ar,MAD;MZ:pt,MZN;MM:my,MMK;NA:en,NAD;NR:en,AUD;NP:ne,NPR;NL:nl,EUR;NC:fr,XPF;NZ:en,NZD;NI:es,NIO;NE:fr,XOF;NG:en,NGN;NU:en,NZD;NF:en,AUD;MK:mk,MKD;MP:en,USD;NO:no,NOK;OM:ar,OMR;PK:ur,PKR;PW:en,USD;PS:ar,ILS;PA:es,PAB;PG:en,PGK;PY:es,PYG;PE:es,PEN;PH:fil,PHP;PN:en,NZD;PL:pl,PLN;PT:pt,EUR;PR:es,USD;QA:ar,QAR;RE:fr,EUR;RO:ro,RON;RU:ru,RUB;RW:rw,RWF;BL:fr,EUR;SH:en,SHP;KN:en,XCD;LC:en,XCD;MF:fr,EUR;PM:fr,EUR;VC:en,XCD;WS:sm,WST;SM:it,EUR;ST:pt,STN;SA:ar,SAR;SN:fr,XOF;RS:sr,RSD;SC:en,SCR;SL:en,SLE;SG:en,SGD;SX:nl,ANG;SK:sk,EUR;SI:sl,EUR;SB:en,SBD;SO:so,SOS;ZA:en,ZAR;GS:en,GBP;SS:en,SSP;ES:es,EUR;LK:si,LKR;SD:ar,SDG;SR:nl,SRD;SJ:no,NOK;SE:sv,SEK;CH:de,CHF;SY:ar,SYP;TW:zh,TWD;TJ:tg,TJS;TZ:sw,TZS;TH:th,THB;TL:pt,USD;TG:fr,XOF;TK:en,NZD;TO:to,TOP;TT:en,TTD;TN:ar,TND;TR:tr,TRY;TM:tk,TMT;TC:en,USD;TV:en,AUD;UG:en,UGX;UA:uk,UAH;AE:ar,AED;GB:en,GBP;UM:en,USD;US:en,USD;UY:es,UYU;UZ:uz,UZS;VU:fr,VUV;VE:es,VES;VN:vi,VND;VG:en,USD;VI:en,USD;WF:fr,XPF;EH:ar,MAD;YE:ar,YER;ZM:en,ZMW;ZW:en,ZWG`.split(';').map(x=>{const [cc,v]=x.split(':'),[language,currency]=v.split(',');return[cc,{language,currency}]}));
const LANG_PRIMARY={"en":"US","ar":"SA","fr":"FR","zh":"CN","es":"ES","hi":"IN","pt":"PT","de":"DE","ja":"JP","ko":"KR","id":"ID","tr":"TR","ru":"RU","ur":"PK","bn":"BD","vi":"VN","it":"IT","sw":"KE","th":"TH","fa":"IR","pl":"PL","nl":"NL","ms":"MY","fil":"PH","ha":"NG","yo":"NG","ig":"NG","am":"ET","he":"IL","el":"GR","uk":"UA","ro":"RO","cs":"CZ","sk":"SK","hu":"HU","sv":"SE","no":"NO","da":"DK","fi":"FI","bg":"BG","hr":"HR","sr":"RS","sl":"SI","lt":"LT","lv":"LV","et":"EE","ca":"ES","eu":"ES","gl":"ES","is":"IS","sq":"AL","mk":"MK","ka":"GE","hy":"AM","az":"AZ","kk":"KZ","uz":"UZ","ky":"KG","tg":"TJ","tk":"TM","ne":"NP","si":"LK","ta":"IN","te":"IN","ml":"IN","mr":"IN","gu":"IN","pa":"IN","km":"KH","lo":"LA","my":"MM","mn":"MN","zu":"ZA","af":"ZA","be":"BY","bs":"BA","dz":"BT","ti":"ER","fo":"FO","kl":"GL","rw":"RW","sm":"WS","to":"TO","so":"SO","ps":"AF","dv":"MV","mt":"MT","mg":"MG","ga":"IE","cy":"GB","mi":"NZ","fy":"NL","lb":"LU","rm":"CH","ku":"IQ","xh":"ZA","st":"LS","tn":"BW"};
const CURRENCY_PRIMARY={"AFN":"AF","ALL":"AL","DZD":"DZ","USD":"US","EUR":"DE","AOA":"AO","XCD":"AG","ARS":"AR","AMD":"AM","AWG":"AW","AUD":"AU","AZN":"AZ","BSD":"BS","BHD":"BH","BDT":"BD","BBD":"BB","BYN":"BY","BZD":"BZ","XOF":"SN","BMD":"BM","BTN":"BT","BOB":"BO","BAM":"BA","BWP":"BW","NOK":"NO","BRL":"BR","BND":"BN","BGN":"BG","BIF":"BI","CVE":"CV","KHR":"KH","XAF":"CM","CAD":"CA","KYD":"KY","CLP":"CL","CNY":"CN","COP":"CO","KMF":"KM","CDF":"CD","NZD":"NZ","CRC":"CR","CUP":"CU","ANG":"CW","CZK":"CZ","DKK":"DK","DJF":"DJ","DOP":"DO","EGP":"EG","ERN":"ER","SZL":"SZ","ETB":"ET","FKP":"FK","FJD":"FJ","XPF":"PF","GMD":"GM","GEL":"GE","GHS":"GH","GIP":"GI","GTQ":"GT","GBP":"GB","GNF":"GN","GYD":"GY","HTG":"HT","HNL":"HN","HKD":"HK","HUF":"HU","ISK":"IS","INR":"IN","IDR":"ID","IRR":"IR","IQD":"IQ","ILS":"IL","JMD":"JM","JPY":"JP","JOD":"JO","KZT":"KZ","KES":"KE","KPW":"KP","KRW":"KR","KWD":"KW","KGS":"KG","LAK":"LA","LBP":"LB","LSL":"LS","LRD":"LR","LYD":"LY","CHF":"CH","MOP":"MO","MGA":"MG","MWK":"MW","MYR":"MY","MVR":"MV","MRU":"MR","MUR":"MU","MXN":"MX","MDL":"MD","MNT":"MN","MAD":"MA","MZN":"MZ","MMK":"MM","NAD":"NA","NPR":"NP","NIO":"NI","NGN":"NG","MKD":"MK","OMR":"OM","PKR":"PK","PAB":"PA","PGK":"PG","PYG":"PY","PEN":"PE","PHP":"PH","PLN":"PL","QAR":"QA","RON":"RO","RUB":"RU","RWF":"RW","SHP":"SH","WST":"WS","STN":"ST","SAR":"SA","RSD":"RS","SCR":"SC","SLE":"SL","SGD":"SG","SBD":"SB","SOS":"SO","ZAR":"ZA","SSP":"SS","LKR":"LK","SDG":"SD","SRD":"SR","SEK":"SE","SYP":"SY","TWD":"TW","TJS":"TJ","TZS":"TZ","THB":"TH","TOP":"TO","TTD":"TT","TND":"TN","TRY":"TR","TMT":"TM","UGX":"UG","UAH":"UA","AED":"AE","UYU":"UY","UZS":"UZ","VUV":"VU","VES":"VE","VND":"VN","YER":"YE","ZMW":"ZM","ZWG":"ZW"};
const RTL=new Set(['ar','fa','ur','he','ps','dv']);
const $=s=>document.querySelector(s);
let syncing=false,lastSignature='',lastReason='boot',settleTimer=0;

function normalizeLang(v){
  v=String(v||'').toLowerCase().replace('_','-');
  if(v==='auto')v=String(navigator.language||'en').toLowerCase();
  return v.split('-')[0]||'en';
}
function primaryForLanguage(lang){return LANG_PRIMARY[normalizeLang(lang)]||'US'}
function primaryForCurrency(cur){cur=String(cur||'USD').toUpperCase();return CURRENCY_PRIMARY[cur]||'US'}
function ensureOption(el,value,label){
  if(!el||!value)return;
  let o=[...el.options].find(x=>x.value===value);
  if(!o){o=document.createElement('option');o.value=value;o.textContent=label||value;el.appendChild(o)}
}
function localeStateFrom(source,value){
  if(source==='country'){
    const cc=String(value||'WW').toUpperCase();
    if(cc==='WW')return {country:'WW',language:'en',currency:'USD',scope:'worldwide',source:'country'};
    const p=PROFILES[cc]||PROFILES.US;
    return {country:PROFILES[cc]?cc:'US',language:p.language,currency:p.currency,scope:'country',source:'country'};
  }
  if(source==='language'){
    const language=normalizeLang(value);
    const country=primaryForLanguage(language);
    const currency=(PROFILES[country]||PROFILES.US).currency;
    return {country,language,currency,scope:'country',source:'language'};
  }
  if(source==='currency'){
    const currency=String(value||'USD').toUpperCase();
    const country=primaryForCurrency(currency);
    const language=(PROFILES[country]||PROFILES.US).language;
    return {country,language,currency,scope:'country',source:'currency'};
  }
  return {country:'WW',language:'en',currency:'USD',scope:'worldwide',source:'country'};
}
function displayRegion(cc,lang){
  if(cc==='WW')return 'Worldwide';
  try{return new Intl.DisplayNames([lang||'en'],{type:'region'}).of(cc)||cc}catch{return cc}
}
function localizeCountryOptions(state){
  const c=$('#country');if(!c)return;
  let dn=null;try{dn=new Intl.DisplayNames([state.language],{type:'region'})}catch{}
  for(const o of c.options){
    const cc=String(o.value||'').toUpperCase();
    if(cc==='WW'){const ww=window.SEEKVERA_LOCALE_R14?.t?.('worldwide')||'Worldwide';o.textContent='🌐 '+ww;continue}
    if(/^[A-Z]{2}$/.test(cc)){try{o.textContent=dn?.of(cc)||o.textContent||cc}catch{}}
  }
}
function localizeLanguageOptions(state){
  const l=$('#lang');if(!l)return;
  let dn=null;try{dn=new Intl.DisplayNames([state.language],{type:'language'})}catch{}
  for(const o of l.options){
    const code=String(o.value||'').toLowerCase();
    if(code==='auto')continue;
    if(code)try{o.textContent=dn?.of(code)||o.textContent||code}catch{}
  }
}
function applyScope(state){
  const buttons=[...document.querySelectorAll('[data-scope]')];
  for(const b of buttons)b.classList.toggle('active',b.dataset.scope===(state.country==='WW'?'worldwide':'country'));
  try{localStorage.setItem('seekvera_scope',state.country==='WW'?'worldwide':'country')}catch{}
}
function applyState(state,{explicit=true,reason='manual'}={}){
  const sig=[state.country,state.language,state.currency,state.scope].join('|');
  syncing=true;lastReason=reason;
  document.documentElement.classList.add('sv-r15-applying');
  const c=$('#country'),l=$('#lang'),cur=$('#currency');
  if(c){
    ensureOption(c,state.country,state.country==='WW'?'🌐 Worldwide':displayRegion(state.country,state.language));
    c.value=state.country;
  }
  if(l){
    ensureOption(l,state.language,state.language);
    l.value=state.language;
  }
  if(cur){
    for(const code of Object.keys(CURRENCY_PRIMARY).sort())ensureOption(cur,code,code);
    ensureOption(cur,state.currency,state.currency);
    cur.value=state.currency;
  }
  try{
    localStorage.setItem('seekvera_country',state.country);
    localStorage.setItem('seekvera_lang',state.language);
    localStorage.setItem('seekvera_currency',state.currency);
    localStorage.setItem('seekvera_locale_source',state.source||'country');
    if(explicit)localStorage.setItem('seekvera_country_explicit','1');
  }catch{}
  document.documentElement.lang=state.language;
  document.documentElement.dir=RTL.has(state.language)?'rtl':'ltr';
  if(document.body){
    document.body.dataset.country=state.country;
    document.body.dataset.language=state.language;
    document.body.dataset.currency=state.currency;
  }
  applyScope(state);
  lastSignature=sig;
  window.SEEKVERA_LOCALE_STATE=Object.freeze({...state});
  // Apply bundled/local translators only after the atomic state is complete.
  try{window.SEEKVERA_LOCALE_R14?.apply?.()}catch{}
  try{window.SEEKVERA_R14_CATEGORIES?.apply?.()}catch{}
  try{window.SEEKVERA_I18N?.apply?.()}catch{}
  clearTimeout(settleTimer);
  settleTimer=setTimeout(()=>{
    try{window.SEEKVERA_LOCALE_R14?.apply?.()}catch{}
    try{window.SEEKVERA_R14_CATEGORIES?.apply?.()}catch{}
    localizeCountryOptions(state);
    localizeLanguageOptions(state);
    requestAnimationFrame(()=>requestAnimationFrame(()=>document.documentElement.classList.remove('sv-r15-applying')));
  },80);
  syncing=false;
  return state;
}
function storedState(){
  let country='WW',language='en',currency='USD',source='country',explicit=false;
  try{
    country=String(localStorage.getItem('seekvera_country')||'WW').toUpperCase();
    language=String(localStorage.getItem('seekvera_lang')||'en');
    currency=String(localStorage.getItem('seekvera_currency')||'USD').toUpperCase();
    source=String(localStorage.getItem('seekvera_locale_source')||'country');
    explicit=localStorage.getItem('seekvera_country_explicit')==='1';
  }catch{}
  if(!explicit&&!localStorage.getItem?.('seekvera_locale_source'))return null;
  if(source==='language')return {...localeStateFrom('language',language),source:'language'};
  if(source==='currency')return {...localeStateFrom('currency',currency),source:'currency'};
  return {...localeStateFrom('country',country),source:'country'};
}
function reconcile({reason='reconcile',explicit=true}={}){
  const s=storedState();
  if(s)return applyState(s,{explicit,reason});
  return null;
}
function coherentProgrammaticChange(target){
  try{
    const cc=String(localStorage.getItem('seekvera_country')||'').toUpperCase();
    const lg=String(localStorage.getItem('seekvera_lang')||'');
    const cu=String(localStorage.getItem('seekvera_currency')||'').toUpperCase();
    const p=PROFILES[cc];
    if(!p)return false;
    if(target.id==='lang')return target.value===lg&&p.language===lg&&p.currency===cu;
    if(target.id==='currency')return target.value===cu&&p.currency===cu&&p.language===lg;
  }catch{}
  return false;
}
function handleChange(e){
  const t=e.target;if(!t||!['country','lang','currency'].includes(t.id))return;
  // This coordinator is the sole change owner. Stop older handlers from racing each other.
  e.stopImmediatePropagation();
  if(syncing)return;
  let source=t.id==='lang'?'language':t.id;
  if(!e.isTrusted&&source!=='country'&&coherentProgrammaticChange(t))source='country';
  const state=localeStateFrom(source,t.value);
  applyState(state,{explicit:true,reason:'change:'+source});
}
document.addEventListener('change',handleChange,true);

function boot(){
  // Existing saved selection is reconciled atomically. If there is no explicit selection,
  // allow the existing geo/device auto-country routine to choose first, then seal it.
  const s=storedState();
  if(s)applyState(s,{explicit:true,reason:'boot-saved'});
  else setTimeout(()=>{
    let cc='';try{cc=String(localStorage.getItem('seekvera_country')||'').toUpperCase()}catch{}
    if(cc&&cc!=='WW'&&PROFILES[cc])applyState(localeStateFrom('country',cc),{explicit:false,reason:'boot-auto'});
    else applyState(localeStateFrom('country','WW'),{explicit:false,reason:'boot-worldwide'});
  },2800);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(boot,0),{once:true});else setTimeout(boot,0);
window.addEventListener('pageshow',()=>setTimeout(()=>reconcile({reason:'pageshow'}),0));
window.addEventListener('storage',e=>{if(['seekvera_country','seekvera_lang','seekvera_currency','seekvera_locale_source'].includes(e.key))setTimeout(()=>reconcile({reason:'storage',explicit:false}),0)});

const st=document.createElement('style');st.id='sv-r15-stability';st.textContent=`
html.sv-r15-applying .r5-top,html.sv-r15-applying .r5-hero,html.sv-r15-applying .r5-chat,html.sv-r15-applying #categories{transition:none!important;animation:none!important}
.sv-controls .sv-select{min-width:0;text-overflow:ellipsis}
`;document.head.appendChild(st);

window.SEEKVERA_LOCALE_R15={
  version:'20260924-r15',
  profiles:PROFILES,
  languagePrimary:LANG_PRIMARY,
  currencyPrimary:CURRENCY_PRIMARY,
  setCountry:cc=>applyState(localeStateFrom('country',cc),{explicit:true,reason:'api-country'}),
  setLanguage:lg=>applyState(localeStateFrom('language',lg),{explicit:true,reason:'api-language'}),
  setCurrency:cu=>applyState(localeStateFrom('currency',cu),{explicit:true,reason:'api-currency'}),
  reconcile,
  state:()=>window.SEEKVERA_LOCALE_STATE||null,
  debug:()=>({lastSignature,lastReason,syncing})
};
})();
