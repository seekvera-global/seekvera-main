# R76 workflow investigation — 8 October 2026

## Evidence

- Run 36855209030 used commit `70edf3e32b222434ff9bbc518a9101d94750541c`; run 36854561177 used `e19f13d5a24947e09cffefb6a423d992ffd472be`. Both ran `.github/workflows/r76-complete-global-final.yml` on 1 October.
- French jobs 110346051112 and 110343936688 failed with `RuntimeError: fr: forced UI remained English: ['Contact']`. HTML batch corruption was retried, split and repaired; it was not the final fatal error.
- Italian jobs 110346051279 and 110343936784 failed on `Privacy`; Dutch job 110343938686 also failed on `Privacy`. These are legitimate target-language labels. The strict equality check confused cognates with untranslated English. The builder is generated from `tools/r35_build_pack.py` inside the prepare job.
- Run 36277820651 used commit `0d3334a491c501a06456c5f3ccbce618b37918f3` on 26 September, not 1 October. Cloudflare deployment succeeded (version `2366d75f-484a-404d-9e5d-cee9d7e8502e`). The API returned HTTP 429; the static homepage returned 200 and all 98 static packs passed.
- Certification logged `R76_98_STATIC_PACKS_PASS` at 22:56:18 UTC and then no further progress before cancellation at 23:40:44. The next awaited operation is the all-country browser evaluation. The job started about 22:55:30 and has `timeout-minutes: 45`: cancellation is consistent with exhaustion of that job deadline, not a successful audit. The logs do not identify the internal browser condition that prevented the country loop from completing.
- `page.evaluate` does not inherit the configured Playwright action timeout. The single async evaluation loop had no host-side deadline or per-country progress. Translation interception was installed only after this loop, so it could not prevent dynamic requests during country changes.
- The persistence step was skipped because certification was cancelled. Deploying before certification therefore left an uncertified live deployment, not a persisted certified release.

## Changes

- Allow only the demonstrated exact language/label pairs: French Contact, Italian Privacy, Dutch Privacy. Keep strict validation for other forced labels and oversized output. The generated R76 builder inherits this fix.
- Add offline pack-write regression tests and execute them in the prepare job.
- Bound each country evaluation with a host-side deadline, log the country before checking it, intercept dynamic translation before country changes, and impose a process deadline plus a step deadline. All country profiles remain checked; no assertion is removed.

## Validation and limits

Passed: three offline regression tests covering complete cognate packs, genuine untranslated forced-label rejection and corrupt output rejection; JavaScript syntax; bounded evaluation success and timeout regression; diff whitespace check. Tests stub translation responses and do not certify the external translator or production UI.

On 8 October, a fresh read of `https://seekveraglobal.com/api/health` returned 200 and `release: 20261001-r125-dialect-voice-quality`. Production is newer than R76. This patch does not deploy or roll it back. The historical R76 certifier still contains old release/source-count assertions; it must not be used to certify R125 without adapting expectations to that exact candidate.

Before final approval: build all 98 packs for the candidate's exact source hash; verify every country/language/currency combination and all category pages; obtain successful live AI language/dialect/routing and chat persistence results; test actual microphone transcription and audible output on Android, iPhone/iPad and desktop. Mocking `speechSynthesis.speak` only verifies invocation, not audible playback or transcription quality. Save a certification record tied to the exact deployed commit/version and artifacts. A health 200 does not establish those results.

## Follow-up implementation and live checks

- Current R125 local tests passed: dialect/uncertainty, direct voice routing, TTS envelopes, audio authority, pack cognates, and locale-control regressions.
- Live server-generated speech was transcribed successfully in Arabic, French and English with automatic language selection despite a contradictory phone transcript and Arabic context. Four live AI cases passed: French jobs, Arabic jobs, Spanish travel and Japanese jobs.
- The existing R124 browser test passed using the live frontend with mocked AI/TTS: a delayed one-second PCM clip decoded and completed before navigation, with chat saved. This is browser audio processing evidence, not a human recording or a physical-speaker test.
- Baseline live audit checked 98 packs, 248 country states and 2,744 section/language combinations across 28 paths and 31 routes. It flagged 84 combinations with recorded English phrases still appearing. Some substring hits were inside longer translated text; the follow-up checker matches whole text nodes to avoid counting those as standalone label failures. Baseline evidence is in `r125-baseline-certification-20261008.json`.
- Fixed currency options losing their implicit values when relabelled, generating duplicates and preventing subsequent localization. Currency values are now pinned to ISO codes and duplicate options removed.
- Country labels now use existing static pack translations when browser Intl region data falls back to English. Category labels prefer available static translations, and emoji-prefixed labels reuse the localized base label when an older pack contains only its English form. These changes were checked using candidate overlays of the live frontend, not represented as already deployed.
- Historical source-rewriting workflows are manual-only: complete R76, persisted R76, and R3 premium i18n. Merging current fixes must not automatically reapply those older releases.

### Final approval remains blocked

The baseline audit recorded dynamic translation requests for game descriptions, navigation labels, the newer assistant introduction and marketplace error messages. Several newer voice placeholders also have no exact key in the recorded source. The direct translation provider returned HTTP 429 during the repair attempt. No English placeholder or machine-produced replacement was invented to mark these complete. Whole-node leak checks also do not prove linguistic accuracy or detect every partially untranslated sentence: German pack examples retain English clauses. A complete source extraction/translation repair and device voice validation remain necessary. The current health endpoint and successful focused checks are insufficient for a final certification.

## Deployment result

PR #7 was merged as `9bc574f1a6a60777201ead9a7d361f6e6109a9ff`. Current R125 deployment/verification runs 37774318439 and 37774318417 completed successfully. The latter deployed Cloudflare version `74bd561b-3458-4383-8289-4894cadb4815` and passed live Arabic/French/English audio, French/Arabic/Spanish/Japanese chat, all 31 Arabic category descriptions, and delayed audio completion before navigation.

Post-deployment focused checking (without candidate overrides) passed 98 live pack integrity checks, 248 atomic country states and 52 page/language checks covering the reported failures. Evidence is in `r125-postdeploy-certification-20261008.json`; its `finalApproval` is explicitly false because dynamic source coverage, translation quality and physical device audio remain incomplete. These focused results must not be described as a new full 2,744-combination pass.

A legacy R35 workflow also auto-triggered through the shared builder path. Its French build passed (job 113301325780), providing an external translation-build check, but it extracts only 970 strings and is not a certification of the current 1,045-string static source. Future R35 executions are now manual-only as well.
