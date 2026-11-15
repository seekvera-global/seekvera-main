#!/usr/bin/env python3
"""Quota-neutral tests for executable CSS source-invariant repair."""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_current_locale_delta import source_invariant_keys

spec = importlib.util.spec_from_file_location(
    "repair_candidate_source_invariants",
    ROOT / "tools" / "repair-candidate-source-invariants.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CSS1 = "html.sv-r15-applying .r5-top{transition:none!important}"
CSS2 = ".sv-r31-switching .r5-center{opacity:.12;transition:none}"
CSS3 = "#categories .r5-tile-body{overflow:hidden!important}"
PROSE = "Hello from SEEKVERA"


def write_pack(path, source_hash, translations):
    path.write_text(
        json.dumps(
            {"sourceHash": source_hash, "translations": translations},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )


def main():
    source = {"sourceHash": "test-source-hash", "strings": [CSS1, CSS2, CSS3, PROSE]}
    assert source_invariant_keys(source["strings"]) == {CSS1, CSS2, CSS3}

    with tempfile.TemporaryDirectory() as temp:
        stage = Path(temp)
        source_bytes = json.dumps(source, ensure_ascii=False).encode()
        (stage / "source.json").write_bytes(source_bytes)

        write_pack(stage / "en.json", source["sourceHash"], {
            CSS1: "translated selector one", CSS2: CSS2,
            CSS3: "translated selector three", PROSE: PROSE,
        })
        write_pack(stage / "ar.json", source["sourceHash"], {
            CSS1: CSS1, CSS2: "translated selector two",
            CSS3: "translated selector three", PROSE: "مرحباً من SEEKVERA",
        })
        write_pack(stage / "dv.json", "stale-hash", {
            CSS1: "must remain untouched", CSS2: CSS2, CSS3: CSS3, PROSE: PROSE,
        })

        first = module.repair(stage)
        assert {item["language"] for item in first["changed"]} == {"ar", "en"}
        assert sum(item["keys"] for item in first["changed"]) == 4
        assert first["skipped"] == [{"language": "dv", "reason": "source_hash_mismatch"}]
        assert (stage / "source.json").read_bytes() == source_bytes

        en = json.loads((stage / "en.json").read_text(encoding="utf-8"))["translations"]
        ar = json.loads((stage / "ar.json").read_text(encoding="utf-8"))["translations"]
        dv = json.loads((stage / "dv.json").read_text(encoding="utf-8"))["translations"]
        for key in (CSS1, CSS2, CSS3):
            assert en[key] == key and ar[key] == key
        assert en[PROSE] == PROSE
        assert ar[PROSE] == "مرحباً من SEEKVERA"
        assert dv[CSS1] == "must remain untouched"

        second = module.repair(stage)
        assert second["changed"] == []
        assert second["skipped"] == [{"language": "dv", "reason": "source_hash_mismatch"}]

    print("PASS: CSS invariants restored exactly, non-CSS translations preserved, stale packs skipped, source unchanged, repair idempotent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
