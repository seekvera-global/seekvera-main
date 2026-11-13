#!/usr/bin/env python3
"""Regression for the deterministic immutable-ID repair; no network or AI calls."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "repair-candidate-reserved-identifiers.py"
IDENTIFIER = "SV-YYYYMMDD-XXXXXXXX"

with tempfile.TemporaryDirectory() as tmp:
    stage = Path(tmp)
    pack = stage / "ar.json"
    original = {
        "language": "ar",
        "count": 2,
        "translations": {IDENTIFIER: "SV-YYYYMMDD-XXXXXXXXX", "Hello": "مرحبا"},
    }
    pack.write_text(json.dumps(original, ensure_ascii=False, indent=2), encoding="utf-8")
    source = stage / "source.json"
    source.write_text(json.dumps({"translations": {IDENTIFIER: "source"}}), encoding="utf-8")

    first = subprocess.run([sys.executable, str(SCRIPT), "--stage", str(stage)], capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    fixed = json.loads(pack.read_text(encoding="utf-8"))
    assert fixed["translations"][IDENTIFIER] == IDENTIFIER
    assert fixed["translations"]["Hello"] == "مرحبا"
    assert json.loads(source.read_text(encoding="utf-8"))["translations"][IDENTIFIER] == "source"
    assert "changed=1 locales=ar" in first.stdout

    second = subprocess.run([sys.executable, str(SCRIPT), "--stage", str(stage)], capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    assert "changed=0 locales=none" in second.stdout

print("PASS: immutable ID is repaired exactly once, other strings/source are preserved, and rerun is idempotent.")
