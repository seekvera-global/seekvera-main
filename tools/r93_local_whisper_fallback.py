from pathlib import Path
import re

VER='20260927-r93-free-local-whisper'

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r"import\('/patched-transformers(?:-r91)?\.js\?v=[^']+'\)",f"import('/patched-transformers-r93.js?v={VER}')",s,count=1)
s=s.replace("'Xenova/whisper-tiny'","'onnx-community/whisper-tiny'")
s=s.replace("'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.25.0-dev.20260212-1a71a5f46e/dist/'","'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.31.0-dev.20260914-8d85527a0/dist/'")
if "onnxruntime-web@1.31.0-dev.20260914-8d85527a0" not in s:
    anchor="    mod.env.useBrowserCache=true;\n"
    if anchor not in s: raise SystemExit('R93 browser cache anchor missing')
    s=s.replace(anchor,anchor+"    mod.env.backends.onnx.wasm.wasmPaths='https://cdn.jsdelivr.net/npm/onnxruntime-web@1.31.0-dev.20260914-8d85527a0/dist/';\n",1)
# Keep local multilingual Whisper as the first path so Cloudflare free quota exhaustion never blocks the user.
pat=r"async function automaticMultilingualTranscribe\(blob\)\{.*?\n\}"
m=re.search(pat,s,re.S)
if not m: raise SystemExit('R93 multilingual transcribe block missing')
block="""async function automaticMultilingualTranscribe(blob){
  let localError=null;
  try{
    const timeout=new Promise((_,reject)=>setTimeout(()=>reject(Error('local multilingual ASR timeout')),60000));
    return await Promise.race([localWhisperTranscribe(blob),timeout])
  }catch(e){localError=e}
  try{return await seekveraAutoTranscribe(blob)}catch(serverError){throw localError||serverError}
}"""
s=s[:m.start()]+block+s[m.end():]
p.write_text(s,encoding='utf-8')

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
print('R93 local Whisper fallback pointers updated')
