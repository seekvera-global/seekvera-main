from pathlib import Path
import re

p = Path('worker.js')
s = p.read_text(encoding='utf-8')

fn = r'''async function runVision(env,input){
 const errors=[],image=input?.image,messages=Array.isArray(input?.messages)?input.messages:[];
 const multimodal=async(model)=>{const mm=messages.map(m=>({...m}));let i=-1;for(let n=mm.length-1;n>=0;n--)if(mm[n]?.role==='user'){i=n;break}if(i<0){mm.push({role:'user',content:'Review this image.'});i=mm.length-1}const text=typeof mm[i].content==='string'?mm[i].content:'Review this image.';mm[i]={...mm[i],content:[{type:'text',text},{type:'image_url',image_url:{url:image}}]};return env.AI.run(model,{messages:mm,max_completion_tokens:Math.min(Number(input?.max_tokens)||140,220),temperature:Number(input?.temperature)||0})};
 const attempt=async(label,fn)=>{try{const r=await fn(),text=out(r);if(text)return r;errors.push(label+':empty');return null}catch(e){errors.push(label+':'+clean(e?.message||e,220));return null}};
 if(image){
  let r=await attempt(VISION+':multimodal',()=>multimodal(VISION));if(r)return r;
  r=await attempt(VISION+':top-level-image',()=>env.AI.run(VISION,{messages,image,max_completion_tokens:Math.min(Number(input?.max_tokens)||140,220),temperature:Number(input?.temperature)||0}));if(r)return r;
  r=await attempt(VISION_FALLBACK+':multimodal',()=>multimodal(VISION_FALLBACK));if(r)return r;
  r=await attempt(VISION_FALLBACK+':top-level-image',()=>env.AI.run(VISION_FALLBACK,{messages,image,max_completion_tokens:Math.min(Number(input?.max_tokens)||140,220),temperature:Number(input?.temperature)||0}));if(r)return r;
 }
 const r=await attempt(VISION+':plain',()=>env.AI.run(VISION,{...input,max_completion_tokens:Math.min(Number(input?.max_tokens)||140,220)}));if(r)return r;
 throw Error(errors.join(' | '))
}'''

s2, n = re.subn(
    r"async function runVision\(env,input\)\{.*?\}\nasync function vision",
    lambda m: fn + '\nasync function vision',
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit('runVision patch target not found')

p.write_text(s2, encoding='utf-8')
print('patched runVision empty-response fallback')
