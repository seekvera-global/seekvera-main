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

The auto-triggered legacy R35 run 37774318592 has a failed Serbian build (job 113301331429). Its final deployment job depends on successful completion of the entire build matrix and has no override condition, so this attempt cannot reach the old R35 deployment. Remaining matrix jobs may finish, but no R35 release is approved or published by this failed attempt. The future automatic trigger has been removed.

A separate coverage inventory records five new static keys and 59 observed dynamic keys missing from the recorded static source (`r125-translation-coverage-gaps.json`). This inventory is diagnostic, not a claim that every untranslated phrase has been found. Fresh hashes of the four repaired live assets matched the tested local files after deployment.

The Serbian failure provides a concrete external-service blocker: Google translation returned HTTP 429, then the public fallback returned HTTP 500 followed by HTTP 402 Payment Required. The system must not treat this as a valid translation, silently approve a pack, or incur payment to bypass it.

## Completion follow-up

The existing same-origin translation endpoint was also tested. It returned HTTP 200 for a French batch, but its 1B-model output incorrectly translated “speaker” as “microphone” and changed the grammatical subject of “Understanding your speech…”. Availability therefore does not resolve linguistic quality. Four reviewed French and Arabic voice labels are now provided by the existing local QUICK dictionary before cached or generated translations; the static 1,045-key manifest remains unchanged. This does not complete other languages or dynamic coverage.

Commit `b8c5e27b6e40af6c2567e802d9fd3e6a2f0487d2` deployed successfully through run 37776102408, Cloudflare version `14b8b26b-6d50-4619-bbb9-d7f2bd14accf`. All audio-authority steps passed, including three live speech languages, four chat cases, 31 Arabic descriptions and delayed playback before navigation. The production i18n asset exactly matched the reviewed local bytes.

R105 initially rejected the updated i18n version because its source check pinned the previous version. The check was updated to the new exact version, with the locale regression added; the validation was not removed. The current-live checker now always records `finalApproval: false` and the outstanding coverage, linguistic review and physical-device checks. A passing exact-node leak audit is not final release certification.

The completion audit passed 98 static packs, 248 country states, 31 route links and 392 page/language combinations across four paths: home, games, deal-agent and everyday. Seven blocked dynamic translation requests confirm that this run did not silently depend on online translation for the recorded phrases. This is a four-path scope, not a complete 28-path rerun. The deployment changed during the audit, so it is not an immutable-commit full certification. Its report is `r125-completion-certification-20261008.json`, explicitly `finalApproval: false`. Separate live lookups passed all four reviewed voice labels in both French and Arabic.

R105 also pinned the previous version in its live-asset assertion; that assertion has now been aligned with the exact new version. The intermediate failed runs deployed successfully but rejected that stale assertion; their logs showed healthy AI, country control and safety responses.

Final current-release deployment run 37776583799 completed successfully for commit `d3fcf11b070f6a653e0ccf4fd633ccf7e266eeb6`, Cloudflare version `16015ab5-76b4-4203-a039-09278bcb9325`. Validation, deployment and live health/chat/country-control/safety checks passed. This success resolves the stale version assertions; it does not override the explicit final-approval gaps.
