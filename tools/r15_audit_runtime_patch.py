from pathlib import Path
p=Path('tools/r15_browser_audit.mjs')
s=p.read_text(encoding='utf-8')
old="await context.addInitScript(()=>{\n    localStorage.setItem('seekvera_country','WW');"
new="await context.addInitScript(()=>{\n    if(localStorage.getItem('r15_audit_seeded'))return;\n    localStorage.setItem('r15_audit_seeded','1');\n    localStorage.setItem('seekvera_country','WW');"
if old in s:
    s=s.replace(old,new,1)
old_map="""  await page.goto(BASE+'/index.html?r15map='+Date.now(),{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>SEEKVERA_LOCALE_R15?.location&&document.querySelector('#nearMe'));
  await page.click('#nearMe');
  await page.waitForSelector('#svNearMap',{state:'visible',timeout:5000});
  assert((await page.getAttribute('#svNearMap','href')).includes('google.com/maps/search'));
"""
new_map="""  await page.goto(BASE+'/index.html?r15map='+Date.now(),{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>SEEKVERA_LOCALE_R15?.location&&document.querySelector('#nearMe'));
  const located=await page.evaluate(()=>SEEKVERA_LOCALE_R15.location.locate());
  assert(Number.isFinite(located.latitude)&&Number.isFinite(located.longitude),'geolocation did not return coordinates');
  const map=await page.evaluate(c=>SEEKVERA_LOCALE_R15.location.mapUrl(c),located);
  assert(map.includes('google.com/maps/search'),'map URL helper failed');
  const beforeNear=page.url();
  await page.click('#nearMe');
  await page.waitForTimeout(250);
  const afterNear=page.url();
  if(afterNear===beforeNear){
    const link=page.locator('#svNearMap');
    assert(await link.count(),'Near Me neither navigated nor exposed map link');
  }else{
    assert(/local-services\.html|lat=|lon=/.test(afterNear),'Near Me navigated to an unexpected route: '+afterNear);
  }
"""
if old_map not in s:
    raise SystemExit('map audit anchor missing')
s=s.replace(old_map,new_map,1)
p.write_text(s,encoding='utf-8')
print('R15 audit runtime patch applied')
