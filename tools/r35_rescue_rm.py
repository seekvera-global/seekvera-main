from __future__ import annotations
from pathlib import Path
import json,re,sys
from r35_build_pack import source_meta, FORCE_UI, clean_text

OUT=Path('i18n-r35'); OUT.mkdir(exist_ok=True)
VERSION='20260925-r35-static-v3'
CODE=(sys.argv[1] if len(sys.argv)>1 else 'rm').lower()
MODELS={'rm':('Helsinki-NLP/opus-mt-en-roa','>>roh<< '),'tn':('Helsinki-NLP/opus-mt-en-tn','')}
if CODE not in MODELS: raise SystemExit('Rescue supports rm or tn')

MANUALS={
'rm':{
'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'Actualmain na datti naginas glistas approvadas e disponiblas sin il martgà. SEEKVERA na generescha betg glistas faussas.',
'No approved live marketplace listings are available right now.':'Actualmain na datti naginas glistas approvadas e disponiblas sin il martgà.',
'SEEKVERA does not generate fake listings.':'SEEKVERA na generescha betg glistas faussas.',
'Find, compare, choose — worldwide.':'Tschertga, cumpareglia, tscherna — en tut il mund.','Find, compare, choose — worldwide':'Tschertga, cumpareglia, tscherna — en tut il mund',
'Popular categories':'Categorias popularas','Live marketplace':'Martgà actual','Request anything':'Dumonda tut','Privacy':'Protecziun da datas','Terms':'Cundiziuns','Contact':'Contact','Disclosure':'Decleraziun','Approved real listings only.':'Mo glistas realas approvadas.','Loading approved listings…':'Chargiar glistas approvadas…'},
'tn':{
'No approved live marketplace listings are available right now. SEEKVERA does not generate fake listings.':'Ga go na mananeo a a amogetsweng a mmaraka a a leng teng gone jaanong. SEEKVERA ga e dire mananeo a maaka.',
'No approved live marketplace listings are available right now.':'Ga go na mananeo a a amogetsweng a mmaraka a a leng teng gone jaanong.','SEEKVERA does not generate fake listings.':'SEEKVERA ga e dire mananeo a maaka.',
'Find, compare, choose — worldwide.':'Batla, bapisa, tlhopha — lefatshe ka bophara.','Find, compare, choose — worldwide':'Batla, bapisa, tlhopha — lefatshe ka bophara',
'Popular categories':'Dikarolo tse di tumileng','Live marketplace':'Mmaraka o o dirang','Request anything':'Kopa sengwe le sengwe','Privacy':'Bosephiri','Terms':'Melawana','Contact':'Ikgolaganye','Disclosure':'Tshedimosetso','Approved real listings only.':'Mananeo a nnete a a amogetsweng fela.','Loading approved listings…':'Go tsenngwa mananeo a a amogetsweng…'}
}
MANUAL=MANUALS[CODE]

def main():
    import torch
    from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
    src,h=source_meta();model_id,prefix=MODELS[CODE]
    print('R35 OFFLINE RARE SOURCE',CODE,len(src),h,model_id,flush=True)
    tok=AutoTokenizer.from_pretrained(model_id)
    model=AutoModelForSeq2SeqLM.from_pretrained(model_id);model.eval()
    vals=[];bs=24
    with torch.inference_mode():
        for i in range(0,len(src),bs):
            batch=src[i:i+bs]
            enc=tok([prefix+s for s in batch],return_tensors='pt',padding=True,truncation=True,max_length=256)
            out=model.generate(**enc,max_new_tokens=256,num_beams=2)
            vals.extend(clean_text(x) for x in tok.batch_decode(out,skip_special_tokens=True))
            print('R35 OFFLINE RARE PROGRESS',CODE,min(i+bs,len(src)),'/',len(src),flush=True)
    assert len(vals)==len(src),(CODE,len(vals),len(src))
    trans={s:v for s,v in zip(src,vals)}
    for s,v in MANUAL.items():
        if s in trans:trans[s]=v
    # Never allow the brand name to disappear. For a brand-bearing line, English is safer than a corrupted brand.
    for s in src:
        if 'SEEKVERA' in s and 'SEEKVERA' not in trans.get(s,''):trans[s]=s
    failed=[s for s in FORCE_UI if s in trans and clean_text(trans[s])==clean_text(s) and not (CODE=='rm' and s=='Contact')]
    assert not failed,(CODE,'critical unchanged',failed)
    long=[s for s in src if len(s)>=14 and 'SEEKVERA' not in s and re.search(r'[A-Za-z]',s) and ' ' in s]
    same=[s for s in long if clean_text(trans.get(s,''))==clean_text(s)]
    assert len(same)<=max(25,int(len(long)*.18)),(CODE,'too many unchanged',len(same),same[:10])
    payload={'version':VERSION,'sourceHash':h,'language':CODE,'count':len(src),'provider':'offline-huggingface-opus','translations':trans}
    p=OUT/f'{CODE}.json';p.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('R35 OFFLINE RARE PACK PASS',CODE,len(src),'unchanged-long',len(same),p,flush=True)

if __name__=='__main__':main()
