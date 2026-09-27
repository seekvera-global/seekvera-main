from pathlib import Path
import re
VER='20260927-r89-native-multilingual-voice'

# ---- Worker: decode base64 audio into byte array expected by Workers AI Whisper ----
p=Path('worker-r76.js')
w=p.read_text(encoding='utf-8')
w=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",w,count=1)
old="const base={audio:m[2],task:'transcribe',vad_filter:true,condition_on_previous_text:false,beam_size:5,no_speech_threshold:.72};"
new="const bin=atob(m[2]),audio=Array.from(bin,c=>c.charCodeAt(0));\n const base={audio,task:'transcribe',vad_filter:true,condition_on_previous_text:false,beam_size:5,no_speech_threshold:.72};"
if old in w:
    w=w.replace(old,new,1)
elif "const bin=atob(m[2]),audio=Array.from(bin,c=>c.charCodeAt(0));" not in w:
    raise SystemExit('ASR byte-array anchor missing')
needle="r88:true,r88Runtime:'fast-auto-asr-server-first-tts-natural-fallback',"
if needle in w and "r89:true" not in w:
    w=w.replace(needle,"r89:true,r89Runtime:'workers-ai-whisper-byte-array-no-consent',"+needle,1)
p.write_text(w,encoding='utf-8')

# ---- Browser voice: remove Puter completely; use first-party server Whisper, then local Whisper only ----
p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
start=s.find('let puterLoaderR88=null;')
end=s.find('async function seekveraAutoTranscribe(blob){',start)
if start>=0 and end>start:
    s=s[:start]+s[end:]
pat=r"async function automaticMultilingualTranscribe\(blob\)\{.*?\n\}"
m=re.search(pat,s,re.S)
if not m:
    raise SystemExit('automaticMultilingualTranscribe block missing')
block="""async function automaticMultilingualTranscribe(blob){
  try{return await seekveraAutoTranscribe(blob)}
  catch(serverError){
    const timeout=new Promise((_,reject)=>setTimeout(()=>reject(Error('local multilingual ASR timeout')),12000));
    try{return await Promise.race([localWhisperTranscribe(blob),timeout])}catch(_){throw serverError}
  }
}"""
s=s[:m.start()]+block+s[m.end():]
s=s.replace("https://js.puter.com/v2/","")
s=s.replace("if(i)i.placeholder='Understanding your language…';","if(i)i.placeholder='Understanding speech automatically…';")
p.write_text(s,encoding='utf-8')

# ---- cache bust ----
p=Path('index.html')
h=p.read_text(encoding='utf-8')
h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
h=re.sub(r'voice-ai\.js\?v=[^"\s]+',f'voice-ai.js?v={VER}',h,count=1)
h=re.sub(r'sw\.js\?v=[^"\s]+',f'sw.js?v={VER}',h,count=1)
p.write_text(h,encoding='utf-8')

p=Path('sw.js')
sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1)
p.write_text(sw,encoding='utf-8')

print('R89 patch applied')
