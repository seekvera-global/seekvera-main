const SOURCE_HOSTS=new Set(['www.skylinewebcams.com','www.earthcam.com']);
export function safeSourceUrl(value){try{const url=new URL(value);return url.protocol==='https:'&&SOURCE_HOSTS.has(url.hostname)&&!url.username&&!url.password&&url.port===''?url.href:null}catch{return null}}
export function fold(value){return String(value||'').normalize('NFKD').replace(/\p{M}/gu,'').toLocaleLowerCase().replace(/[أإآ]/g,'ا').replace(/ى/g,'ي').replace(/[^\p{L}\p{N}\s-]/gu,' ').replace(/\s+/g,' ').trim()}
export function validCamera(camera){return camera&&/^[a-z0-9-]{1,70}$/.test(camera.id)&&/^[A-Z]{2}$/.test(camera.country)&&typeof camera.city==='string'&&safeSourceUrl(camera.sourceUrl)&&Number.isFinite(camera.latitude)&&Math.abs(camera.latitude)<=90&&Number.isFinite(camera.longitude)&&Math.abs(camera.longitude)<=180&&validTimezone(camera.timezone)}
export function validTimezone(timezone){try{new Intl.DateTimeFormat('en',{timeZone:timezone}).format();return true}catch{return false}}
export function filterCameras(cameras,{country='WW',query='',area=''}={}){
 const needle=fold(query),city=fold(area);
 return cameras.filter(validCamera).filter(c=>country==='WW'||c.country===country).filter(c=>{const hay=fold([c.city,c.area,c.aliases].join(' '));return(!city||hay.includes(city))&&(!needle||hay.includes(needle))})
}
export function inferCameraLocation(cameras,query,language='en'){
 const needle=' '+fold(query)+' ';let country='WW',area='';
 for(const camera of cameras){
  const names=[camera.city,camera.area,...String(camera.aliases||'').split(' ')].map(fold).filter(x=>x.length>=3);
  try{names.push(fold(new Intl.DisplayNames([language],{type:'region'}).of(camera.country)))}catch{}
  try{names.push(fold(new Intl.DisplayNames(['en'],{type:'region'}).of(camera.country)))}catch{}
  if(names.some(n=>needle.includes(' '+n+' '))){country=camera.country;const city=fold(camera.city);if(needle.includes(' '+city+' '))area=camera.city;break}
 }
 return{country,area}
}
export function mapUrls(camera){
 if(!validCamera(camera))return null;const lat=camera.latitude,lng=camera.longitude;
 const box=[Math.max(-180,lng-.07),Math.max(-85,lat-.04),Math.min(180,lng+.07),Math.min(85,lat+.04)].join(',');
 return{embed:'https://www.openstreetmap.org/export/embed.html?bbox='+encodeURIComponent(box)+'&layer=mapnik&marker='+encodeURIComponent(lat+','+lng),open:'https://www.openstreetmap.org/?mlat='+lat+'&mlon='+lng+'#map=12/'+lat+'/'+lng}
}
export function distanceKm(aLat,aLng,bLat,bLng){const rad=x=>x*Math.PI/180;const dLat=rad(bLat-aLat),dLng=rad(bLng-aLng);const a=Math.sin(dLat/2)**2+Math.cos(rad(aLat))*Math.cos(rad(bLat))*Math.sin(dLng/2)**2;return 6371*2*Math.atan2(Math.sqrt(a),Math.sqrt(Math.max(0,1-a)))}
export function localTime(camera,language='en',date=new Date()){try{return new Intl.DateTimeFormat(language,{timeZone:camera.timezone,dateStyle:'medium',timeStyle:'short'}).format(date)}catch{return date.toISOString()}}
export function freshTimestamp(timestamp,now=Date.now(),maximumAge=15*60*1000){const time=Date.parse(timestamp);return Number.isFinite(time)&&time<=now+60000&&now-time<=maximumAge}
