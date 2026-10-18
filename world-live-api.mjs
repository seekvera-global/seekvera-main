import {validCamera,distanceKm,safeSourceUrl} from './world-live-core.mjs';
const USGS='https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson';
const GDACS='https://www.gdacs.org/xml/rss.xml';
const TYPE_LABELS={EQ:'earthquake',TC:'cyclone',FL:'flood',VO:'volcano',WF:'wildfire',DR:'drought'};
function result(data,status=200){return Response.json(data,{status,headers:{'cache-control':'no-store','x-content-type-options':'nosniff'}})}
function publicLink(value,host){try{const u=new URL(value);return u.protocol==='https:'&&u.hostname===host&&!u.username&&!u.password&&!u.port?u.href:null}catch{return null}}
async function fetchBounded(url,fetcher,accept){const r=await fetcher(url,{headers:{accept,'user-agent':'SEEKVERA World Live/1.0'},redirect:'error',signal:AbortSignal.timeout(8000)});if(!r.ok)throw Error('upstream '+r.status);const text=await r.text();if(text.length>2*1024*1024)throw Error('oversized feed');return text}
export function usgsEvents(raw,camera,now=Date.now()){
 const data=JSON.parse(raw),generated=data?.metadata?.generated;
 if(!Number.isFinite(generated)||generated>now+60000||now-generated>15*60*1000)throw Error('stale USGS feed');
 if(!Array.isArray(data.features))throw Error('invalid USGS feed');
 return data.features.slice(0,500).flatMap(f=>{const p=f?.properties||{},coords=f?.geometry?.coordinates||[],lng=coords[0],lat=coords[1],time=p.time,url=publicLink(p.url,'earthquake.usgs.gov');
  if(!url||!Number.isFinite(time)||time>now+60000||now-time>86400000||!Number.isFinite(lat)||!Number.isFinite(lng)||Math.abs(lat)>90||Math.abs(lng)>180||!Number.isFinite(p.mag))return[];
  const distance=distanceKm(camera.latitude,camera.longitude,lat,lng);if(distance>500)return[];
  return[{id:'usgs:'+String(f.id||time),source:'USGS',type:'earthquake',magnitude:p.mag,latitude:lat,longitude:lng,distanceKm:Math.round(distance),occurredAt:new Date(time).toISOString(),updatedAt:new Date(Number.isFinite(p.updated)&&p.updated<=now+60000?p.updated:time).toISOString(),expiresAt:new Date(time+86400000).toISOString(),url}]
 })
}
function xmlText(item,tag){const value=item.match(new RegExp('<'+tag+'(?:\\s[^>]*)?>([\\s\\S]*?)</'+tag+'>','i'))?.[1]||'';return value.replace(/^<!\[CDATA\[|\]\]>$/g,'').replace(/<[^>]*>/g,'').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').trim()}
export function gdacsEvents(raw,camera,now=Date.now()){
 if(!/<rss\b/i.test(raw))throw Error('invalid GDACS feed');
 const items=[...raw.matchAll(/<item(?:\s[^>]*)?>([\s\S]*?)<\/item>/gi)].slice(0,300);
 return items.flatMap(([,item])=>{
  const type=xmlText(item,'gdacs:eventtype'),current=xmlText(item,'gdacs:iscurrent'),url=publicLink(xmlText(item,'link'),'www.gdacs.org');
  const updated=Date.parse(xmlText(item,'gdacs:datemodified')||xmlText(item,'pubDate')),start=Date.parse(xmlText(item,'gdacs:fromdate')||xmlText(item,'pubDate'));
  const point=xmlText(item,'georss:point').split(/\s+/).map(Number),[lat,lng]=point;
  if(!TYPE_LABELS[type]||current!=='true'||!url||!Number.isFinite(updated)||updated>now+60000||now-updated>7*86400000||point.length!==2||!Number.isFinite(lat)||!Number.isFinite(lng)||Math.abs(lat)>90||Math.abs(lng)>180)return[];
  const distance=distanceKm(camera.latitude,camera.longitude,lat,lng);if(distance>500)return[];
  return[{id:'gdacs:'+xmlText(item,'guid'),source:'GDACS',type:TYPE_LABELS[type],level:xmlText(item,'gdacs:alertlevel'),latitude:lat,longitude:lng,distanceKm:Math.round(distance),occurredAt:new Date(Number.isFinite(start)?start:updated).toISOString(),updatedAt:new Date(updated).toISOString(),expiresAt:new Date(updated+7*86400000).toISOString(),url}]
 })
}
async function findCamera(request,env){const id=new URL(request.url).searchParams.get('camera');if(!id||!/^[-a-z0-9]{1,70}$/.test(id))return null;const r=await env.ASSETS.fetch(new Request(new URL('/data/world-live-cameras.json',request.url)));if(!r.ok)throw Error('catalogue unavailable');const d=await r.json();return d.cameras?.find(c=>c.id===id&&validCamera(c))||null}
export async function worldLiveApi(request,env,fetcher=fetch){
 if(request.method!=='GET')return result({ok:false,error:'Method not allowed'},405);
 const path=new URL(request.url).pathname;let camera;try{camera=await findCamera(request,env)}catch{return result({ok:false,error:'Camera catalogue unavailable',retryable:true},503)}
 if(!camera)return result({ok:false,error:'Unknown camera'},404);
 const now=Date.now(),checkedAt=new Date(now).toISOString();
 if(path==='/api/world-live/status'){
  // HTTP reachability is not a stream-health signal. Never infer LIVE from HTTP 200.
  try{const response=await fetcher(safeSourceUrl(camera.sourceUrl),{method:'HEAD',redirect:'error',headers:{'user-agent':'SEEKVERA World Live/1.0'},signal:AbortSignal.timeout(6000)});return result({ok:true,camera:camera.id,status:'unknown',sourceReachable:response.ok,sourceHttpStatus:response.status,checkedAt})}catch{return result({ok:true,camera:camera.id,status:'unknown',sourceReachable:false,checkedAt})}
 }
 if(path!=='/api/world-live/alerts')return result({ok:false,error:'Not found'},404);
 const feeds=await Promise.allSettled([fetchBounded(USGS,fetcher,'application/json').then(raw=>usgsEvents(raw,camera,now)),fetchBounded(GDACS,fetcher,'application/xml').then(raw=>gdacsEvents(raw,camera,now))]);
 const sources=['USGS','GDACS'].map((name,i)=>({name,available:feeds[i].status==='fulfilled',checkedAt}));const events=feeds.flatMap(f=>f.status==='fulfilled'?f.value:[]).sort((a,b)=>Date.parse(b.updatedAt)-Date.parse(a.updatedAt));
 const available=sources.some(s=>s.available);return result({ok:available,camera:camera.id,radiusKm:500,checkedAt,expiresAt:new Date(now+10*60*1000).toISOString(),sources,events,scope:'Selected camera area; natural disasters only. This is not a safety assessment or a complete emergency warning service.'},available?200:503)
}
