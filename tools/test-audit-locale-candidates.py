"""Regression tests for exact locale candidate key-set auditing."""
from tools.audit_locale_candidates import key_set_mismatch

assert key_set_mismatch({"a": "translated"}, ["a"]) == ([], [])
assert key_set_mismatch({"a": "translated"}, ["a", "b"]) == (["b"], [])
assert key_set_mismatch({"a": "translated", "extra": "unexpected"}, ["a"]) == ([], ["extra"])
assert key_set_mismatch({"a": "translated", "extra": "unexpected"}, ["a", "b"]) == (["b"], ["extra"])
assert key_set_mismatch(None, ["a"]) == (["a"], [])
print("CANDIDATE_EXACT_KEYSET_AUDIT_PASS")
