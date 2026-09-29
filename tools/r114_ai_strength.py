from pathlib import Path
import re

VER='20260929-r114-fast-strong-ai'
OLD='20260929-r113-ai-reliability'

files=['worker-r76.js','superapp.js','r31-ui-polish.js','voice-ai.js','sw.js','index.html']
if all(VER in Path(f).read_text(encoding='utf-8') for f in ['worker-r76.js','index.html']):
    print('R114 already applied')
    raise SystemExit(0)

p=Path('worker-r76.js'); s=p.read_text(encoding='utf-8')
s=s.replace(f"const RELEASE='{OLD}';",f"const RELEASE='{VER}';")
if "const FAST='@cf/meta/llama-3.1-8b-instruct-fast';" not in s:
    s=s.replace("const FALLBACK='@cf/qwen/qwen3-30b-a3b-fp8';","const FALLBACK='@cf/qwen/qwen3-30b-a3b-fp8';\nconst FAST='@cf/meta/llama-3.1-8b-instruct-fast';")
s=s.replace("env.AI.run(model,{messages,temperature:.2,max_tokens:760})","env.AI.run(model,{messages,temperature:.18,max_tokens:420})")
s=s.replace("Promise.any([PRIMARY,FALLBACK].map(modelAttempt))","Promise.any([FAST,PRIMARY,FALLBACK].map(modelAttempt))")
s=s.replace("'r113-verified-action-first'","'r114-verified-action-first'")
s=s.replace("'r113-meta-conversation-guard'","'r114-meta-conversation-guard'")
s=s.replace("'r113-bounded-structured-ai'","'r114-fast-model-race'")
s=s.replace("'seekvera-r113-instant-local-fallback'","'seekvera-r114-instant-local-fallback'")
s=s.replace("'r113-bounded-fallback'","'r114-bounded-fallback'")
s=s.replace("'r113-real-ai-fallback'","'r114-real-ai-fallback'")
s=s.replace("'r113-natural-plain-fallback'","'r114-natural-plain-fallback'")
p.write_text(s,encoding='utf-8')

for name in ['superapp.js','r31-ui-polish.js','voice-ai.js','sw.js','index.html']:
    p=Path(name); s=p.read_text(encoding='utf-8').replace(OLD,VER); p.write_text(s,encoding='utf-8')
print('R114 patched')
