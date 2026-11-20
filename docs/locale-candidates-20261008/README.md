# Unpublished R125 localization candidates

These files are resumable translation candidates, **not production packs and not a certified release**. Use `resume-summary.json` as the current quality and continuation record; `resume-latest.log` is the most recent provider-resume log. The original `status.json` and `progress.json` are historical initial-generation records, not the current inventory.

## Latest verified snapshot — 2026-11-20 12:22 UTC

- Candidate source: **1,118 strings**, source hash `6a1126e6a2ce5629`.
- Candidate packs: **98/98 structurally complete** (1,118 keys each; exact key/source-hash/nonempty checks pass).
- Saved quality gate: **97/98 pass**. Divehi (`dv`) remains blocked by **58 English-overlap findings**.
- **0/98 published** and **0/98 linguistically certified**. Structural completeness is not linguistic approval.
- Production source has 1,045 keys; candidate source has 1,118. The 73 candidate-only keys are 60 game strings and 13 additional UI/voice strings. The 60 game strings are present in sampled candidate packs, but remain unpublished and uncertified. Igbo and Divehi samples reinforce the existing duplicate/quality warnings; native review is required.
- Main R125 #153 (2026-11-20) passed the 98-language × 27-section matrix (2,646 applications), the 248-country matrix, and visible-English checks (zero exact/partial/unresolved findings), but **failed the no-dynamic-fallback gate**: 551 locally intercepted requests across 97 languages and 63 unique strings (60 game strings plus three seller-plan limits).
- The three seller-plan limits are real Supabase data: Free = 3 active ads, Business Monthly = 50, Business Yearly = 100. Their phrases have no reviewed locale-source keys in production or candidate source. Do not hide the limits, mark them no-translate, or remove them to force a pass.
- All R125 audit translation calls were intercepted locally. No AI/provider/Pollinations request and no quota use occurred.
- The candidate resume workflow on Main is manual-only, not hourly scheduled. Both `run_translations` and `repair_candidates` default to false. Latest located matching run #150 (2026-10-16) completed with Resume skipped, audit success, and zero candidate-pack writes. The latest observed 100 repository runs contain no matching or active/queued resume run.
- Current live AI chat and translation availability are **unknown—not probed**. Historical `daily_free_ai_limit` and Google HTTP429 are real blockers; the latest resume log records Dhivehi timeouts, HTTP 503 `all_translation_backends_unavailable`, and three unparseable Workers AI outputs. Do not bypass quotas or treat backend failures as translations.
- Audio Authority #178 passed programmatic TTS, acknowledgement and placeholder checks, but production multilingual audio assets and live ASR were not verified; physical microphones and speakers are not certified.
- Country R9e #138 and Safety #92 passed on 2026-11-19. R125 #153 also passed its 248-country matrix. Country/Safety suites have not been re-dispatched on the latest Main head.
- Checkout remains inactive pending merchant configuration and end-to-end payment, refund, forged-reference rejection, settlement and webhook verification.

## R125 candidate-resume write policy

The Main workflow `.github/workflows/r125-hourly-candidate-resume.yml` is `workflow_dispatch` only. Audit-only mode may produce logs/artifacts, but candidate-pack writes require explicit `run_translations=true` or `repair_candidates=true`. Translation mode can consume production AI quota; do not enable it while free quota/provider rate limits are blockers. Do not write candidate packs while a matching resume run is active.

## Safe handling

Keep all candidate JSON and compressed snapshots separate from production `i18n-r32` packs. Do not replace the production source inventory or manifest until all 98 packs pass the current structural and quality audits and receive independent qualified linguistic review. Do not publish partial or unreviewed packs. No chat transcripts or private user data are included.
