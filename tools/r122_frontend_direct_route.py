from pathlib import Path
import re

VER='20260929-r122-unified-direct-routing'
VOICE_VER='20260929-r122-language-independent-voice'

# Home controller owns the visible home chat. Make server-certified direct intents navigate immediately.
p=Path('superapp.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r'const RELEASE = "[^"]+";',f'const RELEASE = "{VER}";',s,count=1)

start=s.find('  function navigateAfterReply(')
end=s.find('\n  function sameReply(',start)
if start<0 or end<0: raise SystemExit('R122 navigateAfterReply boundaries missing')
new_nav=r'''  function navigateAfterReply(route, q, category, reply = "", language = "auto") {
    if (!route || category === "general") return;
    const url =
      route +
      (route.includes("?") ? "&" : "?") +
      "q=" +
      encodeURIComponent(q) +
      "&country=" +
      encodeURIComponent(
        $("#country")?.value ||
          localStorage.getItem("seekvera_country") ||
          "WW",
      );
    clearTimeout(routeTimer);
    let done = false;
    const go = () => {
      if (done) return;
      done = true;
      clearTimeout(routeTimer);
      window.removeEventListener("seekvera:tts-start", onStart);
      window.removeEventListener("seekvera:tts-end", go);
      location.assign(url);
    };
    const voice = window.SEEKVERA_VOICE_AI?.isVoiceReplyPending?.();
    const onStart = () => setTimeout(go, 280);
    if (voice) {
      // Let speech start before routing; the R31 runtime replays it on the destination page.
      try {
        sessionStorage.setItem(
          "seekvera_route_voice",
          JSON.stringify({ text: String(reply || ""), language: String(language || "auto"), at: Date.now() }),
        );
      } catch {}
      window.addEventListener("seekvera:tts-start", onStart, { once: true });
      window.addEventListener("seekvera:tts-end", go, { once: true });
      routeTimer = setTimeout(go, 1100);
    } else routeTimer = setTimeout(go, 180);
  }'''
s=s[:start]+new_nav+s[end:]

old='''      if (!changed && explicitNavigationRequest(q))
        navigateAfterReply(route, q, finalCat);'''
new='''      const directServerIntent = d?.fastPath === "r120-direct-intent";
      if (!changed && (directServerIntent || explicitNavigationRequest(q)))
        navigateAfterReply(route, q, finalCat, reply, d.language || lang());'''
if old in s:
    s=s.replace(old,new,1)
elif 'const directServerIntent = d?.fastPath === "r120-direct-intent";' not in s:
    raise SystemExit('R122 direct navigation anchor missing')

# Faster request timeout: backend direct intents are sub-second; conversation still has room for model response.
s=s.replace('timer = setTimeout(() => controller.abort(), 7500);','timer = setTimeout(() => controller.abort(), 5200);',1)
p.write_text(s,encoding='utf-8')
print('R122 superapp patched')

# Keep version identities aligned and remove stale Android asset references.
p=Path('voice-ai.js');v=p.read_text(encoding='utf-8');v=re.sub(r"window\.__seekveraVoiceMode='[^']+'",f"window.__seekveraVoiceMode='{VOICE_VER}'",v,count=1);p.write_text(v,encoding='utf-8')
p=Path('r31-ui-polish.js');r=p.read_text(encoding='utf-8');r=re.sub(r'const VERSION = "[^"]+";',f'const VERSION = "{VER}";',r,count=1);p.write_text(r,encoding='utf-8')

# Explicitly bust the home HTML runtime references, not only worker-side rewrites.
for p in Path('.').glob('*.html'):
    if p.name.lower().startswith('google'): continue
    h=p.read_text(encoding='utf-8')
    n=re.sub(r'superapp\.js(?:\?v=[^"\'<> ]*)?',f'superapp.js?v={VER}',h)
    n=re.sub(r'r31-ui-polish\.js(?:\?v=[^"\'<> ]*)?',f'r31-ui-polish.js?v={VER}',n)
    n=re.sub(r'voice-ai\.js(?:\?v=[^"\'<> ]*)?',f'voice-ai.js?v={VOICE_VER}',n)
    if n!=h:p.write_text(n,encoding='utf-8')

p=Path('worker-r31.js');w=p.read_text(encoding='utf-8')
w=re.sub(r'superapp\\?\.js(?:\\?v=[A-Za-z0-9._-]+)?',lambda m:m.group(0),w)  # no-op; preserve worker logic
w=re.sub(r'r31-ui-polish\\.js\\?v=[A-Za-z0-9._-]+',f'r31-ui-polish.js?v={VER}',w)
w=re.sub(r'r31-ui-polish\.js\?v=[A-Za-z0-9._-]+',f'r31-ui-polish.js?v={VER}',w)
w=re.sub(r'voice-ai\\.js\\?v=[A-Za-z0-9._-]+',f'voice-ai.js?v={VOICE_VER}',w)
w=re.sub(r'voice-ai\.js\?v=[A-Za-z0-9._-]+',f'voice-ai.js?v={VOICE_VER}',w)
p.write_text(w,encoding='utf-8')

p=Path('sw.js');sw=p.read_text(encoding='utf-8');sw=re.sub(r"const CACHE='[^']+';",f"const CACHE='seekvera-r122-unified-direct-routing';",sw,count=1);p.write_text(sw,encoding='utf-8')
print('R122 cache identities patched')
