from pathlib import Path
import re
VER='20260927-r91-true-language-autodetect'

p=Path('voice-ai.js')
s=p.read_text(encoding='utf-8')
s=s.replace("/patched-transformers.js?v=20260927-r90-local-multilingual-voice","/patched-transformers-r91.js?v="+VER)
s=s.replace("'Xenova/whisper-tiny'","'onnx-community/whisper-tiny'")
# v4 bundle carries its own matching ORT dependency; use its configured CDN defaults.
s=s.replace("    mod.env.backends.onnx.wasm.wasmPaths='https://cdn.jsdelivr.net/npm/onnxruntime-web@1.25.0-dev.20260212-1a71a5f46e/dist/';\n","")
p.write_text(s,encoding='utf-8')

p=Path('index.html');h=p.read_text(encoding='utf-8')
h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
h=re.sub(r'voice-ai\.js\?v=[^"\s]+',f'voice-ai.js?v={VER}',h,count=1)
h=re.sub(r'sw\.js\?v=[^"\s]+',f'sw.js?v={VER}',h,count=1)
p.write_text(h,encoding='utf-8')

p=Path('sw.js');sw=p.read_text(encoding='utf-8')
sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1)
p.write_text(sw,encoding='utf-8')
print('R91 source pointers updated')
