from pathlib import Path

p=Path('locale-r14.js')
s=p.read_text(encoding='utf-8')
anchor="if(window.__SEEKVERA_LOCALE_R14)return;window.__SEEKVERA_LOCALE_R14=true;"
replacement=anchor+"if(window.SEEKVERA_I18N_R32){window.SEEKVERA_LOCALE_R14={apply:()=>{},schedule:()=>{},t:()=>'',languages:[],version:'r44-disabled-under-r32'};return;}"
if replacement not in s:
    if anchor not in s:
        raise SystemExit('R14 boot anchor missing')
    s=s.replace(anchor,replacement,1)
p.write_text(s,encoding='utf-8')
print('R44 legacy R14 visible-UI override disabled under R32')
