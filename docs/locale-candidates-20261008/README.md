# Unpublished R125 localization candidates

These are resumable translation candidates, not production packs and not a certified release. **Use `resume-summary.json` as the latest candidate-quality snapshot**. The original `status.json` and `progress.json` are historical initial-generation records (20 initial candidates / initial failed attempt), not the current 98-pack inventory.

## Latest verified snapshot (2026-11-16 01:34 UTC)

- Source inventory: **1,118 strings**, source hash `6a1126e6a2ce5629`.
- **98/98 packs pass structural key/hash/nonempty checks**: 1,118 keys each, no missing/extra/empty values, source hash and quality policy match.
- **97/98** pass the current candidate-quality / long-English-overlap screen. Divehi (`dv`) remains blocked with `english_overlap:58`.
- Structural read-back report: `full-structural-readback-20261115-224200Z.json` (98 packs fetched directly; structural PASS only).
- Candidate packs remain unpublished; final approval and linguistic accuracy certification are both false (**0/98 native-certified**).
- The latest resume log records 48 successful prior Divehi repair translations, then timeout/HTTP 503 and unparseable Workers AI outputs. Google translation previously returned HTTP 429; `daily_free_ai_limit` was a real earlier blocker. Do not bypass provider quotas or treat backend errors as successful translations.
- Current AI Chat and translation availability are **unknown—not probed**; no quota-consuming request was made in this snapshot.
- The partial script/date warning map is clear, but the full 98-pack quality/duplicate/script audit remains pending. **304 deterministic/manual repairs since the last full audit are not native-language certification.**
- Amharic, Burmese, Igbo, Yoruba and other manual repairs are recorded in the summary/checkpoint; all still require qualified native review.
- Latest Pages build/deploy #1572 succeeded (2026-11-16 01:36 UTC). No R125 resume/translation run is active in the current observed run window; candidate writes remain deferred unless an explicit repair/translation mode is authorized.

## R125 audit-only write policy

Main workflow repair `298d8ab8` gates the Candidate Branch save/commit step on `run_translations || repair_candidates`. Audit-only mode can create workspace metadata and upload its report artifact, but it must not commit or push candidate metadata. Translation and deterministic repair modes are explicit opt-ins; publishing is not part of this workflow.

## Safe handling

Restore any `.json.gz` only into a separate staging directory (Python gzip or `gzip -dk`). Do not replace the production source inventory or manifest until all 98 packs pass integrity, full quality audit, and independent linguistic review. Do not publish partial or unreviewed packs. No chat transcripts or private user data are included.
