(()=>{
  const SLOGANS={
    en:'Find faster. Compare better.',
    ar:'ابحث أسرع. قارن أفضل.',
    fr:'Trouvez plus vite. Comparez mieux.',
    zh:'更快找到，更好比较。',
    es:'Encuentra más rápido. Compara mejor.',
    hi:'जल्दी खोजें। बेहतर तुलना करें।',
    pt:'Encontre mais rápido. Compare melhor.',
    de:'Schneller finden. Besser vergleichen.',
    ja:'もっと速く探して、もっと良く比較。',
    ko:'더 빠르게 찾고, 더 잘 비교하세요.',
    id:'Temukan lebih cepat. Bandingkan lebih baik.',
    tr:'Daha hızlı bul. Daha iyi karşılaştır.',
    ru:'Находите быстрее. Сравнивайте лучше.',
    ur:'تیزی سے تلاش کریں۔ بہتر موازنہ کریں۔',
    bn:'দ্রুত খুঁজুন। ভালোভাবে তুলনা করুন।',
    vi:'Tìm nhanh hơn. So sánh tốt hơn.',
    it:'Trova più velocemente. Confronta meglio.',
    sw:'Pata haraka. Linganisha vizuri.',
    th:'ค้นหาเร็วขึ้น เปรียบเทียบได้ดีกว่า',
    fa:'سریع‌تر پیدا کنید. بهتر مقایسه کنید.',
    pl:'Znajdź szybciej. Porównaj lepiej.',
    nl:'Vind sneller. Vergelijk beter.',
    ms:'Cari lebih cepat. Bandingkan lebih baik.',
    fil:'Mas mabilis maghanap. Mas mahusay maghambing.',
    ha:'Nemo da sauri. Kwatanta da kyau.',
    yo:'Wa kíákíá. Ṣe àfiwé dáadáa.',
    ig:'Chọta ngwa ngwa. Tụnyere nke ọma.',
    am:'በፍጥነት ያግኙ። በተሻለ ያነፃፅሩ።'
  };
  const DIR_RTL=new Set(['ar','ur','fa']);
  function langCode(){
    const sel=document.querySelector('#lang');
    let raw=String(sel?.value||document.documentElement.lang||navigator.language||'en').toLowerCase();
    if(raw==='auto') raw=String(document.documentElement.lang||navigator.language||'en').toLowerCase();
    return raw.split('-')[0]||'en';
  }
  function apply(){
    const lang=langCode();
    const h=document.querySelector('.r5-hero h1');
    if(h){
      h.textContent=SLOGANS[lang]||SLOGANS.en;
      h.setAttribute('lang',lang);
      h.setAttribute('dir',DIR_RTL.has(lang)?'rtl':'auto');
    }
  }
  function schedule(){apply();setTimeout(apply,40);setTimeout(apply,180);setTimeout(apply,500)}
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',schedule,{once:true}); else schedule();
  document.addEventListener('change',e=>{if(e.target&&e.target.id==='lang') schedule()});
  window.addEventListener('pageshow',schedule);
  window.addEventListener('seekvera:languagechange',schedule);
})();
