const CACHE='seekvera-one-app-v1-20260921';
const CORE=[
 './','./app.html','./index.html','./hub.html','./marketplace.html','./post-ad.html','./seller-plans.html',
 './travel.html','./tourism.html','./wifi.html','./scan.html','./terms.html','./privacy.html','./about.html',
 './property.html','./cars-auto.html','./shopping.html','./jobs.html','./business-software.html','./education.html',
 './solar.html','./health.html','./web-hosting.html','./import-export.html','./favicon.svg','./manifest.webmanifest','./seekvera-qr.svg'
];
self.addEventListener('install',event=>{
 event.waitUntil((async()=>{
  const cache=await caches.open(CACHE);
  await Promise.allSettled(CORE.map(url=>cache.add(url)));
  await self.skipWaiting();
 })());
});
self.addEventListener('activate',event=>{
 event.waitUntil((async()=>{
  const keys=await caches.keys();
  await Promise.all(keys.filter(k=>k.startsWith('seekvera-one-app-')&&k!==CACHE).map(k=>caches.delete(k)));
  await self.clients.claim();
 })());
});
self.addEventListener('fetch',event=>{
 const req=event.request;
 if(req.method!=='GET')return;
 const url=new URL(req.url);
 if(url.origin!==self.location.origin)return;
 if(url.pathname.includes('/api/'))return;
 if(req.mode==='navigate'){
  event.respondWith((async()=>{
   try{
    const fresh=await fetch(req);
    const cache=await caches.open(CACHE);
    cache.put(req,fresh.clone());
    return fresh;
   }catch{
    return (await caches.match(req))||(await caches.match('./app.html'));
   }
  })());
  return;
 }
 event.respondWith((async()=>{
  const cached=await caches.match(req);
  if(cached)return cached;
  try{
   const fresh=await fetch(req);
   if(fresh.ok){const cache=await caches.open(CACHE);cache.put(req,fresh.clone())}
   return fresh;
  }catch{return new Response('',{status:503,statusText:'Offline'})}
 })());
});