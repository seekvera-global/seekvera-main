from pathlib import Path

ROOT=Path('.')
OLD=['20260922-i18n-premium2','20260922-premium-r1','20260922-premium1']
NEW='20260922-final-r3'
changed=[]
for p in ROOT.glob('*.html'):
    s=p.read_text(encoding='utf-8')
    old=s
    for v in OLD:
        s=s.replace(v,NEW)
    if p.name=='hub.html':
        s=s.replace('href="entertainment.html"><span class="icon">🎮</span><b>Games</b><small>Discover games by age, device and category.</small>', 'href="games.html"><span class="icon">🎮</span><b>Games</b><small>Play 50 free racing, action, flight, adventure, puzzle and kids games.</small>')
    if p.name=='entertainment.html' and 'games.html' not in s:
        s=s.replace('</main>', '<section style="max-width:1180px;margin:16px auto;padding:0 14px"><a href="games.html" style="display:block;padding:16px;border-radius:16px;background:#112f4d;color:#fff;text-decoration:none;font-weight:900">🎮 Play 50 Free SEEKVERA Games →</a></section></main>')
    if s!=old:
        p.write_text(s,encoding='utf-8');changed.append(p.name)

sm=ROOT/'sitemap.xml'
if sm.exists():
    s=sm.read_text(encoding='utf-8')
    if 'games.html' not in s:
        entry='  <url><loc>https://seekveraglobal.com/games.html</loc></url>\n'
        s=s.replace('</urlset>',entry+'</urlset>')
        sm.write_text(s,encoding='utf-8');changed.append('sitemap.xml')

print('FINAL R3 PATCHED',len(changed),'FILES')
print('\n'.join(changed))
