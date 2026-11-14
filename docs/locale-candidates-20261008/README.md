# Unpublished R125 localization candidates

These are resumable translation candidates, not production packs and not a certified release. Read `status.json` and `resume-summary.json` before using them.

## Snapshot (2026-11-14 12:01 UTC)

- Source inventory: **1,118 strings**, source hash `6a1126e6a2ce5629`.
- **97/98** language packs pass the current structural/long-English-overlap screen.
- **Divehi (`dv`) is the remaining pack**; its current audit reports `english_overlap:58`.
- Candidate packs remain unpublished; final approval and linguistic accuracy certification are both false.
- The latest resume log records 48 successful prior Divehi repair translations, then backend HTTP 503/unparseable outputs. Google translation previously returned HTTP 429. Do not bypass provider quotas or treat backend errors as successful translations.
- The current partial warning map is cleared, but the full 98-pack audit is still pending. The 82 deterministic/manual repairs since the last audit are not native-language certification.
- Amharic and Burmese have manual repairs recorded in the summary/checkpoint; those changes still require qualified native review.

## Safe handling

Restore any `.json.gz` only into a separate staging directory (Python gzip or `gzip -dk`). Do not replace the production source inventory or manifest until all 98 packs pass integrity, full audit, and independent linguistic review. Do not publish partial or unreviewed packs. No chat transcripts or private user data are included.
