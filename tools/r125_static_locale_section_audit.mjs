import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const BASE = process.env.SEEKVERA_BASE_URL || 'https://seekveraglobal.com';
const RELEASE = '20260926-r76-complete-global-final';
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

const browser = await chromium.launch({ headless: true });
try {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    locale: 'en-US',
    serviceWorkers: 'block',
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36'
  });
  context.setDefaultTimeout(20000);

  const blocked = { ai: [], translation: [], pollinations: [] };
  await context.route('**/api/ai**', async route => {
    blocked.ai.push({ url: route.request().url(), method: route.request().method() });
    await route.fulfill({ status: 503, contentType: 'application/json', body: '{"ok":false,"audit":"quota-neutral-static-only"}' });
  });
  await context.route('**/api/ui-translate**', async route => {
    blocked.translation.push({ url: route.request().url(), method: route.request().method() });
    await route.fulfill({ status: 503, contentType: 'application/json', body: '{"ok":false,"audit":"static-pack-only"}' });
  });
  await context.route('https://text.pollinations.ai/**', async route => {
    blocked.pollinations.push(route.request().url());
    await route.fulfill({ status: 503, contentType: 'text/plain', body: 'quota-neutral static audit' });
  });

  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));

  const homeResponse = await page.goto(BASE + '/?r125static=' + Date.now(), {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });
  assert(homeResponse && homeResponse.status() === 200, 'homepage HTTP status');
  await page.waitForFunction(
    () => window.SEEKVERA_LOCALE_R15 && window.SEEKVERA_I18N_R32,
    { timeout: 30000 }
  );

  const manifestResponse = await context.request.get(BASE + '/i18n-r32/manifest.json?v=' + Date.now());
  const sourceResponse = await context.request.get(BASE + '/i18n-r32-source.json?v=' + Date.now());
  assert.equal(manifestResponse.status(), 200, 'locale manifest HTTP status');
  assert.equal(sourceResponse.status(), 200, 'locale source HTTP status');
  const manifest = await manifestResponse.json();
  const source = await sourceResponse.json();

  assert.equal(manifest.version, RELEASE, 'live locale release version');
  assert.equal(manifest.packs, 98, 'manifest pack count');
  assert.equal(manifest.languages.length, 98, 'manifest language count');
  assert.equal(new Set(manifest.languages).size, 98, 'unique manifest language codes');
  assert.equal(source.count, source.strings.length, 'source count');
  assert.equal(source.sourceHash, manifest.sourceHash, 'source/manifest hash');
  assert.equal(new Set(source.strings).size, source.count, 'unique source strings');
  assert(source.count >= 1000, 'source inventory unexpectedly small');

  const sourceKeys = source.strings;
  const sourceSet = new Set(sourceKeys);
  const packs = {};
  for (let i = 0; i < manifest.languages.length; i += 14) {
    const batch = manifest.languages.slice(i, i + 14);
    await Promise.all(batch.map(async language => {
      const response = await context.request.get(
        BASE + '/i18n-r32/' + language + '.json?v=' + manifest.sourceHash,
        { timeout: 30000 }
      );
      assert.equal(response.status(), 200, language + ' pack HTTP status');
      const data = await response.json();
      assert.equal(data.count, source.count, language + ' pack count');
      assert.equal(data.sourceHash, manifest.sourceHash, language + ' source hash');
      const translations = data.translations;
      assert(translations && typeof translations === 'object' && !Array.isArray(translations), language + ' translations object');
      const actualKeys = Object.keys(translations);
      assert.equal(actualKeys.length, source.count, language + ' exact key count');
      const missing = sourceKeys.filter(key => !Object.hasOwn(translations, key));
      const extra = actualKeys.filter(key => !sourceSet.has(key));
      const empty = sourceKeys.filter(key => typeof translations[key] !== 'string' || !translations[key].trim());
      assert.equal(missing.length, 0, language + ' missing keys');
      assert.equal(extra.length, 0, language + ' extra keys');
      assert.equal(empty.length, 0, language + ' empty/non-string values');
      packs[language] = translations;
    }));
    console.log('R125_STATIC_PACK_PROGRESS', Math.min(i + 14, 98), '/ 98');
  }

  const countryMatrix = await page.evaluate(async () => {
    const profiles = window.SEEKVERA_LOCALE_R15.profiles || {};
    const countryElement = document.getElementById('country') || document.querySelector('[name="country"]');
    const languageElement = document.getElementById('lang') || document.querySelector('[name="lang"]');
    const currencyElement = document.getElementById('currency') || document.querySelector('[name="currency"]');
    const failures = [];
    for (const [code, profile] of Object.entries(profiles)) {
      window.SEEKVERA_LOCALE_R15.setCountry(code);
      await new Promise(resolve => setTimeout(resolve, 5));
      const actual = {
        country: countryElement?.value,
        language: languageElement?.value,
        currency: currencyElement?.value,
        htmlLanguage: document.documentElement.lang
      };
      if (
        actual.country !== code ||
        actual.language !== profile.language ||
        actual.currency !== profile.currency ||
        actual.htmlLanguage !== profile.language
      ) failures.push({ code, expected: profile, actual });
    }
    return { count: Object.keys(profiles).length, failures };
  });
  assert(countryMatrix.count >= 248, 'country profile coverage below 248: ' + countryMatrix.count);
  assert.equal(countryMatrix.failures.length, 0, 'country/language/currency synchronization: ' + JSON.stringify(countryMatrix.failures.slice(0, 8)));
  console.log('R125_STATIC_COUNTRY_MATRIX_PASS', countryMatrix.count);

  const hrefs = await page.evaluate(() => [
    ...new Set([...document.querySelectorAll('#categories .r5-tile')]
      .map(anchor => anchor.getAttribute('href'))
      .filter(Boolean))
  ]);
  assert(hrefs.length >= 31, 'category route links below expected minimum: ' + hrefs.length);
  const paths = [...new Set(hrefs.map(href => new URL(href, BASE).pathname))];
  assert(paths.length >= 25, 'unique section paths below expected minimum: ' + paths.length);

  const candidateEnglish = sourceKeys.filter(value =>
    value.length >= 12 &&
    (value.match(/[A-Za-z][A-Za-z'’+-]{2,}/g) || []).length >= 2 &&
    !value.includes('SEEKVERA') &&
    !/https?:\/\/|@/.test(value)
  );
  const leakFindings = [];
  let languageApplications = 0;
  let sectionLanguageApplications = 0;

  await page.goto(BASE + '/?r125static-home=' + Date.now(), { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForFunction(() => window.SEEKVERA_LOCALE_R15 && window.SEEKVERA_I18N_R32, { timeout: 30000 });
  await page.evaluate(() => window.SEEKVERA_LOCALE_R15.setLanguage('en'));
  await pause(50);
  const homeEnglish = await page.locator('body').innerText();
  const homePresent = candidateEnglish.filter(value => homeEnglish.includes(value));

  for (let index = 0; index < manifest.languages.length; index++) {
    const language = manifest.languages[index];
    await page.evaluate(async code => {
      window.SEEKVERA_LOCALE_R15.setLanguage(code);
      await window.SEEKVERA_I18N_R32.loadPack(code);
      await window.SEEKVERA_I18N_R32.apply();
    }, language);
    const state = await page.evaluate(() => ({
      language: document.documentElement.lang,
      direction: document.documentElement.dir
    }));
    assert.equal(state.language, language, 'homepage language application: ' + language);
    languageApplications++;
    if (language !== 'en') {
      const body = await page.locator('body').innerText();
      const leaks = homePresent.filter(value =>
        typeof packs[language]?.[value] === 'string' &&
        body.includes(value)
      ).slice(0, 6);
      if (leaks.length) leakFindings.push({ path: '/', language, leaks });
    }
    if ((index + 1) % 14 === 0 || index === manifest.languages.length - 1) {
      console.log('R125_STATIC_HOME_LANGUAGE_PROGRESS', index + 1, '/ 98');
    }
  }

  for (let pathIndex = 0; pathIndex < paths.length; pathIndex++) {
    const path = paths[pathIndex];
    const response = await page.goto(BASE + path + '?r125static-section=' + Date.now(), {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });
    assert(response && response.status() === 200, 'section HTTP status: ' + path);
    await page.waitForFunction(() => window.SEEKVERA_LOCALE_R15 && window.SEEKVERA_I18N_R32, { timeout: 30000 });
    await page.evaluate(() => window.SEEKVERA_LOCALE_R15.setLanguage('en'));
    await pause(30);
    const englishBody = await page.locator('body').innerText();
    const visibleEnglish = candidateEnglish.filter(value => englishBody.includes(value));
    const testLanguages = manifest.languages;

    for (const language of testLanguages) {
      await page.evaluate(async code => {
        window.SEEKVERA_LOCALE_R15.setLanguage(code);
        await window.SEEKVERA_I18N_R32.loadPack(code);
        await window.SEEKVERA_I18N_R32.apply();
      }, language);
      const state = await page.evaluate(() => document.documentElement.lang);
      assert.equal(state, language, 'section language application: ' + path + ' / ' + language);
      sectionLanguageApplications++;
      if (language === 'en') continue;
      const body = await page.locator('body').innerText();
      const leaks = visibleEnglish.filter(value =>
        typeof packs[language]?.[value] === 'string' &&
        body.includes(value)
      ).slice(0, 6);
      if (leaks.length) leakFindings.push({ path, language, leaks });
    }
    console.log('R125_STATIC_SECTION_PROGRESS', pathIndex + 1, '/', paths.length, path, 'languages', testLanguages.length);
  }

  assert.equal(leakFindings.length, 0, 'English UI leaks: ' + JSON.stringify(leakFindings.slice(0, 10)));
  assert.equal(blocked.translation.length, 0, 'unexpected dynamic translation calls: ' + JSON.stringify(blocked.translation.slice(0, 5)));
  assert.equal(blocked.ai.length, 0, 'unexpected AI calls: ' + JSON.stringify(blocked.ai.slice(0, 5)));
  assert.equal(blocked.pollinations.length, 0, 'unexpected external translation calls: ' + JSON.stringify(blocked.pollinations.slice(0, 5)));
  assert.equal(pageErrors.length, 0, 'browser page errors: ' + pageErrors.slice(0, 10).join(' | '));

  console.log('R125_STATIC_LOCALE_SECTION_AUDIT_PASS', JSON.stringify({
    languages: manifest.languages.length,
    sourceStrings: source.count,
    packs: Object.keys(packs).length,
    countryProfiles: countryMatrix.count,
    categoryLinks: hrefs.length,
    sectionPaths: paths.length,
    homepageLanguageApplications: languageApplications,
    sectionLanguageApplications,
    coverage: 'all 98 languages on homepage and all 98 languages on every discovered section path (full language-by-section matrix)',
    missingKeys: 0,
    extraKeys: 0,
    emptyValues: 0,
    englishLeakFindings: 0,
    aiRequests: blocked.ai.length,
    translationRequests: blocked.translation.length,
    externalTranslationRequests: blocked.pollinations.length,
    pageErrors: pageErrors.length
  }));
  await context.close();
} finally {
  await browser.close();
}
