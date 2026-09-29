const RELEASE='20260929-r113-ai-reliability';
self.addEventListener('install',e=>{e.waitUntil(self.skipWaiting())});
self.addEventListener('activate',e=>{e.waitUntil((async()=>{for(const k of await caches.keys())await caches.delete(k);await self.clients.claim()})())});
self.addEventListener('message',e=>{if(e.data==='SKIP_WAITING')self.skipWaiting()});
