from __future__ import annotations
from pathlib import Path
import argparse, importlib.util, json

VER='20260926-r76-complete-global-final'

def load_builder():
    spec=importlib.util.spec_from_file_location('r76_builder',Path('tools/r76_build_pack.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def translate_small(b,lang,items):
    if not items:return []
    try:return b.google_translate(lang,items),'google-html'
    except Exception as e:
        print('R76_SMALL_GOOGLE_FALLBACK',lang,repr(e),flush=True)
        return b.pollinations_translate(lang,items),'public-ai'

def build(lang:str):
    b=load_builder();src=json.loads(Path('i18n-r76-source.json').read_text(encoding='utf-8'));strings=src['strings']
    oldp=Path('i18n-r32')/(lang+'.json');old=json.loads(oldp.read_text(encoding='utf-8')) if oldp.exists() else {'translations':{}};oldt=old.get('translations') or {}
    translations={s:str(oldt.get(s,'')).strip() for s in strings if str(oldt.get(s,'')).strip()}
    missing=[s for s in strings if s not in translations]
    print('R76_INCREMENTAL2',lang,'reused',len(translations),'new',len(missing),'total',len(strings),flush=True)
    providers=['old-pack']
    if lang=='en':
        for s in missing:translations[s]=s
    else:
        vals,provider=translate_small(b,lang,missing);providers.append(provider)
        assert len(vals)==len(missing),(lang,len(vals),len(missing))
        for s,v in zip(missing,vals):
            v=str(v).strip()
            if not v or not b.translation_sane(s,v):raise RuntimeError(f'{lang}: bad new translation {s!r}')
            translations[s]=v
        # Repair only required UI phrases that are still English; never retranslate the whole old pack.
        forced=[s for s in b.FORCE_UI if s in translations and b.clean_text(translations[s])==b.clean_text(s)]
        if forced:
            vals2,provider2=translate_small(b,lang,forced);providers.append(provider2)
            for s,v in zip(forced,vals2):
                v=str(v).strip()
                if v and b.translation_sane(s,v):translations[s]=v
    assert len(translations)==src['count']==len(strings),(lang,len(translations),src['count'])
    forced=[s for s in b.FORCE_UI if s in translations and b.clean_text(translations[s])==b.clean_text(s)] if lang!='en' else []
    if forced:raise RuntimeError(f'{lang}: forced UI still English {forced[:8]}')
    payload={'version':VER,'sourceHash':src['sourceHash'],'language':lang,'count':src['count'],'provider':'+'.join(dict.fromkeys(providers)),'translations':translations}
    out=Path('i18n-r76');out.mkdir(exist_ok=True);(out/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('R76_INCREMENTAL2_PASS',lang,len(translations),payload['provider'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();build(a.lang)
