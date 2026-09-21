from pathlib import Path

app = Path('app.html')
s = app.read_text(encoding='utf-8')
s = s.replace('grid-template-columns:repeat(4,1fr)', 'grid-template-columns:repeat(5,1fr)')

if 'data-page="scan.html"' not in s:
    old = '  <button data-page="seller-plans.html">🚀 Promote / Business / Pay</button>\n</nav>'
    new = '  <button data-page="seller-plans.html">🚀 Promote / Business / Pay</button>\n  <button data-page="scan.html">📲 Scan / Share</button>\n</nav>'
    if old not in s:
        raise SystemExit('Desktop navigation marker not found')
    s = s.replace(old, new, 1)

    old = '  <button data-page="seller-plans.html"><span>🚀</span>Promote</button>\n</nav>'
    new = '  <button data-page="seller-plans.html"><span>🚀</span>Promote</button>\n  <button data-page="scan.html"><span>📲</span>Scan</button>\n</nav>'
    if old not in s:
        raise SystemExit('Mobile navigation marker not found')
    s = s.replace(old, new, 1)

if 'const scanLabels=' not in s:
    marker = '\n};\nfunction appLanguage(){'
    insert = '''
};
const scanLabels={
 en:['Scan / Share','Scan'],
 ar:['مسح / مشاركة','مسح'],
 zh:['扫码 / 分享','扫码'],
 ja:['スキャン / 共有','スキャン'],
 fr:['Scanner / Partager','Scanner'],
 es:['Escanear / Compartir','Escanear'],
 hi:['स्कैन / शेयर','स्कैन']
};
function appLanguage(){'''
    if marker not in s:
        raise SystemExit('Language block marker not found')
    s = s.replace(marker, '\n' + insert, 1)

s = s.replace("const code=appLanguage(), t=labels[code];", "const code=appLanguage(), t=labels[code], s=scanLabels[code]||scanLabels.en;")
s = s.replace("document.querySelectorAll('.nav button').forEach((b,i)=>b.textContent=['🏠 ','🛒 ','＋ ','🚀 '][i]+t[3+i]);", "document.querySelectorAll('.nav button').forEach((b,i)=>{const names=[t[3],t[4],t[5],t[6],s[0]],icons=['🏠 ','🛒 ','＋ ','🚀 ','📲 '];b.textContent=icons[i]+names[i]});")
s = s.replace("document.querySelectorAll('.bottom button').forEach((b,i)=>b.lastChild.textContent=t[7+i]);", "document.querySelectorAll('.bottom button').forEach((b,i)=>{const names=[t[7],t[8],t[9],t[10],s[1]];b.lastChild.textContent=names[i]});")
s = s.replace("promote:'seller-plans.html'};", "promote:'seller-plans.html',scan:'scan.html'};")
s = s.replace("const buildTag='20260921-voice3';", "const buildTag='20260921-scan1';")
app.write_text(s, encoding='utf-8')

scan = Path('scan.html')
t = scan.read_text(encoding='utf-8')
if 'rel="manifest"' not in t:
    t = t.replace('<link rel="canonical" href="https://seekvera-global.github.io/seekvera-main/scan.html"><link rel="icon"', '<link rel="canonical" href="https://seekvera-global.github.io/seekvera-main/scan.html"><link rel="manifest" href="manifest.webmanifest"><link rel="icon"')
if 'id="install"' not in t:
    t = t.replace('<button onclick="window.print()">🖨️ Print this poster</button><button class="dark" id="share">↗ Share SEEKVERA</button>', '<button onclick="window.print()">🖨️ Print this poster</button><button class="dark" id="install">⬇️ Install / Add to Home</button><button class="dark" id="share">↗ Share SEEKVERA</button>')
old = "<script>const url='https://seekvera-global.github.io/seekvera-main/';document.getElementById('share').onclick=async()=>{try{if(navigator.share)await navigator.share({title:'SEEKVERA',text:'Everything you need. One search.',url});else{await navigator.clipboard.writeText(url);alert('SEEKVERA link copied.')}}catch{}};document.getElementById('copy').onclick=async()=>{try{await navigator.clipboard.writeText(url);document.getElementById('copy').textContent='Copied ✓';setTimeout(()=>document.getElementById('copy').textContent='Copy link',1300)}catch{}};</script>"
new = "<script>const url='https://seekvera-global.github.io/seekvera-main/';let installPrompt=null;const installBtn=document.getElementById('install');window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installPrompt=e;installBtn.textContent='⬇️ Install SEEKVERA'});window.addEventListener('appinstalled',()=>{installPrompt=null;installBtn.textContent='Installed ✓'});installBtn.onclick=async()=>{if(installPrompt){installPrompt.prompt();try{await installPrompt.userChoice}catch{}installPrompt=null;return}alert('Open your browser menu and choose Install app or Add to Home screen.');};document.getElementById('share').onclick=async()=>{try{if(navigator.share)await navigator.share({title:'SEEKVERA',text:'Everything you need. One search.',url});else{await navigator.clipboard.writeText(url);alert('SEEKVERA link copied.')}}catch{}};document.getElementById('copy').onclick=async()=>{try{await navigator.clipboard.writeText(url);document.getElementById('copy').textContent='Copied ✓';setTimeout(()=>document.getElementById('copy').textContent='Copy link',1300)}catch{}};</script>"
if old in t:
    t = t.replace(old, new, 1)
elif 'installPrompt' not in t:
    raise SystemExit('Scan JavaScript marker not found')
scan.write_text(t, encoding='utf-8')
