import {filterCameras,inferCameraLocation,fold,validCamera,mapUrls,safeSourceUrl,localTime,freshTimestamp,regionNames,locationNameMatches} from './world-live-core.mjs';
const root=document.getElementById('worldLive');root.setAttribute('data-no-translate','');
const $=id=>document.getElementById(id),HOST=location.hostname;
const API=['seekveraglobal.com','www.seekveraglobal.com'].includes(HOST)||HOST.endsWith('workers.dev')?'':'https://seekvera-main.seekvera-global.workers.dev';
const cache=new Map();let catalogue=[],directories={},supportedLanguages=['en','ar','fr','zh','ja'],source={},reviewed={},labels={},language='',country='WW',selected='',area='',renderSequence=0,selectionSequence=0,controller=null,expiryTimer=0,lastCountry='';
const params=new URLSearchParams(location.search);const query=String(params.get('q')||'').slice(0,160);
function appLanguage(){const selected=String(localStorage.getItem('seekvera_lang')||document.documentElement.lang||navigator.language||'en');return (selected==='auto'?navigator.language||'en':selected).split(/[-_]/)[0]}
function appCountry(){const value=String(localStorage.getItem('seekvera_country')||'WW').toUpperCase();return value==='WW'||/^[A-Z]{2}$/.test(value)?value:'WW'}
function region(code){if(code==='WW')return labels.all;try{return new Intl.DisplayNames([language],{type:'region'}).of(code)||code}catch{return code}}
function text(key){return labels[key]||''}
function element(tag,value,className){const e=document.createElement(tag);if(value)e.textContent=value;if(className)e.className=className;return e}
function numeric(value){try{return new Intl.NumberFormat(language).format(value)}catch{return String(value)}}
function date(value){try{return new Intl.DateTimeFormat(language,{dateStyle:'medium',timeStyle:'short'}).format(new Date(value))}catch{return value}}
function languageName(code){try{return new Intl.DisplayNames(['en'],{type:'language'}).of(code)||code}catch{return code}}
async function json(url,signal){const r=await fetch(url,{signal,cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return r.json()}
async function labelPack(code,signal){
 if(cache.has(code))return cache.get(code);if(reviewed[code]){cache.set(code,reviewed[code]);return reviewed[code]}
 try{const pack=await json('/data/world-live-locales/'+encodeURIComponent(code)+'.json',signal);if(Object.keys(source).every(k=>typeof pack.labels?.[k]==='string'&&pack.labels[k].trim())){cache.set(code,pack.labels);return pack.labels}}catch(e){if(signal.aborted)throw e}
 const keys=Object.keys(source),output={};
 for(let i=0;i<keys.length;i+=18){const part=keys.slice(i,i+18),r=await fetch(API+'/api/ui-translate',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({language:languageName(code),strings:part.map(k=>source[k])}),signal,cache:'no-store'});const d=await r.json();if(!r.ok||!d.ok||!Array.isArray(d.translations)||d.translations.length!==part.length||d.translations.some(v=>typeof v!=='string'||!v.trim()))throw Error('labels unavailable');part.forEach((k,j)=>output[k]=d.translations[j])}
 cache.set(code,output);return output
}
function matching(){return filterCameras(catalogue,{country,area})}
function countryOptions(){const profiles=window.SEEKVERA_LOCALE_R15?.profiles||{};const codes=Object.keys(profiles).filter(cc=>cc!=='WW'&&/^[A-Z]{2}$/.test(cc));const list=codes.length?codes:[...new Set([...catalogue.map(c=>c.country),...Object.keys(directories)])];const options=[new Option(text('all'),'WW'),...list.map(cc=>[cc,region(cc)]).sort((a,b)=>a[1].localeCompare(b[1],language)).map(([cc,name])=>new Option(name,cc))];$('wlCountry').replaceChildren(...options);$('wlCountry').value=country}
function directory(){const link=safeSourceUrl(directories[country]);$('wlMore').hidden=!link;if(link)$('wlMore').href=link}
async function refreshLocale(){
 const sequence=++renderSequence;language=appLanguage();controller?.abort();controller=new AbortController();const currentController=controller,signal=currentController.signal;const timeout=setTimeout(()=>currentController.abort(),25000);
 root.querySelectorAll('[data-wl]').forEach(e=>e.textContent='');
 $('wlContent').hidden=true;$('wlLoading').hidden=false;$('wlLoading').replaceChildren(document.createTextNode('◌'));
 try{const pack=await labelPack(language,signal);if(sequence!==renderSequence)return;labels=pack;document.documentElement.lang=language;document.documentElement.dir=['ar','fa','ur','he','ps','dv'].includes(language)?'rtl':'ltr';root.querySelectorAll('[data-wl]').forEach(e=>e.textContent=text(e.dataset.wl));$('wlMap').title=text('map');countryOptions();directory();render();$('wlContent').hidden=false;$('wlLoading').hidden=true}
 catch{if(sequence!==renderSequence)return;const button=element('button','↻');button.type='button';button.setAttribute('aria-label',window.SEEKVERA_I18N?.t('Try again')||'↻');button.addEventListener('click',refreshLocale);$('wlLoading').replaceChildren(document.createTextNode('⚠ '),button)}
 finally{clearTimeout(timeout)}
}
function render(){
 const cameras=matching();if(!cameras.some(c=>c.id===selected))selected=cameras[0]?.id||'';
 $('wlCamera').replaceChildren(...cameras.map(c=>new Option(c.city+' · '+c.area,c.id)));$('wlCamera').value=selected;$('wlCamera').disabled=!cameras.length;$('wlEmpty').hidden=!!cameras.length;$('wlCount').textContent=text('cameras')+' · '+numeric(cameras.length);$('wlCards').replaceChildren();
 for(const c of cameras){const card=element('article','', 'wl-card');card.setAttribute('aria-current',c.id===selected?'true':'false');card.append(element('h3',c.city),element('p',c.area),element('p',region(c.country)));const button=element('button',text('camera'));button.type='button';button.addEventListener('click',()=>{selected=c.id;render();$('wlViewer').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'})});card.append(button);$('wlCards').append(card)}
 const camera=cameras.find(c=>c.id===selected);$('wlViewer').hidden=!camera;if(camera)selectCamera(camera);else{$('wlMap').removeAttribute('src');$('wlAlertList').replaceChildren();$('wlAlertState').textContent='';selectionSequence++;clearTimeout(expiryTimer)}
 directory()
}
async function selectCamera(camera){
 const sequence=++selectionSequence;clearTimeout(expiryTimer);$('wlSelected').textContent=camera.city+' · '+camera.area;$('wlProvider').textContent=camera.source;$('wlOpen').href=safeSourceUrl(camera.sourceUrl);$('wlTime').textContent=localTime(camera,language);$('wlTime').dateTime=new Date().toISOString();$('wlStatus').textContent=text('unknown');$('wlChecked').textContent='';
 const map=mapUrls(camera);if($('wlMap').src!==map.embed)$('wlMap').src=map.embed;$('wlMapOpen').href=map.open;$('wlAlertList').replaceChildren();$('wlAlertState').textContent='◌';
 const ctl=new AbortController(),timeout=setTimeout(()=>ctl.abort(),12000);
 const answers=await Promise.allSettled([json(API+'/api/world-live/status?camera='+encodeURIComponent(camera.id),ctl.signal),json(API+'/api/world-live/alerts?camera='+encodeURIComponent(camera.id),ctl.signal)]);clearTimeout(timeout);if(sequence!==selectionSequence)return;
 const status=answers[0].status==='fulfilled'?answers[0].value:null;if(status?.ok&&status.camera===camera.id&&freshTimestamp(status.checkedAt)){$('wlStatus').textContent=status.sourceReachable?text('unknown'):text('sourceUnavailable');$('wlChecked').textContent=date(status.checkedAt)}
 const alerts=answers[1].status==='fulfilled'?answers[1].value:null;if(!alerts?.ok||alerts.camera!==camera.id||!freshTimestamp(alerts.checkedAt)||Date.parse(alerts.expiresAt)<=Date.now()){$('wlAlertState').textContent=text('alertsUnavailable');return}
 const available=alerts.sources.filter(s=>s.available).map(s=>s.name);const events=alerts.events.filter(e=>Date.parse(e.expiresAt)>Date.now());$('wlAlertState').textContent=(events.length?text('updated')+' · '+date(alerts.checkedAt):text('noAlerts'))+' · '+available.join(' / ');
 for(const item of events){let url;try{const parsed=new URL(item.url);if(parsed.protocol!=='https:'||!['earthquake.usgs.gov','www.gdacs.org'].includes(parsed.hostname))continue;url=parsed.href}catch{continue}const card=element('article','','wl-alert'),link=element('a',text(item.type)+(Number.isFinite(item.magnitude)?' · M'+numeric(item.magnitude):'')+' · '+item.source+' ↗');link.href=url;link.target='_blank';link.rel='noopener noreferrer';card.append(link,element('p',numeric(item.distanceKm)+' km'),element('time',date(item.updatedAt)));$('wlAlertList').append(card)}
 expiryTimer=setTimeout(()=>{if(sequence!==selectionSequence)return;$('wlAlertState').textContent=text('alertsUnavailable');$('wlAlertList').replaceChildren()},Math.max(1,Date.parse(alerts.expiresAt)-Date.now()))
}
function inferInitialCountry(){
 if(/\b(?:worldwide|all countries|the whole world|around the world)\b|كل الدول|كل البلدان|كل العالم|العالم كله|monde entier|todo el mundo|mundo inteiro|weltweit|全世界|所有国家|世界中|전 세계/iu.test(query)){country='WW';area='';return}
 const inferred=inferCameraLocation(catalogue,query,language,supportedLanguages);if(inferred.country!=='WW'){country=inferred.country;area=inferred.area;return}
 const codes=Object.keys(window.SEEKVERA_LOCALE_R15?.profiles||{});const needle=' '+fold(query)+' ';for(const cc of codes){if(!/^[A-Z]{2}$/.test(cc))continue;const names=regionNames(cc,supportedLanguages);if(names.some(n=>locationNameMatches(query,n))){country=cc;return}}
}
$('wlCountry').addEventListener('change',()=>{country=$('wlCountry').value;area='';$('wlCity').value='';const before=appCountry();if(window.SEEKVERA_LOCALE_R15?.setCountry){window.SEEKVERA_LOCALE_R15.setCountry(country);if(before===country)render()}else render()});
let cityTimer=0;$('wlCity').addEventListener('input',()=>{area=$('wlCity').value.trim();clearTimeout(cityTimer);cityTimer=setTimeout(render,180)});$('wlCamera').addEventListener('change',()=>{selected=$('wlCamera').value;render()});$('wlRefresh').addEventListener('click',()=>{const camera=matching().find(c=>c.id===selected);if(camera)selectCamera(camera)});
window.addEventListener('seekvera:locale-change',()=>{const cc=appCountry();if(cc!==lastCountry){country=cc;area='';$('wlCity').value=''}lastCountry=cc;if(appLanguage()!==language)refreshLocale();else if(Object.keys(labels).length){countryOptions();render()}});
setInterval(()=>{const camera=catalogue.find(c=>c.id===selected);if(camera&&!$('wlContent').hidden)$('wlTime').textContent=localTime(camera,language)},30000);
setInterval(()=>{if(document.visibilityState==='visible'&&!$('wlContent').hidden){const camera=matching().find(c=>c.id===selected);if(camera)selectCamera(camera)}},300000);
try{[source,reviewed]=await Promise.all([json('/data/world-live-ui-source.json'),json('/data/world-live-ui-reviewed.json')]);const [data,dirs,manifest]=await Promise.all([json('/data/world-live-cameras.json'),json('/data/world-live-directories.json'),json('/i18n-r32/manifest.json')]);catalogue=data.cameras.filter(validCamera);directories=dirs.countries;supportedLanguages=manifest.languages;language=appLanguage();country=appCountry();lastCountry=country;inferInitialCountry();$('wlCity').value=area;await refreshLocale()}catch{ $('wlLoading').textContent='⚠'; }
