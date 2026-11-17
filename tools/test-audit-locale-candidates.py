"""Regression tests for exact locale candidate key-set auditing."""
from tools.audit_locale_candidates import key_set_mismatch, source_string_keys

assert key_set_mismatch({"a": "translated"}, ["a"]) == ([], [])
assert key_set_mismatch({"a": "translated"}, ["a", "b"]) == (["b"], [])
assert key_set_mismatch({"a": "translated", "extra": "unexpected"}, ["a"]) == ([], ["extra"])
assert key_set_mismatch({"a": "translated", "extra": "unexpected"}, ["a", "b"]) == (["b"], ["extra"])
assert key_set_mismatch(None, ["a"]) == (["a"], [])

# The current R125 builder writes source.json["strings"] as an ordered array.
assert source_string_keys({"strings": ["Ask", "Job", "Nearby"]}) == ["Ask", "Job", "Nearby"]

# Retain compatibility with legacy source maps.
assert source_string_keys({"strings": {"Ask": "Ask", "Job": "Job"}}) == ["Ask", "Job"]

for invalid in (
    {"strings": ["Ask", "Ask"]},
    {"strings": ["Ask", ""]},
    {"strings": ["Ask", 7]},
    {"strings": None},
    {},
):
    try:
        source_string_keys(invalid)
    except RuntimeError:
        pass
    else:
        raise AssertionError(f"Invalid candidate source strings accepted: {invalid}")

print("CANDIDATE_SOURCE_FORMAT_AND_EXACT_KEYSET_AUDIT_PASS")
