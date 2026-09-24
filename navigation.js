/* SEEKVERA universal in-app navigation: Back + Home on every internal page */
(()=>{'use strict';
const HOME_PATHS=new Set(['/','/index.html','/app.html']);
const sameOriginReferrer=()=>{try{return document.referrer&&new URL(document.referrer).origin===location.origin}catch{return false}};
function goHome(){location.href='index.html'}
function goBack(){
  if(sameOriginReferrer()&&history.length>1){history.back();return;}
  const last=sessionStorage.getItem('seekvera_last_internal_page');
  if(last&&last!==location.pathname+location.search+location.hash){location.href=last;return;}
  goHome();
}
function rememberInternalLinks(){
  document.addEventListener('click',e=>{
    const a=e.target.closest?.('a[href]');if(!a)return;
    try{const u=new URL(a.href,location.href);if(u.origin===location.origin){sessionStorage.setItem('seekvera_last_internal_page',location.pathname+location.search+location.hash)}}catch{}
  },true);
}
function build(){
  rememberInternalLinks();
  if(HOME_PATHS.has(location.pathname))return;
  if(document.getElementById('svUniversalNav'))return;
  const st=document.createElement('style');st.id='svUniversalNavStyles';st.textContent=`
#svUniversalNav{position:fixed;z-index:2147483000;top:calc(env(safe-area-inset-top,0px) + 10px);inset-inline-start:10px;display:flex;gap:8px;align-items:center;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
#svUniversalNav button,#svUniversalNav a{appearance:none;border:1px solid rgba(15,23,42,.16);background:rgba(255,255,255,.96);color:#0f172a;min-height:42px;padding:0 13px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;gap:7px;font:700 14px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;text-decoration:none;box-shadow:0 8px 24px rgba(15,23,42,.14);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);cursor:pointer}
#svUniversalNav button:active,#svUniversalNav a:active{transform:scale(.97)}
#svUniversalNav .sv-nav-icon{font-size:20px;line-height:1}
@media(max-width:640px){#svUniversalNav{top:calc(env(safe-area-inset-top,0px) + 7px);inset-inline-start:7px;gap:6px}#svUniversalNav button,#svUniversalNav a{min-height:40px;padding:0 10px;font-size:12px}.sv-nav-label{display:none}#svUniversalNav .sv-nav-icon{font-size:21px}}
@media(prefers-color-scheme:dark){#svUniversalNav button,#svUniversalNav a{background:rgba(15,23,42,.94);color:#fff;border-color:rgba(255,255,255,.18)}}`;
  document.head.appendChild(st);
  const nav=document.createElement('nav');nav.id='svUniversalNav';nav.setAttribute('aria-label','Page navigation');
  nav.innerHTML=`<button type="button" id="svBackButton" aria-label="Back"><span class="sv-nav-icon" aria-hidden="true">←</span><span class="sv-nav-label">Back</span></button><a href="index.html" id="svHomeButton" aria-label="Home"><span class="sv-nav-icon" aria-hidden="true">⌂</span><span class="sv-nav-label">Home</span></a>`;
  document.body.appendChild(nav);
  document.getElementById('svBackButton')?.addEventListener('click',goBack);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',build,{once:true});else build();
})();
