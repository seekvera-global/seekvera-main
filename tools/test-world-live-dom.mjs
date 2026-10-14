import assert from 'node:assert/strict';
import fs from 'node:fs';
const {JSDOM}=await import(process.env.DOM_QA_MODULE||'jsdom');
const dom=new JSDOM(fs.readFileSync('world-live.html','utf8'),{url:'https://seekveraglobal.com/world-live.html?q=Show%20live%20cameras%20worldwide',pretendToBeVisual:true});
const window=dom.window;
const originals=new Map();for(const key of ['window','document','location','navigator','localStorage','Option','matchMedia','fetch','setInterval','setTimeout'])originals.set(key,Object.getOwnPropertyDescriptor(globalThis,key));
for(const [key,value] of Object.entries({window,document:window.document,location:window.location,navigator:window.navigator,localStorage:window.localStorage,Option:window.Option,matchMedia:()=>({matches:true})}))Object.defineProperty(globalThis,key,{configurable:true,writable:true,value});
window.HTMLElement.prototype.scrollIntoView=function(){};
const realTimeout=globalThis.setTimeout;globalThis.setTimeout=(fn,ms,...args)=>{const timer=realTimeout(fn,ms,...args);timer.unref?.();return timer};globalThis.setInterval=()=>0;
window.localStorage.setItem('seekvera_lang','en');window.localStorage.setItem('seekvera_country','NG');
const profiles={WW:{language:'en',currency:'USD'},JP:{language:'ja',currency:'JPY'},LB:{language:'ar',currency:'LBP'},NG:{language:'en',currency:'NGN'},FR:{language:'fr',currency:'EUR'}};
window.SEEKVERA_LOCALE_R15={profiles,setCountry(code){window.localStorage.setItem('seekvera_country',code);window.localStorage.setItem('seekvera_lang',profiles[code].language);window.dispatchEvent(new window.CustomEvent('seekvera:locale-change'))}};
window.SEEKVERA_I18N={t:key=>key==='Try again'?'Réessayer':key};
const requests=[];
globalThis.fetch=async(url,options={})=>{
 const u=new URL(url,'https://seekveraglobal.com');requests.push(u.pathname);
 if(u.pathname.startsWith('/data/')){const path='.'+u.pathname;return fs.existsSync(path)?Response.json(JSON.parse(fs.readFileSync(path))):new Response('missing',{status:404})}
 if(u.pathname.startsWith('/api/world-live/'))return Response.json(u.pathname.endsWith('/status')?{ok:true,camera:u.searchParams.get('camera'),status:'unknown',sourceReachable:true,checkedAt:new Date().toISOString()}:{ok:true,camera:u.searchParams.get('camera'),checkedAt:new Date().toISOString(),expiresAt:new Date(Date.now()+600000).toISOString(),sources:[{name:'USGS',available:true},{name:'GDACS',available:false}],events:[]});
 if(u.pathname==='/api/ui-translate')return Response.json({ok:false},{status:503});
 throw Error('Unexpected request '+url)
};
async function until(condition,message){const deadline=Date.now()+3000;while(!condition()){if(Date.now()>deadline)throw Error(message);await new Promise(resolve=>realTimeout(resolve,15))}}
try{
 await import('../world-live-ui.mjs?dom-test');
 const $=id=>window.document.getElementById(id);await until(()=>$('wlContent').hidden===false,'initial page');
 assert.equal($('wlCountry').value,'WW');assert.equal($('wlCards').children.length,15);$('wlCamera').value='tokyo';$('wlCamera').dispatchEvent(new window.Event('change'));assert.match($('wlSelected').textContent,/Tokyo/);assert.match($('wlMap').src,/openstreetmap/);assert.equal([...$('wlCountry').options].filter(o=>o.value==='WW').length,1);assert.equal($('wlMore').hidden,true);assert.equal(window.localStorage.getItem('seekvera_country'),'NG','worldwide search does not alter the app country');
 $('wlCountry').value='LB';$('wlCountry').dispatchEvent(new window.Event('change'));
 await until(()=>$('wlContent').hidden===false&&window.document.documentElement.lang==='ar','Arabic country switch');assert.equal(window.document.documentElement.dir,'rtl');assert.equal($('wlCards').children.length,1);assert.match(window.document.querySelector('h1').textContent,/شاهد/);assert.match($('wlSelected').textContent,/Beirut/);assert.equal(window.localStorage.getItem('seekvera_country'),'LB');
 $('wlCity').value='no-such-city';$('wlCity').dispatchEvent(new window.Event('input'));await until(()=>$('wlEmpty').hidden===false,'empty city');assert.equal($('wlViewer').hidden,true);assert.equal($('wlCards').children.length,0);
 $('wlCountry').value='NG';$('wlCountry').dispatchEvent(new window.Event('change'));await until(()=>$('wlContent').hidden===false&&window.document.documentElement.lang==='en','Nigeria switch');assert.equal($('wlCity').value,'');assert.equal($('wlCards').children.length,0);assert.equal($('wlMore').hidden,true);assert.equal($('wlEmpty').hidden,false);
 window.localStorage.setItem('seekvera_lang','fr');window.dispatchEvent(new window.CustomEvent('seekvera:locale-change'));await until(()=>window.document.querySelector('h1').textContent==='Regarder le monde en direct','French switch');
 window.localStorage.setItem('seekvera_lang','dv');window.dispatchEvent(new window.CustomEvent('seekvera:locale-change'));await until(()=>$('wlLoading').textContent.includes('⚠'),'translation outage');assert.equal($('wlContent').hidden,true);assert.equal(window.document.querySelector('h1').textContent,'','previous language must not leak during an outage');assert($('wlLoading').querySelector('button').getAttribute('aria-label'));
 assert.equal(requests.filter(path=>path==='/api/ui-translate').length,1);
 console.log('PASS: DOM worldwide search independent of stored country, camera selection, atomic Arabic/RTL switch, unavailable city/country, French switch, retry accessibility and translation-outage no-leak guard. Not browser layout or physical audio certification.');
}finally{dom.window.close();for(const [key,descriptor] of originals){if(descriptor)Object.defineProperty(globalThis,key,descriptor);else delete globalThis[key]}}
