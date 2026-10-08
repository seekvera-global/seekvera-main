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
