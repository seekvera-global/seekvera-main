const CACHE='seekvera-r20-final-ui-20260925';
const R21_SCRIPT='/r21-card-cleanup.js?v=20260925-r21';
const CORE=['./','./index.html','./app.html','./premium.css','./superapp.js','./voice-ai.js','./global-ui.js','./global-ui.css','./i18n-ui.js','./r20-final-guard.js','./r20-extra-categories.js','./r21-card-cleanup.js','./locale-r15.js','./locale-r14.js','./locale-r14-categories.js','./i18n-premium.css','./navigation.js','./games.html','./media.html','./home-marketplace-r5.css','./games.js','./connectivity.html','./deal-agent.html','./deal-agent.js','./marketplace.html','./post-ad.html','./travel.html','./tourism.html','./wifi.html','./scan.html','./hub.html','./manifest.webmanifest','./favicon.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE).catch(()=>{})).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()).then(()=>self.clients.matchAll({type:'window'})).then(cs=>Promise.all(cs.map(c=>c.navigate(c.url).catch(()=>null)))))});
self.addEventListener('message',e=>{if(e.data==='SKIP_WAITING')self.skipWaiting()});
async function r21Html(resp){
 if(!resp)return resp;
 const ct=resp.headers.get('content-type')||'';
 if(!ct.includes('text/html'))return resp;
 let text=await resp.text();
 if(!/name=["']google["'][^>]*content=["']notranslate["']/i.test(text))text=text.replace(/<head(\s[^>]*)?>/i,m=>m+'<meta name="google" content="notranslate">');
 if(!/\btranslate=["']no["']/i.test(text))text=text.replace(/<html\b([^>]*)>/i,'<html$1 translate="no" class="notranslate">');
 if(!text.includes('r21-card-cleanup.js'))text=text.replace(/<\/body>/i,'<script src="'+R21_SCRIPT+'" defer></script></body>');
 const h=new Headers(resp.headers);h.delete('content-length');h.set('cache-control','no-store');
 return new Response(text,{status:resp.status,statusText:resp.statusText,headers:h});
}
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);if(u.origin!==self.location.origin)return;const critical=/\/(?:i18n-ui|voice-ai|global-ui|superapp|navigation|locale-r15|locale-r14|locale-r14-categories|r20-final-guard|r20-extra-categories|r21-card-cleanup)\.js$/.test(u.pathname);if(r.mode==='navigate'||/\.html$/.test(u.pathname)||u.pathname.endsWith('/')||critical){e.respondWith((async()=>{try{const resp=await fetch(r,{cache:'no-store'});const out=await r21Html(resp);if(out?.ok){const copy=out.clone();caches.open(CACHE).then(c=>c.put(r,copy))}return out}catch{const x=await caches.match(r)||await caches.match('./index.html');return r21Html(x)}})());return}e.respondWith(fetch(r).then(resp=>{if(resp.ok){const copy=resp.clone();caches.open(CACHE).then(c=>c.put(r,copy))}return resp}).catch(()=>caches.match(r)))});
