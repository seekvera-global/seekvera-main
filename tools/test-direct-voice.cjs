const fs=require('fs'), vm=require('vm'), assert=require('node:assert/strict');
const source=fs.readFileSync('worker-r76.js','utf8');
const context={Response, Headers, URL, setTimeout, clearTimeout, console};
vm.createContext(context);
vm.runInContext(source.slice(source.indexOf('const RELEASE='),source.indexOf('export default')),context);
const cases=[['بدي أسافر','travel','ar'],['بدي اشتري','shopping','ar'],['بدي سيارة','cars','ar'],['دوريني على شغل','jobs','ar'],['Find me a hotel','travel','en'],['Je veux acheter une voiture','cars','fr'],['Ich möchte eine Wohnung mieten','property','de'],['Quiero comprar un coche','cars','es'],['Bana bir iş bul','jobs','tr'],['我想买汽车','cars','zh'],['ホテルを探して','travel','ja'],['مجھے نوکری چاہیے','jobs','ur']];
for(const [message,category,language] of cases){const result=context.fastActionResult(message,{language:'auto'});assert.equal(result?.category,category,message);assert.equal(result.language,language,message);assert.ok(result.route,message);assert.ok(!/[?؟]/.test(result.response),message)}
assert.equal(context.fastActionResult('مرحبا',{language:'auto'}),null);
const ui=fs.readFileSync('r31-ui-polish.js','utf8');
const start=ui.indexOf('  function autoRoute('),end=ui.indexOf('  function replayPendingRouteVoice',start);
const events=new EventTarget(),tasks=[];let moves=0,pending=true;
const nav={window:events,sessionStorage:{removeItem(){pending=false}},shouldAutoRoute:()=>true,setIntent(){},routeUrl:()=>'/travel.html',location:{assign(){moves++}},pendingVoiceOnNextPage(){},setTimeout(fn,ms){tasks.push({fn,ms});return tasks.length},clearTimeout(){}};
vm.createContext(nav);vm.runInContext(ui.slice(start,end),nav);
nav.autoRoute('travel','بدي أسافر','أكيد','ar',true);
events.dispatchEvent(new Event('seekvera:tts-start'));assert.equal(moves,0,'must not destroy the audio context when playback starts');
assert.equal(tasks.filter(t=>t.ms<1000).length,0,'must not navigate before server audio is ready');
events.dispatchEvent(new Event('seekvera:tts-end'));assert.equal(moves,1);assert.equal(pending,false);
events.dispatchEvent(new Event('seekvera:tts-end'));assert.equal(moves,1,'navigate once');
assert.ok(!ui.includes('if (similarReply(reply, previous))'),'never replace a correctly localized server reply with UI language');
console.log('PASS: 12 language/intent cases; no pre-route questions; voice navigation preserves complete acknowledgement; localized reply retained.');

const voice=fs.readFileSync("voice-ai.js","utf8"),chunkCtx={};vm.createContext(chunkCtx);vm.runInContext(voice.slice(voice.indexOf("function cleanSpeech("),voice.indexOf("function unlockTTS(")),chunkCtx);assert.equal(chunkCtx.splitSpeech("أكيد، عم بفتحلك القسم المناسب.").length,1);console.log("PASS: short acknowledgement uses one audio request");
