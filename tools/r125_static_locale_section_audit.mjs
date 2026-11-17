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
    const raw = route.request().postData() || '';
    let payload = {};
    try { payload = JSON.parse(raw); } catch { payload = { raw: raw.slice(0, 500) }; }
    blocked.translation.push({
      url: route.request().url(),
      method: route.request().method(),
      language: payload.language || payload.lang || 'unknown',
      strings: Array.isArray(payload.strings) ? payload.strings.slice(0, 20) : [],
      stringCount: Array.isArray(payload.strings) ? payload.strings.length : 0
    });
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

  // Neon Highway is a named game title; its dedicated game-title assertion below still verifies any supplied localized title.
  const approvedProperNouns = new Set(['YouTube Music', 'United Kingdom', 'United States', 'Neon Highway']);
  const candidateEnglish = sourceKeys.filter(value =>
    value.length >= 12 &&
    (value.match(/[A-Za-z][A-Za-z'’+-]{2,}/g) || []).length >= 2 &&
    !value.includes('SEEKVERA') &&
    !approvedProperNouns.has(value) &&
    !/https?:\/\/|@/.test(value)
  );
  const leakFindings = [];
  const partialFindings = [];
  const unresolvedFindings = [];
  async function inspectLeakState(phrases) {
    return page.evaluate(targets => {
      const norm = value => String(value || '').replace(/\\s+/g, ' ').trim();
      const nodes = [];
      const options = [];
      const elements = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const el = node.parentElement;
        if (!el || !el.getClientRects().length) continue;
        const raw = norm(node.nodeValue);
        if (!raw) continue;
        for (const phrase of targets) {
          if (!raw.includes(phrase)) continue;
          const chain = [];
          let current = el;
          for (let depth = 0; current && depth < 4; depth++, current = current.parentElement) {
            chain.push({
              tag: current.tagName.toLowerCase(),
              id: current.id || '',
              className: typeof current.className === 'string' ? current.className : '',
              noTranslate: current.hasAttribute('data-no-translate'),
              userContent: current.hasAttribute('data-user-content'),
              text: norm(current.innerText || current.textContent).slice(0, 160)
            });
          }
          nodes.push({ phrase, text: raw.slice(0, 240), chain });
        }
      }
      for (const select of document.querySelectorAll('select')) {
        if (!select.getClientRects().length) continue;
        for (const option of [...select.options]) {
          const raw = norm(option.textContent);
          if (!raw) continue;
          for (const phrase of targets) {
            if (raw.includes(phrase)) options.push({
              phrase, text: raw, selectId: select.id || '',
              selectName: select.name || '', selected: option.selected,
              value: option.value || ''
            });
          }
        }
      }
      for (const phrase of targets) {
        const hasNode = nodes.some(item => item.phrase === phrase);
        const hasOption = options.some(item => item.phrase === phrase);
        if (hasNode || hasOption) continue;
        const candidates = [...document.body.querySelectorAll('*')].filter(el =>
          el.getClientRects().length && norm(el.innerText).includes(phrase)
        );
        const leaves = candidates.filter(el =>
          ![...el.children].some(child => child.getClientRects().length && norm(child.innerText).includes(phrase))
        );
        for (const el of leaves.slice(0, 4)) {
          const text = norm(el.innerText || el.textContent);
          elements.push({
            phrase, text: text.slice(0, 240), exact: text === phrase,
            tag: el.tagName.toLowerCase(), id: el.id || '',
            className: typeof el.className === 'string' ? el.className : ''
          });
        }
      }
      return {
        runtime: {
          language: document.documentElement.lang,
          readyLanguage: document.documentElement.dataset.seekveraI18nReady || '',
          runtimeVersion: document.documentElement.dataset.seekveraI18nVersion || '',
          packReady: !!window.SEEKVERA_I18N_R32?.packReady?.(document.documentElement.lang)
        },
        nodes: nodes.slice(0, 40),
        options: options.slice(0, 20),
        elements: elements.slice(0, 20)
      };
    }, phrases);
  }
  function classifyLeakEvidence(phrases, evidence) {
    const exact = [], partial = [], unresolved = [], details = {};
    for (const phrase of phrases) {
      const nodes = evidence.nodes.filter(item => item.phrase === phrase);
      const options = evidence.options.filter(item => item.phrase === phrase);
      const elements = evidence.elements.filter(item => item.phrase === phrase);
      details[phrase] = { nodes, options, elements };
      const exactMatch = nodes.some(item => item.text === phrase) ||
        options.some(item => item.text === phrase) ||
        elements.some(item => item.text === phrase || item.exact);
      if (exactMatch) exact.push(phrase);
      else if (nodes.length || options.length || elements.length) partial.push(phrase);
      else unresolved.push(phrase);
    }
    return { exact, partial, unresolved, details };
  }
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
      const controlLabels = await page.evaluate(() => ({
        country: document.querySelector('.sv-control-field[data-kind="country"] .sv-control-caption-label')?.textContent?.trim() || '',
        language: document.querySelector('.sv-control-field[data-kind="language"] .sv-control-caption-label')?.textContent?.trim() || '',
        currency: document.querySelector('.sv-control-field[data-kind="currency"] .sv-control-caption-label')?.textContent?.trim() || ''
      }));
      for (const [kind, source] of [['country', 'Country / Region'], ['language', 'Language'], ['currency', 'Currency']]) {
        // The runtime has a small, reviewed QUICK dictionary that may intentionally
        // use a different valid wording from the full locale pack (for example,
        // Arabic "الدولة / المنطقة" vs the pack's "البلد / المنطقة").
        // Accept either runtime translation or pack translation, but never English
        // source text for a non-English locale.
        const runtimeExpected = await page.evaluate(
          value => String(window.SEEKVERA_I18N?.t?.(value) || value).trim(),
          source
        );
        const packExpected = String(packs[language]?.[source] || source).trim();
        const acceptable = new Set([runtimeExpected, packExpected].filter(value => value && value !== source));
        assert(acceptable.size > 0, 'missing localized ' + kind + ' control caption: ' + language);
        assert(acceptable.has(controlLabels[kind]), 'localized ' + kind + ' control caption: ' + language + ' got ' + controlLabels[kind]);
      }
      const body = await page.locator('body').innerText();
      const leaks = homePresent.filter(value =>
        typeof packs[language]?.[value] === 'string' &&
        body.includes(value)
      ).slice(0, 6);
      if (leaks.length) {
        const evidence = await inspectLeakState(leaks);
        const classified = classifyLeakEvidence(leaks, evidence);
        if (classified.exact.length) leakFindings.push({ path: '/', language, leaks: classified.exact, runtime: evidence.runtime, evidence: classified.details });
        if (classified.partial.length) partialFindings.push({ path: '/', language, leaks: classified.partial, runtime: evidence.runtime, evidence: classified.details });
        if (classified.unresolved.length) unresolvedFindings.push({ path: '/', language, leaks: classified.unresolved, runtime: evidence.runtime, evidence: classified.details });
      }
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
      if (path.endsWith('/games.html')) {
        const expectedGameTitle = String(packs[language]?.['Neon Highway'] || 'Neon Highway').trim();
        if (expectedGameTitle !== 'Neon Highway') {
          const renderedTitles = await page.evaluate(() => ({
            selected: document.querySelector('#gameTitle')?.textContent?.trim() || '',
            firstCard: document.querySelector('#gameGrid .game b')?.textContent?.trim() || ''
          }));
          assert.equal(renderedTitles.selected, expectedGameTitle, 'localized selected game title: ' + language);
          assert.equal(renderedTitles.firstCard, expectedGameTitle, 'localized game card title: ' + language);
        }
      }
      const leaks = visibleEnglish.filter(value =>
        typeof packs[language]?.[value] === 'string' &&
        body.includes(value)
      ).slice(0, 6);
      if (leaks.length) {
          const evidence = await inspectLeakState(leaks);
          const classified = classifyLeakEvidence(leaks, evidence);
          if (classified.exact.length) leakFindings.push({ path, language, leaks: classified.exact, runtime: evidence.runtime, evidence: classified.details });
          if (classified.partial.length) partialFindings.push({ path, language, leaks: classified.partial, runtime: evidence.runtime, evidence: classified.details });
          if (classified.unresolved.length) unresolvedFindings.push({ path, language, leaks: classified.unresolved, runtime: evidence.runtime, evidence: classified.details });
        }
    }
    console.log('R125_STATIC_SECTION_PROGRESS', pathIndex + 1, '/', paths.length, path, 'languages', testLanguages.length);
  }

  const leakCounts = new Map();
  for (const finding of leakFindings) {
    for (const phrase of finding.leaks) {
      leakCounts.set(phrase, (leakCounts.get(phrase) || 0) + 1);
    }
  }
  console.log('R125_STATIC_LEAK_SUMMARY', JSON.stringify({
    exactFindingCombinations: leakFindings.length,
    exactLanguages: [...new Set(leakFindings.map(item => item.language))].sort(),
    exactSections: [...new Set(leakFindings.map(item => item.path))].sort(),
    exactPhraseCounts: Object.fromEntries([...leakCounts.entries()].sort((a, b) => b[1] - a[1])),
    partialFindingCombinations: partialFindings.length,
    partialLanguages: [...new Set(partialFindings.map(item => item.language))].sort(),
    unresolvedFindingCombinations: unresolvedFindings.length,
    unresolvedLanguages: [...new Set(unresolvedFindings.map(item => item.language))].sort(),
    sectionLanguageApplications
  }));
  const fallbackByLanguage = {};
  for (const request of blocked.translation) {
    const language = request.language || 'unknown';
    const entry = fallbackByLanguage[language] || { requests: 0, strings: new Set() };
    entry.requests++;
    for (const value of request.strings || []) entry.strings.add(value);
    fallbackByLanguage[language] = entry;
  }
  const fallbackSummary = Object.fromEntries(Object.entries(fallbackByLanguage).map(([language, value]) => [
    language,
    { requests: value.requests, uniqueStrings: value.strings.size, samples: [...value.strings].slice(0, 20) }
  ]));
  console.log('R125_STATIC_LEAK_DETAILS', JSON.stringify(leakFindings));
  console.log('R125_STATIC_PARTIAL_MATCH_DETAILS', JSON.stringify(partialFindings));
  console.log('R125_STATIC_UNRESOLVED_MATCH_DETAILS', JSON.stringify(unresolvedFindings));
  console.log('R125_STATIC_TRANSLATION_FALLBACK_DETAILS', JSON.stringify(fallbackSummary));
  console.log('R125_STATIC_BLOCKED_REQUESTS', JSON.stringify({
    ai: blocked.ai.length,
    translation: blocked.translation.length,
    pollinations: blocked.pollinations.length
  }));
  assert.equal(leakFindings.length, 0, 'English UI leaks: ' + JSON.stringify(leakFindings.slice(0, 10)));
  assert.equal(partialFindings.length, 0, 'English segments inside localized UI require review: ' + JSON.stringify(partialFindings.slice(0, 10)));
  assert.equal(unresolvedFindings.length, 0, 'Unresolved visible English matches require DOM review: ' + JSON.stringify(unresolvedFindings.slice(0, 10)));
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
    pageErrors: pageErrors.length,
    approvedProperNouns: [...approvedProperNouns]
  }));
  await context.close();
} finally {
  await browser.close();
}
