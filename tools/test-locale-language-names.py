#!/usr/bin/env python3
"""Quota-neutral regression: every manifest locale must have a target-language name."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_current_locale_delta import translation_language_name  # noqa: E402

manifest = json.loads((ROOT / "i18n-r32" / "manifest.json").read_text(encoding="utf-8"))
codes = manifest["languages"]
assert len(codes) == 98, f"Expected 98 manifest languages, found {len(codes)}"
assert len(set(codes)) == 98, "Manifest contains duplicate language codes"

unresolved = {}
for code in codes:
    try:
        name = translation_language_name(code)
    except Exception as exc:
        unresolved[code] = str(exc)
        continue
    if not isinstance(name, str) or not name.strip():
        unresolved[code] = "empty target-language name"

assert not unresolved, f"Unresolved target-language names: {unresolved}"
print(f"PASS: {len(codes)}/98 target-language names resolve; no translation requests sent.")
