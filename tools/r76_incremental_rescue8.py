from __future__ import annotations
from pathlib import Path
import argparse, collections, http.cookiejar, importlib.util, json, re, time, urllib.parse, urllib.request

VER='20260926-r76-complete-global-final'
BING_LANGS={'fr','it','nl','ro','to','fy','xh','tn'}
MYMEMORY_LANGS={'sr'}
GOOGLE_LANGS={'kl'}
STATIC_LANGS={'rm'}
BAD={'[object object]','i understood your request. i’m taking you directly to the best matching section now.',"i understood your request. i'm taking you directly to the best matching section now."}
STATIC_RM={
'Job':'Plazza da lavur','New':'Nov','Boat':'Bartga','Cars':'Autos','Used':'Duvrà','1 day':'1 di','Boats':'Bartgas','China':'China','Other':'Auter','2 days':'2 dis','3 days':'3 dis','4 days':'4 dis','5 days':'5 dis','7 days':'7 dis','Arabic':'Arab','Budget':'Budget','French':'Franzos','Paused':'Pausà','Turkey':'Tirchia','Chinese':'Chinais','English':'Englais','Lebanon':'Libanon','Nigeria':'Nigeria','Premium':'Premium','Product':'Product','Service':'Servetsch','Spanish':'Spagnol','Vehicle':'Vehichel','Aircraft':'Aviun','Business':'Fatschenta','Services':'Servetschs','Equipment':'Equipament','Game Over':'Gieu finì','Mid-range':'Categoria mesauna','SAFE AUTO':'AUTO SEGIR','Any budget':'Mintga budget','Individual':'Persuna singula','Negotiable':'Negozziabel','SEEKVERA —':'SEEKVERA —','Fixed price':'Pretsch fix','Duplicate ad':'Inserat duplicà','Home & Garden':'Chasa e curtin','United States':'Stadis Unids','All categories':'Tut las categorias','Not applicable':'Betg applicabel','Sign in first.':"T'annunzia l'emprim.",'Suspected scam':'Suspect da fraud','United Kingdom':'Reginavel Unì','Wrong category':'Categoria faussa','Business Yearly':'Fatschenta annuala','Prohibited item':'Artitgel scumandà','Travel & Hotels':'Viadis e hotels','2026-09-26 · R74':'2026-09-26 · R74','Business Monthly':'Fatschenta mensila','Sports & Hobbies':'Sport e hobbis','Contact for price':'Contactar per il pretsch','Business / Company':'Fatschenta / Interpresa','Food & Restaurants':'Mangiar e restaurants','Research & shortlist':'Retschertga e selecziun','Technology & Software':'Tecnologia e software','Destination (optional)':'Destinaziun (facultativ)','Misleading information':'Infurmaziuns engianaivlas','Could not save mission.':'Impussibel da memorisar la missiun.','RFQ / supplier sourcing':"Dumonda d'offerta / tschertga da furniturs",'Server settings loaded.':'Configuraziuns dal server chargiadas.','Sending secure sign-in link…':"Trametter il link segir per s'annunziar…",'Understanding your language…':'Identifitgar tia lingua…','FULL AUTO WITH APPROVAL GATES':"COMPLET AUTOMATIC CUN CONTROLLAS D'APPROVAZIUN",'Enter the owner business email.':"Endatescha l'adressa e-mail da la fatschenta dal proprietari.",'Supplier / partnership sourcing':'Tschertga da furniturs / partenaris','Trying phone voice recognition…':'Empruvar la reconuschientscha vocala dal telefon…','· Everything you need. One search.':'· Tut quai che ti dovras. Ina tschertga.','Sector, country and goal are required.':'Sectur, pajais e finamira èn obligatoris.','Tap Play Now to continue from a new round.':"Tutscha «Giugar ussa» per cuntinuar cun ina nova runda.",'Live counts from your private Deal Agent database.':'Dumbers en temp real da tia banca da datas privata dal Deal Agent.','Mission saved as draft. No outreach has been sent.':'Missiun memorisada sco sboz. Nagina communicaziun è vegnida tramessa.','20260926-r74-global-ai-failover final deployment marker':'Marcader final da la deployaziun 20260926-r74-global-ai-failover','I did not hear speech — tap the microphone and speak again.':"Jau n'hai betg udì tia vusch — tutscha il microfon e discurra anc ina giada.",'Voice recognition failed — tap the microphone and try again.':"La reconuschientscha vocala n'ha betg funcziunà — tutscha il microfon e prova anc ina giada.",'Tap Play Now, then use ◀, ACTION and ▶ or touch the game area.':"Tutscha «Giugar ussa», lura dovra ◀, ACZIUN e ▶ u tutscha la zona dal gieu.",
'html.sv-r15-applying .r5-top,html.sv-r15-applying .r5-hero,html.sv-r15-applying .r5-chat,html.sv-r15-applying #categories{transition:none!important;animation:none!important} .sv-controls .sv-select{min-width:0;text-overflow:ellipsis}':'html.sv-r15-applying .r5-top,html.sv-r15-applying .r5-hero,html.sv-r15-applying .r5-chat,html.sv-r15-applying #categories{transition:none!important;animation:none!important} .sv-controls .sv-select{min-width:0;text-overflow:ellipsis}',
'.sv-r31-switching .r5-center,.sv-r31-switching .r5-left,.sv-r31-switching .r5-right{opacity:.12;transition:opacity .12s ease}.r5-center,.r5-left,.r5-right{transition:opacity .12s ease}.r5-thumb{overflow:hidden}.r5-thumb img{display:none!important}':'.sv-r31-switching .r5-center,.sv-r31-switching .r5-left,.sv-r31-switching .r5-right{opacity:.12;transition:opacity .12s ease}.r5-center,.r5-left,.r5-right{transition:opacity .12s ease}.r5-thumb{overflow:hidden}.r5-thumb img{display:none!important}',
'#categories .r5-tile-body{min-width:0!important;overflow:hidden!important} #categories .r5-tile-body>b,#categories .r5-tile-body>small{max-width:100%!important;overflow-wrap:anywhere!important;word-break:normal!important} #categories .r5-tile-body>small{font-weight:400!important} html,body{overflow-x:hidden!important}':'#categories .r5-tile-body{min-width:0!important;overflow:hidden!important} #categories .r5-tile-body>b,#categories .r5-tile-body>small{max-width:100%!important;overflow-wrap:anywhere!important;word-break:normal!important} #categories .r5-tile-body>small{font-weight:400!important} html,body{overflow-x:hidden!important}'
}

def load_builder():
    spec=importlib.util.spec_from_file_location('r76_builder',Path('tools/r76_build_pack.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def clean(v):
    s=str(v or '').strip();s=re.sub(r'^```(?:json|text)?\s*','',s,flags=re.I);s=re.sub(r'```$','',s).strip()
    if len(s)>=2 and s[0]==s[-1] and s[0] in ('"',"'"):s=s[1:-1].strip()
    return s

class Bing:
    def __init__(self):self.h={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36','Accept-Language':'en-US,en;q=0.9'};self.calls=0;self.refresh()
    def refresh(self):
        self.cj=http.cookiejar.CookieJar();self.op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj));html=self.op.open(urllib.request.Request('https://www.bing.com/translator',headers=self.h),timeout=25).read().decode('utf-8','replace');ig=(re.search(r'IG:"([^"]+)"',html) or re.search(r'"IG":"([^"]+)"',html));ab=re.search(r'params_AbusePreventionHelper\s*=\s*\[(\d+),"([^"]+)",(\d+)\]',html)
        if not ig or not ab:raise RuntimeError('Bing session markers missing')
        self.key,self.token,_=ab.groups();self.ig=ig.group(1);self.calls=0
    def raw(self,lang,text):
        last=None
        for attempt in range(6):
            try:
                if self.calls>=30:self.refresh()
                data=urllib.parse.urlencode({'fromLang':'en','to':lang,'text':text,'token':self.token,'key':self.key}).encode();url=f'https://www.bing.com/ttranslatev3?isVertical=1&&IG={urllib.parse.quote(self.ig)}&IID=translator.5024.1';req=urllib.request.Request(url,data=data,headers={**self.h,'Content-Type':'application/x-www-form-urlencoded','Referer':'https://www.bing.com/translator'},method='POST');d=json.loads(self.op.open(req,timeout=30).read().decode('utf-8','replace'));self.calls+=1;out=clean(d[0]['translations'][0]['text']) if isinstance(d,list) and d and d[0].get('translations') else ''
                if not out:raise RuntimeError('Bing empty')
                return out
            except Exception as e:last=e;time.sleep(1.5*(attempt+1));self.refresh()
        raise RuntimeError(f'Bing failed {lang}: {last!r}')
    def batch(self,lang,items):
        if len(items)==1:return [self.raw(lang,items[0])]
        marked=''.join(f'\n§§{i}§§\n{s}' for i,s in enumerate(items))
        try:
            out=self.raw(lang,marked);ms=list(re.finditer(r'§§\s*(\d+)\s*§§',out));vals=['']*len(items)
            if len(ms)!=len(items):raise RuntimeError('marker count')
            for j,m in enumerate(ms):idx=int(m.group(1));end=ms[j+1].start() if j+1<len(ms) else len(out);vals[idx]=clean(out[m.end():end])
            if all(vals):return vals
            raise RuntimeError('empty member')
        except Exception as e:
            print('R76_BING_SPLIT',lang,len(items),repr(e),flush=True);mid=max(1,len(items)//2);return self.batch(lang,items[:mid])+self.batch(lang,items[mid:])

def mymemory_one(lang,text):
    last=None
    for attempt in range(6):
        try:
            u='https://api.mymemory.translated.net/get?'+urllib.parse.urlencode({'q':text,'langpair':'en|'+lang});d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 SEEKVERA-R76'}),timeout=25).read().decode('utf-8','replace'));out=clean((d.get('responseData') or {}).get('translatedText'))
            if not out or out.lower()==text.lower():raise RuntimeError('empty/unchanged')
            return out
        except Exception as e:last=e;time.sleep(1.2*(attempt+1))
    raise RuntimeError(f'MyMemory failed {lang}: {last!r}')

def google_one(lang,text):
    last=None
    for client,host in [('at','translate.google.com'),('dict-chrome-ex','clients5.google.com'),('gtx','translate.googleapis.com')]:
        for attempt in range(4):
            try:
                q=urllib.parse.urlencode({'client':client,'sl':'en','tl':lang,'dt':'t','q':text});path='/translate_a/t' if host=='clients5.google.com' else '/translate_a/single';req=urllib.request.Request('https://'+host+path+'?'+q,headers={'User-Agent':'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'});d=json.loads(urllib.request.urlopen(req,timeout=25).read().decode('utf-8','replace'));out=clean(d[0] if host=='clients5.google.com' and isinstance(d,list) and d else ''.join(str(x[0] or '') for x in (d[0] if isinstance(d,list) and d else []) if isinstance(x,list)))
                if not out or out.lower()==text.lower():raise RuntimeError('empty/unchanged')
                return out
            except Exception as e:last=e;time.sleep(.8*(attempt+1))
    raise RuntimeError(f'Google failed {lang}: {last!r}')

def real_phrase(s):return len(re.findall(r"[A-Za-z][A-Za-z'’+-]{2,}",str(s)))>=2 and len(str(s).strip())>=10

def validate_new(b,lang,srcs,vals):
    if len(srcs)!=len(vals):raise RuntimeError('count mismatch')
    bad=[]
    for s,v in zip(srcs,vals):
        v=clean(v)
        if not v or not b.translation_sane(s,v) or v.lower() in BAD:bad.append((s,v))
    unchanged=[s for s,v in zip(srcs,vals) if real_phrase(s) and b.clean_text(s)==b.clean_text(v)]
    if len(unchanged)>max(8,int(len(srcs)*.18)):bad.append(('unchanged',unchanged[:8]))
    freq=collections.Counter(clean(v) for v in vals if clean(v))
    if freq and freq.most_common(1)[0][1]>max(5,int(len(vals)*.10)):bad.append(('duplicates',freq.most_common(3)))
    if bad:raise RuntimeError(f'{lang}: quality failed {bad[:8]}')

def build(lang):
    if lang not in BING_LANGS|MYMEMORY_LANGS|GOOGLE_LANGS|STATIC_LANGS:raise RuntimeError('unsupported '+lang)
    b=load_builder();src=json.loads(Path('i18n-r76-source.json').read_text());strings=src['strings'];oldp=Path('i18n-r32')/(lang+'.json');old=json.loads(oldp.read_text()) if oldp.exists() else {'translations':{}};oldt=old.get('translations') or {};translations={s:clean(oldt.get(s)) for s in strings if clean(oldt.get(s))};missing=[s for s in strings if s not in translations];vals=[];print('R76_RESCUE8',lang,'reused',len(translations),'new',len(missing),flush=True)
    if lang in STATIC_LANGS:
        provider='verified-static-rm';absent=[s for s in missing if s not in STATIC_RM]
        if absent:raise RuntimeError('missing static Romansh '+repr(absent))
        vals=[STATIC_RM[s] for s in missing]
    elif lang in BING_LANGS:
        provider='bing-web';bing=Bing()
        for start in range(0,len(missing),8):vals.extend(bing.batch(lang,missing[start:start+8]));print('R76_PROGRESS',lang,len(vals),'of',len(missing),flush=True);time.sleep(.5)
    elif lang in MYMEMORY_LANGS:
        provider='mymemory'
        for i,s in enumerate(missing,1):vals.append(mymemory_one(lang,s));print('R76_PROGRESS',lang,i,'of',len(missing),flush=True) if i%15==0 or i==len(missing) else None;time.sleep(.1)
    else:
        provider='google-at'
        for i,s in enumerate(missing,1):vals.append(google_one(lang,s));print('R76_PROGRESS',lang,i,'of',len(missing),flush=True) if i%15==0 or i==len(missing) else None;time.sleep(.1)
    validate_new(b,lang,missing,vals)
    for s,v in zip(missing,vals):translations[s]=clean(v)
    assert len(translations)==src['count']==len(strings)
    payload={'version':VER,'sourceHash':src['sourceHash'],'language':lang,'count':src['count'],'provider':'old-pack+'+provider,'translations':translations};out=Path('i18n-r76');out.mkdir(exist_ok=True);(out/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')));print('R76_RESCUE8_PASS',lang,len(translations),payload['provider'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lang',required=True);a=ap.parse_args();build(a.lang)
