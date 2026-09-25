from pathlib import Path

p=Path('worker.js')
s=p.read_text(encoding='utf-8')
marker="pollinations-private-backup"
if marker not in s:
    old="}throw Error(errors.join(' | '))}"
    new="""}try{const backupPrompt=(messages||[]).map(x=>String(x?.role||'user').toUpperCase()+': '+String(x?.content||'')).join('\\n').slice(-3600),backupUrl='https://text.pollinations.ai/'+encodeURIComponent(backupPrompt)+'?model=openai&private=true',signal=(typeof AbortSignal!=='undefined'&&AbortSignal.timeout)?AbortSignal.timeout(10000):undefined,br=await fetch(backupUrl,{headers:{'accept':'text/plain','user-agent':'SEEKVERA/1.0'},...(signal?{signal}:{})});if(br.ok){const bs=clean(await br.text(),5000);if(bs)return{response:bs,model:'pollinations-private-backup'}}errors.push('pollinations:'+br.status)}catch(e){errors.push('pollinations:'+clean(e?.message||e,180))}throw Error(errors.join(' | '))}"""
    if old not in s:
        raise SystemExit('AI terminal throw anchor missing')
    s=s.replace(old,new,1)

# Keep the fallback private/no-cache and identifiable in health metadata.
old="voiceRuntime:'native-plus-server-asr-v1',voiceInputFallback:'server-asr-v1'"
new="voiceRuntime:'native-plus-server-asr-v1',voiceInputFallback:'server-asr-v1',aiBackup:'pollinations-private-backup'"
if old in s:
    s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

s=p.read_text(encoding='utf-8')
assert "model:'pollinations-private-backup'" in s
assert "?model=openai&private=true" in s
assert "AbortSignal.timeout(10000)" in s
print('R25 AI resilience patch PASS')
