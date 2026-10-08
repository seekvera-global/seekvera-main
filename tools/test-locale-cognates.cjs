const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
function option(text,value){return {textContent:text,_value:value,get value(){return this._value===undefined?this.textContent:this._value},set value(v){this._value=v},remove(){currency.options=currency.options.filter(x=>x!==this)}}}
const currency={options:[option('USD'),option('EUR'),option('USD — US Dollar','USD — US Dollar')],value:'USD',setAttribute(){},set title(v){}};
const country={options:[option('United States','US')],value:'US',setAttribute(){},set title(v){}};
let language='en';
const context={Intl,Set,console,$:s=>s==='#currency'?currency:s==='#country'?country:null,ensureControlStyles(){},labels:()=>['Country','Worldwide','Language','Auto','Currency'],wrapControl:()=>null,langCode:()=>language,window:{SEEKVERA_I18N:{t:s=>language==='ha'&&s==='United States'?'Amurka':s}}};
vm.createContext(context);const source=fs.readFileSync('global-ui.js','utf8');vm.runInContext(source.slice(source.indexOf('function localizeControls'),source.indexOf('function bindLocaleControls')),context);
context.localizeControls();assert.deepEqual(currency.options.map(x=>x.value),['USD','EUR']);
language='fr';context.localizeControls();assert.deepEqual(currency.options.map(x=>x.value),['USD','EUR']);assert.match(currency.options[0].textContent,/dollar des États-Unis/);
language='ar';context.localizeControls();assert.deepEqual(currency.options.map(x=>x.value),['USD','EUR']);assert.match(currency.options[0].textContent,/[\u0600-\u06ff]/);
language='ha';context.localizeControls();assert.equal(country.options[0].textContent,'Amurka');
const i18n=fs.readFileSync('i18n-ui.js','utf8');const lookup={QUICK:{},MEM:new Map([['rm\u0000News & Media','Noticies & Medios'],['rm\u0000📰 News & Media','News & Media']]),canonical:s=>s.trim(),plainKey:s=>s.replace(/^[^\p{L}\p{N}]+/u,'').trim(),localStorage:{getItem:()=>null},k:()=>''};vm.createContext(lookup);vm.runInContext(i18n.slice(i18n.indexOf('function get('),i18n.indexOf('function put(')),lookup);assert.equal(lookup.get('rm','📰 News & Media'),'📰 Noticies & Medios');
console.log('PASS: currency values stay stable and unique across languages; country pack fallback works; emoji labels reuse localized base text.');
