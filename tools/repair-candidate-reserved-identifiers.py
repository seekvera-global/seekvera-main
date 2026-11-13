#!/usr/bin/env python3
"""Deterministically restore the immutable SEEKVERA ID placeholder in candidate locale packs.

This is a structural repair only. It does not translate, certify, or publish any pack.
"""
import argparse
import json
import re
from pathlib import Path

IDENTIFIER = "SV-YYYYMMDD-XXXXXXXX"
LOCALE_FILE = re.compile(r"^[a-z]{2,3}\.json$")


def repair(stage: Path) -> list[str]:
    changed = []
    for path in sorted(stage.glob("*.json")):
        if not LOCALE_FILE.fullmatch(path.name):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        translations = data.get("translations")
        if not isinstance(translations, dict) or IDENTIFIER not in translations:
            continue
        if translations[IDENTIFIER] == IDENTIFIER:
            continue
        translations[IDENTIFIER] = IDENTIFIER
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed.append(path.stem)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="docs/locale-candidates-20261008")
    args = parser.parse_args()
    stage = Path(args.stage)
    if not stage.is_dir():
        raise SystemExit(f"candidate stage not found: {stage}")
    changed = repair(stage)
    print(f"RESERVED_ID_REPAIR changed={len(changed)} locales={','.join(changed) if changed else 'none'}")
    print("STRUCTURAL_ONLY no translation requests; no linguistic certification; no publication")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
