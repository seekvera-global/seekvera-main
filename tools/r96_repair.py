from pathlib import Path
import re

VER='20260927-r96-authoritative-language-ai-voice'

def must_replace(path, old, new, label):
    p=Path(path); s=p.read_text(encoding='utf-8')
    if new in s:
        return
    if old not in s:
        raise SystemExit(f'{label} anchor missing in {path}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# One visible translation owner: R32. Stop R85 from translating the same DOM again.
p=Path('r85-visible-i18n.js'); s=p.read_text(encoding='utf-8')
if 'disabled-under-r32' not in s:
    anchor="  'use strict';\n"
    if anchor not in s: raise SystemExit('r85 strict anchor missing')
    s=s.replace(anchor,anchor+"  if(window.SEEKVERA_I18N_R32){window.__SEEKVERA_R85_VISIBLE_I18N='disabled-under-r32';return;}\n",1)
p.write_text(s,encoding='utf-8')

# Keep curated category data, but do not let this legacy layer rewrite the visible DOM.
p=Path('locale-r14-categories.js'); s=p.read_text(encoding='utf-8')
if 'function apply(){if(window.SEEKVERA_I18N_R32)return;' not in s:
    if 'function apply(){' not in s: raise SystemExit('category apply anchor missing')
    s=s.replace('function apply(){','function apply(){if(window.SEEKVERA_I18N_R32)return;',1)
p.write_text(s,encoding='utf-8')

# Category lock uses curated language titles and R32 descriptions; never force English or erase descriptions.
p=Path('r22-category-lock.js'); s=p.read_text(encoding='utf-8')
old="function titles(l){const d=window.SEEKVERA_R14_CATEGORIES?.data?.[l];return Array.isArray(d)&&d.length>=31?d:EN_TITLES}"
new="function titles(l){const d=window.SEEKVERA_R14_CATEGORIES?.data?.[l];return Array.isArray(d)&&d.length>=31?d:EN_TITLES.map(x=>window.SEEKVERA_I18N?.t?.(x)||x)}"
if new not in s:
    if old not in s: raise SystemExit('r22 titles anchor missing')
    s=s.replace(old,new,1)
old="  const exact=children.length===1&&bs.length===1&&bs[0].textContent.trim()===title;\n  if(exact)return;\n  const b=bs[0]||document.createElement('b');b.textContent=title;b.setAttribute('data-no-translate','1');b.setAttribute('data-no-i18n','1');body.replaceChildren(b);"
new="  const td=window.SEEKVERA_I18N?.t?.(desc)||desc;\n  const exact=children.length===2&&bs.length===1&&ss.length===1&&bs[0].textContent.trim()===title&&ss[0].textContent.trim()===td;\n  if(exact)return;\n  const b=bs[0]||document.createElement('b'),sm=ss[0]||document.createElement('small');b.textContent=title;sm.textContent=td;b.setAttribute('data-no-translate','1');b.setAttribute('data-no-i18n','1');sm.setAttribute('data-no-translate','1');sm.setAttribute('data-no-i18n','1');body.replaceChildren(b,sm);"
if new not in s:
    if old not in s: raise SystemExit('r22 description anchor missing')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# R32 source text must remain the original source forever. Late DOM mutations trigger re-apply, not re-capture.
p=Path('i18n-ui.js'); s=p.read_text(encoding='utf-8')
old="if(m.type==='characterData'){const n=m.target;if(!skipped(n)){const now=String(n.nodeValue||'').trim(),rendered=RENDERED_TEXT.get(n);if(rendered!==undefined&&now===rendered)continue;RENDERED_TEXT.delete(n);const src=canonicalText(n);if(worth(src)){SRC.set(n,src);dirty=true}}}"
new="if(m.type==='characterData'){const n=m.target;if(!skipped(n)){const now=String(n.nodeValue||'').trim(),rendered=RENDERED_TEXT.get(n);if(rendered!==undefined&&now===rendered)continue;if(SRC.has(n)){dirty=true;continue}RENDERED_TEXT.delete(n);const src=canonicalText(n);if(worth(src)){SRC.set(n,src);dirty=true}}}"
if new not in s:
    if old not in s: raise SystemExit('i18n text observer anchor missing')
    s=s.replace(old,new,1)
old="else if(m.type==='attributes'){const el=m.target,a=m.attributeName;if(el&&a&&ATTRS.includes(a)&&!el.closest?.(SKIP)){const now=String(el.getAttribute(a)||'').trim(),rendered=RENDERED_ATTR.get(el)?.[a];if(rendered!==undefined&&now===rendered)continue;const rm=RENDERED_ATTR.get(el);if(rm)delete rm[a];if(worth(now)){let mm=ATTRSRC.get(el);if(!mm){mm={};ATTRSRC.set(el,mm)}mm[a]=now;dirty=true}}}"
new="else if(m.type==='attributes'){const el=m.target,a=m.attributeName;if(el&&a&&ATTRS.includes(a)&&!el.closest?.(SKIP)){const now=String(el.getAttribute(a)||'').trim(),rendered=RENDERED_ATTR.get(el)?.[a];if(rendered!==undefined&&now===rendered)continue;const known=ATTRSRC.get(el);if(known&&known[a]){dirty=true;continue}const rm=RENDERED_ATTR.get(el);if(rm)delete rm[a];if(worth(now)){let mm=ATTRSRC.get(el);if(!mm){mm={};ATTRSRC.set(el,mm)}mm[a]=now;dirty=true}}}"
if new not in s:
    if old not in s: raise SystemExit('i18n attr observer anchor missing')
    s=s.replace(old,new,1)
s=re.sub(r"const VERSION='[^']+';",f"const VERSION='{VER}';",s,count=1)
p.write_text(s,encoding='utf-8')

# True multilingual microphone: record first, run local Whisper auto-language first; native recognizer is fallback only.
p=Path('voice-ai.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r"window\.__seekveraVoiceMode='[^']+';", "window.__seekveraVoiceMode='local-whisper-auto-first-r96';", s, count=1)
s=s.replace('const VOICE_SILENCE_MS=3600,VOICE_MAX_MS=45000,VOICE_RMS_THRESHOLD=.014;','const VOICE_SILENCE_MS=1800,VOICE_MAX_MS=45000,VOICE_RMS_THRESHOLD=.012;',1)
priority="  if(navigator.mediaDevices?.getUserMedia&&window.MediaRecorder&&!forceNative){serverVoice(targetId,activeButton,true);return}\n"
if priority not in s:
    anchor="  if(!SpeechRecognition){\n"
    if anchor not in s: raise SystemExit('voice start anchor missing')
    s=s.replace(anchor,priority+anchor,1)
s=s.replace("setTimeout(()=>reject(Error('local multilingual ASR timeout')),45000)","setTimeout(()=>reject(Error('local multilingual ASR timeout')),60000)",1)
p.write_text(s,encoding='utf-8')

# When Cloudflare AI quota is exhausted, skip the second quota-consuming model and reach free conversational fallback.
p=Path('worker-r76.js'); s=p.read_text(encoding='utf-8')
old=" }catch{}}\n // Keep a real conversational AI fallback instead of dropping immediately to fixed keyword templates."
new=" }catch(e){const em=String(e?.message||e||'');if(/daily neuron allocation|quota|limit exceeded|allocation exceeded|usage limit/i.test(em))break}}\n // Keep a real conversational AI fallback instead of dropping immediately to fixed keyword templates."
if new not in s:
    if old not in s: raise SystemExit('worker AI fallback anchor missing')
    s=s.replace(old,new,1)
s=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",s,count=1)
p.write_text(s,encoding='utf-8')

# Give the real fallback enough time to answer instead of aborting first.
p=Path('r31-ui-polish.js'); s=p.read_text(encoding='utf-8')
s=s.replace('t = setTimeout(() => c.abort(), 11000);','t = setTimeout(() => c.abort(), 18000);',1)
s=re.sub(r'const VERSION = "[^"]+";',f'const VERSION = "{VER}";',s,count=1)
p.write_text(s,encoding='utf-8')

p=Path('superapp.js'); s=p.read_text(encoding='utf-8')
s=re.sub(r'const RELEASE = "[^"]+";',f'const RELEASE = "{VER}";',s,count=1)
s=s.replace('timer=setTimeout(()=>controller.abort(),8000)','timer=setTimeout(()=>controller.abort(),18000)',1)
s=s.replace('timer=setTimeout(()=>controller.abort(),22000)','timer=setTimeout(()=>controller.abort(),18000)',1)
p.write_text(s,encoding='utf-8')

# Force browsers/service worker to fetch the repaired runtime.
assets=['locale-r15.js','i18n-ui.js','locale-r14-categories.js','r22-category-lock.js','r85-visible-i18n.js','superapp.js','voice-ai.js','r31-ui-polish.js']
for hp in Path('.').glob('*.html'):
    h=hp.read_text(encoding='utf-8')
    for name in assets:
        h=re.sub(re.escape(name)+r'\?v=[^"\s]+',name+'?v='+VER,h)
    if hp.name=='index.html':
        h=re.sub(r'data-release="[^"]+"',f'data-release="{VER}"',h,count=1)
        h=re.sub(r'sw\.js\?v=[^"\s]+','sw.js?v='+VER,h,count=1)
    hp.write_text(h,encoding='utf-8')
p=Path('sw.js'); sw=p.read_text(encoding='utf-8'); sw=re.sub(r"const RELEASE='[^']+';",f"const RELEASE='{VER}';",sw,count=1); p.write_text(sw,encoding='utf-8')

print('R96_REPAIR_APPLIED',VER)
