"""Regression tests for strict JSON parsing in locale candidate audits."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.audit_locale_candidates import (
    DuplicateJSONKeyError,
    parse_json_unique,
    read_json_unique,
)

assert parse_json_unique('{"a": 1, "nested": {"b": 2}}') == {
    "a": 1,
    "nested": {"b": 2},
}

for raw in (
    '{"translations": {"hello": "one", "hello": "two"}}',
    '{"metadata": {"sourceHash": "x", "sourceHash": "y"}}',
    '{"outer": {"inner": {"k": 1, "k": 2}}}',
):
    try:
        parse_json_unique(raw)
    except DuplicateJSONKeyError:
        pass
    else:
        raise AssertionError(f"Duplicate JSON key was silently accepted: {raw}")

try:
    parse_json_unique('{"a": ')
except json.JSONDecodeError:
    pass
else:
    raise AssertionError("Malformed JSON must remain a parse error")

with TemporaryDirectory() as directory:
    invalid_utf8 = Path(directory) / "invalid.json"
    invalid_utf8.write_bytes(b"\\xff")
    try:
        read_json_unique(invalid_utf8)
    except UnicodeDecodeError:
        pass
    else:
        raise AssertionError("Invalid UTF-8 must be rejected")

print("LOCALE_JSON_DUPLICATE_KEY_GUARD_PASS: duplicate keys, malformed JSON and invalid UTF-8 rejected")
