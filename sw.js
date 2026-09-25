const CACHE='seekvera-r57-native-first-voice-20260926';
const CORE=['./','./index.html','./app.html','./premium.css','./superapp.js','./voice-ai.js','./global-ui.js','./global-ui.css','./i18n-ui.js','./r20-final-guard.js','./r24-ai-controller.js','./r20-extra-categories.js','./r22-category-lock.js','./locale-r15.js','./locale-r14.js','./locale-r14-categories.js','./i18n-premium.css','./navigation.js','./games.html','./media.html','./home-marketplace-r5.css','./games.js','./connectivity.html','./deal-agent.html','./deal-agent.js','./marketplace.html','./post-ad.html','./travel.html','./tourism.html','./wifi.html','./scan.html','./hub.html','./manifest.webmanifest','./favicon.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE).catch(()=>{})).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('message',e=>{if(e.data==='SKIP_WAITING')self.skipWaiting()});
async function hardenHtml(resp){
  if(!resp)return resp;const ct=resp.headers.get('content-type')||'';if(!ct.includes('text/html'))return resp;
  let text=await resp.text();
  // Remove the retired R21 DOM watcher if any older cached/source page still references it.
  text=text.replace(/<script\b[^>]*src=["'][^"']*r21-card-cleanup\.js[^"']*["'][^>]*><\/script>\s*/gi,'');
  if(!/name=["']google["'][^>]*content=["']notranslate["']/i.test(text))text=text.replace(/<head(\s[^>]*)?>/i,m=>m+'<meta name="google" content="notranslate">');
  if(!/\btranslate=["']no["']/i.test(text))text=text.replace(/<html\b([^>]*)>/i,'<html$1 translate="no" class="notranslate">');
  const h=new Headers(resp.headers);h.delete('content-length');h.set('cache-control','no-store');h.set('x-seekvera-release','r23-stable');
  return new Response(text,{status:resp.status,statusText:resp.statusText,headers:h});
}
async function networkFirst(r,html=false){try{const resp=await fetch(r,{cache:'no-store'}),out=html?await hardenHtml(resp):resp;if(out?.ok){const copy=out.clone();caches.open(CACHE).then(c=>c.put(r,copy)).catch(()=>{})}return out}catch{const x=await caches.match(r)||await caches.match('./index.html');return html?hardenHtml(x):x}}
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);if(u.origin!==self.location.origin)return;const critical=/\/(?:r31-ui-polish|r24-ai-controller|i18n-ui|voice-ai|global-ui|superapp|navigation|locale-r15|locale-r14|locale-r14-categories|r20-final-guard|r20-extra-categories|r22-category-lock)\.js$/.test(u.pathname);if(r.mode==='navigate'||/\.html$/.test(u.pathname)||u.pathname.endsWith('/')||critical){e.respondWith(networkFirst(r,r.mode==='navigate'||/\.html$/.test(u.pathname)||u.pathname.endsWith('/')));return}e.respondWith(fetch(r).then(resp=>{if(resp.ok){const copy=resp.clone();caches.open(CACHE).then(c=>c.put(r,copy)).catch(()=>{})}return resp}).catch(()=>caches.match(r)))});
