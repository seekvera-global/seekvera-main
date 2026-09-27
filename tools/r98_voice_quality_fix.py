from pathlib import Path
import re

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
VER='20260927-r98-voice-quality-recovery'
old="""async function localWhisperTranscribe(blob){
  const engine=await localWhisperEngine(),url=URL.createObjectURL(blob);
  try{
    const r=await engine(url,{task:'transcribe'}),text=String(r?.text||'').trim();
    if(!text)throw Error('local multilingual transcription returned no text');
    rememberChatVoiceLanguage('',text);
    return{text,language:codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'')||'auto',engine:'local-whisper-auto'}
  }finally{try{URL.revokeObjectURL(url)}catch(_){}}
}
"""
new="""function whisperLanguageName(code){
  code=codeOf(code);if(!code)return'';
  for(const [name,c] of Object.entries(NAME_CODE))if(c===code&&!name.includes(' '))return name;
  return code
}
function transcriptScript(text){
  const t=String(text||'');
  if(/[\\u0600-\\u06ff]/.test(t))return'arabic';
  if(/[\\u0e00-\\u0e7f]/.test(t))return'thai';
  if(/[\\u0900-\\u097f]/.test(t))return'devanagari';
  if(/[\\u0980-\\u09ff]/.test(t))return'bengali';
  if(/[\\u4e00-\\u9fff]/.test(t))return'han';
  if(/[\\u3040-\\u30ff]/.test(t))return'japanese';
  if(/[\\uac00-\\ud7af]/.test(t))return'korean';
  if(/[\\u0400-\\u04ff]/.test(t))return'cyrillic';
  if(/[\\u0590-\\u05ff]/.test(t))return'hebrew';
  if(/[\\u0370-\\u03ff]/.test(t))return'greek';
  if(/[A-Za-zÀ-ÖØ-öø-ÿ]/.test(t))return'latin';
  return''
}
function transcriptPoor(text){
  const t=String(text||'').replace(/[^\\p{L}\\p{N}'’-]+/gu,' ').trim();if(!t)return true;
  const w=t.split(/\\s+/).filter(Boolean);if(w.length<2)return t.length<4;
  const low=w.map(x=>x.toLocaleLowerCase()),u=new Set(low);
  let maxRun=1,run=1;for(let i=1;i<low.length;i++){if(low[i]===low[i-1]){run++;maxRun=Math.max(maxRun,run)}else run=1}
  if(w.length>=6&&u.size/w.length<.34)return true;
  if(maxRun>=4)return true;
  return false
}
function hintedVoiceCodes(){
  const out=[];const add=x=>{const c=codeOf(x);if(c&&LANGS[c]&&!out.includes(c))out.push(c)};
  try{add(localStorage.getItem('seekvera_chat_voice_lang'));add(selectedLang());add(document.documentElement.lang);add(navigator.language)}catch(_){}
  return out.slice(0,3)
}
function transcriptScore(text,hint=''){
  const t=String(text||'').trim();if(!t)return-999;
  let score=Math.min(60,t.length/3);if(transcriptPoor(t))score-=120;
  const sc=transcriptScript(t),hc=codeOf(hint),expected={ar:'arabic',fa:'arabic',ur:'arabic',ps:'arabic',th:'thai',hi:'devanagari',mr:'devanagari',ne:'devanagari',bn:'bengali',zh:'han',ja:'japanese',ko:'korean',ru:'cyrillic',uk:'cyrillic',bg:'cyrillic',sr:'cyrillic',he:'hebrew',el:'greek'}[hc]||'';
  if(expected&&sc===expected)score+=80;
  return score
}
async function localWhisperTranscribe(blob){
  const engine=await localWhisperEngine(),url=URL.createObjectURL(blob);
  try{
    let r=await engine(url,{task:'transcribe'}),text=String(r?.text||'').trim(),chosenHint='',bestScore=transcriptScore(text);
    if(!text)throw Error('local multilingual transcription returned no text');
    if(transcriptPoor(text)){
      for(const hint of hintedVoiceCodes()){
        const language=whisperLanguageName(hint);if(!language)continue;
        try{
          const rr=await engine(url,{task:'transcribe',language}),tt=String(rr?.text||'').trim(),sc=transcriptScore(tt,hint);
          if(tt&&sc>bestScore){text=tt;r=rr;chosenHint=hint;bestScore=sc}
          if(tt&&!transcriptPoor(tt)&&sc>=80)break
        }catch(_){}
      }
    }
    if(!text||transcriptPoor(text))throw Error('local multilingual transcription quality was too low');
    rememberChatVoiceLanguage(chosenHint,text);
    return{text,language:codeOf(localStorage.getItem('seekvera_chat_voice_lang')||'')||chosenHint||'auto',engine:chosenHint?'local-whisper-recovered':'local-whisper-auto'}
  }finally{try{URL.revokeObjectURL(url)}catch(_){}}
}
"""
if new not in s:
    if old not in s: raise SystemExit('localWhisperTranscribe anchor missing')
    s=s.replace(old,new,1)
s=re.sub(r"window\.__seekveraVoiceMode='[^']+';", "window.__seekveraVoiceMode='local-whisper-quality-r98';", s, count=1)
p.write_text(s,encoding='utf-8')

# Cache-bust root pages that load voice-ai.
for hp in Path('.').glob('*.html'):
    h=hp.read_text(encoding='utf-8')
    h=re.sub(r'voice-ai\.js\?v=[^"\\s]+','voice-ai.js?v='+VER,h)
    if hp.name=='index.html': h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
    hp.write_text(h,encoding='utf-8')
psw=Path('sw.js'); sw=psw.read_text(encoding='utf-8'); sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1); psw.write_text(sw,encoding='utf-8')
print('R98_APPLIED')
