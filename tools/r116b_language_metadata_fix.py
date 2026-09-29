from pathlib import Path

p=Path('worker-r76.js')
s=p.read_text(encoding='utf-8')
repls={
"if(/[ãõ]/iu.test(t)||/\\b(olá|ola|preciso|procuro|hotel|obrigado|obrigada)\\b/iu.test(s))return'pt';":"if(/[ãõ]/iu.test(t)||/\\b(olá|ola|preciso|procuro|obrigado|obrigada|aeroporto|perto)\\b/iu.test(s))return'pt';",
"if(/\\b(bonjour|salut|merci|cherche|voudrais|besoin|langue|pays|hôtel|hotel)\\b/iu.test(s))return'fr';":"if(/\\b(bonjour|salut|merci|cherche|voudrais|besoin|langue|pays|aéroport|aeroport|près)\\b/iu.test(s))return'fr';",
"if(/\\b(selamat|terima kasih|saya|ingin|cari|butuh|hotel)\\b/iu.test(s))return pick(['id','ms'],'id');":"if(/\\b(selamat|terima kasih|saya|ingin|cari|butuh|bandara|dekat)\\b/iu.test(s))return pick(['id','ms'],'id');"
}
for old,new in repls.items():
    if old in s:
        s=s.replace(old,new,1)
    elif new not in s:
        raise SystemExit('R116B language marker missing: '+old[:70])
p.write_text(s,encoding='utf-8')
print('R116B removed ambiguous Latin-language tokens')
