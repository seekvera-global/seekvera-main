"""Audit staged packs without claiming linguistic review or publishing them."""
import argparse
import datetime
import json
import subprocess
from pathlib import Path

from tools.build_current_locale_delta import (
    ROOT,
    reviewed_labels,
    source_invariant_keys,
    suspicious_overlap,
)


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object repeats a key that json.loads would overwrite."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_unique(raw):
    """Parse JSON while rejecting duplicate keys at every object depth."""
    return json.loads(raw, object_pairs_hook=_unique_object)


def read_json_unique(path):
    return parse_json_unique(Path(path).read_text(encoding="utf-8"))


def key_set_mismatch(values, expected_keys):
    expected = set(expected_keys)
    if not isinstance(values, dict):
        return sorted(expected), []
    actual = set(values)
    return sorted(expected - actual), sorted(actual - expected)


def audit(stage, exit_code="not-run"):
    stage = Path(stage)
    try:
        source = read_json_unique(stage / "source.json")
    except (DuplicateJSONKeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"Candidate source JSON is invalid: {exc}") from exc
    if not isinstance(source, dict) or not isinstance(source.get("strings"), dict):
        raise RuntimeError("Candidate source JSON must contain a strings object")

    languages = json.loads((ROOT / "i18n-r32/manifest.json").read_text(encoding="utf-8"))["languages"]
    reviewed = reviewed_labels()
    completed = []
    failures = {}
    packs = {}

    for code in languages:
        path = stage / (code + ".json")
        if not path.exists():
            failures[code] = ["missing_pack"]
            continue
        try:
            data = read_json_unique(path)
        except DuplicateJSONKeyError:
            failures[code] = ["duplicate_json_keys"]
            continue
        except (json.JSONDecodeError, UnicodeDecodeError):
            failures[code] = ["invalid_json"]
            continue
        if not isinstance(data, dict):
            failures[code] = ["pack_not_object"]
            continue

        values = data.get("translations", {})
        reasons = []
        if not isinstance(values, dict):
            reasons.append("translations_not_object")
            values = {}

        missing_keys, extra_keys = key_set_mismatch(values, source["strings"])
        if missing_keys or extra_keys:
            reasons.append(
                "key_set_mismatch:missing=" + str(len(missing_keys))
                + ":extra=" + str(len(extra_keys))
            )
        if data.get("sourceHash") != source.get("sourceHash"):
            reasons.append("source_hash_mismatch")
        if data.get("qualityPolicy") != "source-overlap-5-v1":
            reasons.append("quality_policy_mismatch")
        if not all(
            isinstance(values.get(key), str) and values[key].strip()
            for key in source["strings"]
        ):
            reasons.append("missing_strings")
        if not all(
            values.get(key) == value
            for key, value in reviewed.get(code, {}).items()
            if key in source["strings"]
        ):
            reasons.append("reviewed_label_mismatch")

        invariants = source_invariant_keys(source["strings"])
        invariant_mismatches = [key for key in invariants if values.get(key) != key]
        if invariant_mismatches:
            reasons.append("source_invariant_mismatch:" + str(len(invariant_mismatches)))

        overlap = [
            key for key in source["strings"]
            if code != "en" and suspicious_overlap(key, values.get(key, ""))
        ]
        if overlap:
            reasons.append("english_overlap:" + str(len(overlap)))

        if reasons:
            failures[code] = reasons
        else:
            completed.append(code)
        packs[code] = values

    script = Path(__file__).with_name("audit-candidate-scripts.cjs")
    script_issues = json.loads(
        subprocess.check_output(
            ["node", str(script)],
            input=json.dumps(packs),
            text=True,
            cwd=ROOT,
        )
    )
    report = {
        "checkedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sourceHash": source["sourceHash"],
        "completed": completed,
        "completedCount": len(completed),
        "remaining": [code for code in languages if code not in completed],
        "structuralFailures": failures,
        "scriptWarnings": script_issues,
        "exitCode": str(exit_code),
        "published": False,
        "finalApproval": False,
        "linguisticAccuracyCertified": False,
        "scope": (
            "Source coverage, duplicate JSON object-key rejection, reviewed labels, "
            "long English overlap and script screening. Structural completeness does "
            "not certify translation quality."
        ),
    }
    report["resumeSucceeded"] = str(exit_code) == "0" and not report["remaining"]
    report["readyForLinguisticReview"] = not report["remaining"] and not script_issues
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    args = parser.parse_args()
    stage = Path(args.stage)
    exit_path = stage / "resume-exit-code.txt"
    exit_code = exit_path.read_text().strip() if exit_path.exists() else "not-run"
    report = audit(stage, exit_code)
    (stage / "resume-summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({
        key: report[key]
        for key in (
            "completedCount",
            "remaining",
            "resumeSucceeded",
            "readyForLinguisticReview",
            "exitCode",
        )
    }))
    return 0 if str(report["exitCode"]) == "not-run" or (
        report["resumeSucceeded"] and report["readyForLinguisticReview"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
