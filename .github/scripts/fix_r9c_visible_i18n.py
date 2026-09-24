from pathlib import Path

p = Path('i18n-ui.js')
s = p.read_text(encoding='utf-8')

marker = "};\nfunction api(path){return location.hostname==='seekveraglobal.com'"
replacement = "};\nwindow.__SEEKVERA_R9_QUICK=QUICK;\nfunction api(path){return location.hostname==='seekveraglobal.com'"
if 'window.__SEEKVERA_R9_QUICK=QUICK;' not in s:
    if marker not in s:
        raise SystemExit('R9 QUICK marker not found')
    s = s.replace(marker, replacement, 1)

old_local = "function local(l,s){return DICTS[l]?.[norm(s)]||''}"
new_local = "function local(l,s){const k=norm(s);return DICTS[l]?.[k]||window.__SEEKVERA_R9_QUICK?.[l]?.[k]||''}"
if old_local in s:
    s = s.replace(old_local, new_local, 1)
elif new_local not in s:
    raise SystemExit('legacy local() function not found')

old_apply = "async function apply(){const token=++runToken,l=currentLang();applying=true;setDirection(l);applyControlLabels(l);const pending=captureAndApply(l);document.body?.classList.add('sv-i18n-ready');applying=false;if(l!=='en'&&pending.length)aiTranslate(l,pending,token)}"
new_apply = "async function apply(){const token=++runToken,l=currentLang();applying=true;setDirection(l);applyControlLabels(l);const pending=captureAndApply(l);document.body?.classList.add('sv-i18n-ready');applying=false;window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(40);if(l!=='en'&&pending.length){await aiTranslate(l,pending,token);window.SEEKVERA_LOCALE_GUARD_R9?.schedule?.(60)}}"
if old_apply in s:
    s = s.replace(old_apply, new_apply, 1)
elif new_apply not in s:
    raise SystemExit('legacy apply() function not found')

p.write_text(s, encoding='utf-8')

# Bump the cache query everywhere the localized runtime is loaded.
for h in Path('.').glob('*.html'):
    t = h.read_text(encoding='utf-8')
    if 'i18n-ui.js?v=20260924-final-r9b' in t:
        t = t.replace('i18n-ui.js?v=20260924-final-r9b', 'i18n-ui.js?v=20260924-final-r9c')
        h.write_text(t, encoding='utf-8')

# Update service worker references/cache marker where present.
sw = Path('sw.js')
if sw.exists():
    t = sw.read_text(encoding='utf-8')
    t = t.replace('seekvera-final-r9b-20260924', 'seekvera-final-r9c-20260924')
    t = t.replace('i18n-ui.js?v=20260924-final-r9b', 'i18n-ui.js?v=20260924-final-r9c')
    t = t.replace('voice-ai.js?v=20260924-final-r9b', 'voice-ai.js?v=20260924-final-r9c')
    sw.write_text(t, encoding='utf-8')

# Keep voice source unchanged, but bump query on pages so phone caches cannot hold R9b.
for h in Path('.').glob('*.html'):
    t = h.read_text(encoding='utf-8')
    if 'voice-ai.js?v=20260924-final-r9b' in t:
        t = t.replace('voice-ai.js?v=20260924-final-r9b', 'voice-ai.js?v=20260924-final-r9c')
        h.write_text(t, encoding='utf-8')

print('R9c unified visible translation patch applied')
