#!/usr/bin/env python3
"""Restore executable CSS source strings exactly; no translation or publication."""
import argparse
import json
import re
from pathlib import Path

from tools.build_current_locale_delta import source_invariant_keys

LOCALE_FILE = re.compile(r"^[a-z]{2,3}\.json$")


def repair(stage: Path):
    source = json.loads((stage / "source.json").read_text(encoding="utf-8"))
    source_hash = source.get("sourceHash")
    invariants = source_invariant_keys(source.get("strings", []))
    if len(invariants) != 3:
        raise RuntimeError(f"Expected exactly 3 executable source invariants; found {len(invariants)}")

    changed = []
    skipped = []
    for path in sorted(stage.glob("*.json")):
        if not LOCALE_FILE.fullmatch(path.name):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("sourceHash") != source_hash:
            skipped.append({"language": path.stem, "reason": "source_hash_mismatch"})
            continue
        translations = data.get("translations")
        if not isinstance(translations, dict):
            skipped.append({"language": path.stem, "reason": "translations_not_object"})
            continue

        missing = [key for key in invariants if key not in translations]
        changed_keys = [key for key in invariants if key in translations and translations[key] != key]
        if changed_keys:
            for key in changed_keys:
                translations[key] = key
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            changed.append({"language": path.stem, "keys": len(changed_keys)})
        if missing:
            skipped.append({"language": path.stem, "reason": "invariant_key_missing", "count": len(missing)})

    return {"invariantCount": len(invariants), "changed": changed, "skipped": skipped}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="docs/locale-candidates-20261008")
    args = parser.parse_args()
    result = repair(Path(args.stage))
    changed_values = sum(item["keys"] for item in result["changed"])
    print(
        "SOURCE_INVARIANT_REPAIR "
        f"changed_packs={len(result['changed'])} exact_values={changed_values} "
        f"skipped={len(result['skipped'])} invariant_keys={result['invariantCount']}"
    )
    print("STRUCTURAL_ONLY no translation requests; no AI quota; no linguistic certification; no publication")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
