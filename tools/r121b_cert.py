import json,time,urllib.request,re,base64
B='https://seekveraglobal.com'
UA='Mozilla/5.0 (Linux; Android 11; SM-A225F) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36'

def post(path,obj,timeout=7,accept='application/json'):
    raw=json.dumps(obj,ensure_ascii=False).encode()
    req=urllib.request.Request(B+path,data=raw,headers={'content-type':'application/json','accept':accept,'user-agent':UA},method='POST')
    t=time.monotonic()
    with urllib.request.urlopen(req,timeout=timeout) as r:return r.read(),dict(r.headers),time.monotonic()-t

def ai(msg):
    raw,_,sec=post('/api/ai',{'message':msg,'country':'Worldwide','language':'auto','fast':True},6)
    return json.loads(raw),sec

actions=[
 ('ar','دوريني على شغل','jobs'),('en','Find me a job','jobs'),('fr','Trouve-moi un hôtel','travel'),
 ('es','Búscame un coche','cars'),('de','Finde mir eine Wohnung','property'),('tr','Bana bir iş bul','jobs'),
 ('pt','Procure um hotel para mim','travel'),('it','Trova un lavoro per me','jobs'),('vi','Tìm việc làm cho tôi','jobs'),
 ('id','Carikan pekerjaan untuk saya','jobs'),('sw','Tafuta kazi kwa ajili yangu','jobs'),('ru','Найди мне работу','jobs'),
 ('zh','帮我找一份工作','jobs'),('ja','仕事を探して','jobs'),('ko','일자리를 찾아줘','jobs'),('hi','मेरे लिए नौकरी खोजो','jobs'),
 ('bn','আমার জন্য চাকরি খুঁজে দিন','jobs'),('fa','برای من کار پیدا کن','jobs'),('ur','میرے لیے نوکری تلاش کرو','jobs')]
for code,msg,cat in actions:
    d,sec=ai(msg)
    assert d.get('ok') and d.get('language')==code,(code,msg,d)
    assert d.get('category')==cat,(code,msg,cat,d)
    assert sec<2.2,(code,msg,sec,d)
    print('ACTION_PASS',code,cat,round(sec,2),d.get('model'))

d,sec=ai('حوليني على تركيا');a=d.get('countryAction') or {}
assert d.get('language')=='ar' and a.get('type')=='set-country' and a.get('code')=='TR',d
assert sec<2.2,(sec,d)
print('CONTROL_PASS',round(sec,2),d.get('model'))

chats=[
 ('ar','مرحبا كيفك؟',r'[\u0600-\u06ff]'),('en','Hello, how are you?',r'[A-Za-z]'),('fr','Bonjour, comment allez-vous ?',r'[A-Za-zÀ-ÿ]'),
 ('tr','Merhaba, nasılsın?',r'[A-Za-zÇĞİÖŞÜçğıöşü]'),('ru','Привет, как дела?',r'[\u0400-\u052f]'),('hi','नमस्ते, आप कैसे हैं?',r'[\u0900-\u097f]'),
 ('zh','你好，你好吗？',r'[\u4e00-\u9fff]'),('ja','こんにちは。元気ですか？',r'[\u3040-\u30ff\u4e00-\u9fff]')]
for code,msg,pat in chats:
    d,sec=ai(msg);text=str(d.get('response',''))
    assert d.get('ok') and d.get('language')==code,(code,d)
    assert d.get('category')=='general',(code,d)
    assert re.search(pat,text),(code,text,d)
    assert sec<5.0,(code,sec,d)
    print('CHAT_PASS',code,round(sec,2),d.get('model'))

phrase='مرحبا دوريني على شغل في بيروت'
audio,_,_=post('/api/tts',{'text':phrase,'language':'ar'},10,'audio/mpeg,audio/*;q=0.9,*/*;q=0.8')
assert len(audio)>500
payload={'audio':'data:audio/mpeg;base64,'+base64.b64encode(audio).decode(),'language':'auto','languageHint':'en','uiLanguage':'en','browserLanguage':'en-US','nativeText':'Halið á að leita að vinnu','nativeConfidence':0.97}
raw,_,sec=post('/api/transcribe?r121b=1',payload,9)
d=json.loads(raw)
assert d.get('ok') and d.get('language')=='ar',d
assert re.search(r'[\u0600-\u06ff]',str(d.get('text',''))),d
assert sec<6.5,(sec,d)
print('AR_AUDIO_PASS',round(sec,2),d.get('model'),d.get('text'))
