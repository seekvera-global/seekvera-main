# SEEKVERA — First 20 language commercial release scope (2026-10-16)

## Decision
Prioritize a usable worldwide commercial SEEKVERA release over claiming the existing 98-language UI inventory is entirely production-certified. The user explicitly prioritizes **Arabic, English and French**, followed by at least **20 important world languages**. The voice and written chat experience must use the language actually spoken/typed, not silently inherit an unrelated UI language.

This is an **acceptance plan, not a release certificate**. None of the 20 languages is marked end-to-end voice certified here. Do not substitute static translation-pack counts, mocked audio or HTTP health checks for real device audio success.

## Proposed rollout languages, in priority order
1. Arabic (`ar`)
2. English (`en`)
3. French (`fr`)
4. Hindi (`hi`)
5. Chinese / Mandarin (`zh`)
6. Spanish (`es`)
7. Portuguese (`pt`)
8. German (`de`)
9. Russian (`ru`)
10. Japanese (`ja`)
11. Korean (`ko`)
12. Turkish (`tr`)
13. Urdu (`ur`)
14. Bengali (`bn`)
15. Indonesian (`id`)
16. Vietnamese (`vi`)
17. Italian (`it`)
18. Swahili (`sw`)
19. Persian (`fa`)
20. Hausa (`ha`)

All 20 already occur in `i18n-r32/manifest.json`. Their presence in the manifest is **not evidence of verified translation quality or working speech recognition and audio**. Keep the remaining language packs intact; do not call them certified or remove them as part of an untested config edit. This list is a practical proposed priority cohort, not an empirical ranking of language populations.

## Acceptance gate for EACH language
- [ ] Write free-form chat; correct language in AI's response (no unexpected English or language switching).
- [ ] Microphone understands normal spoken requests and accents, transcribes words accurately, preserves language without manually selecting it, and works through multiple consecutive turns.
- [ ] Speaker reads the answer aloud naturally, audibly, in the correct language, without silence, dropped playback, speech stuck in loading, or wrong-language output.
- [ ] Full speech -> transcription -> AI response -> speaker -> subsequent speech chain works on physical Android, iPhone/iPad and desktop (at minimum on supported browser environments).
- [ ] A spoken instruction to change country/language/currency updates the entire interface consistently; no stale values or mixed section labels.
- [ ] Spoken and typed requests for properties, cars, jobs, hotels/travel, services and other available sections route to the correct category/link, preserving context and user country choice.
- [ ] Each visible navigation section, search/filter, marketplace flow, saved conversation, and relevant listing action passes functional checks in that language.
- [ ] Live AI and ASR quota exhaustion produces a truthful, usable graceful fallback; do not advertise full hands-free speech reliability while live ASR is returning HTTP 503.
- [ ] Translation strings, placeholders, payment/price/currency labels and RTL where relevant are checked; manual language review required for release claims.
- [ ] Publish a dated, version-specific pass/fail record per language and device, with no false 100% claims.

## Execution priorities
1. Certify Arabic, English and French end to end before claiming them ready.
2. Apply the same check suite to the next 17 languages.
3. Confirm all existing country / category / listing and AI interactions for the release cohort; fix evidence-backed blockers.
4. Publish commercially only what the evidence proves. Missing third-party credentials and checkout configuration remain distinct launch blockers when payment is required.

## Existing evidence and current blockers (as of 2026-10-16)
- Earlier live auto speech-transcription checks: Arabic, English, French; several targeted written AI routes also passed.
- These checks do **not** establish full voice/speaker conversations on physical mobile devices.
- Latest staged candidate audit: 97 of 98 structurally complete packs; Dhivehi missing. Candidate packs remain unpublished and linguistic accuracy is not approved.
- Live ASR/translation requests have encountered daily free AI quota exhaustion (HTTP 503); no reliable universal speech claim is possible while unresolved.
- Current release certification remains `finalApproval: false`.

Work must prioritize demonstrable end-user usability over extending internal release version numbers.