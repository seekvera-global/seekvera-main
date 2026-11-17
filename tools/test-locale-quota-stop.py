"""Quota-neutral regression tests for terminal translation blockers."""
import urllib.error
from io import BytesIO
from unittest.mock import patch

import tools.build_current_locale_delta as builder

cases = [
    ("daily_free_ai_limit", "quota_or_rate_limit"),
    ("daily free AI limit", "quota_or_rate_limit"),
    ("3036 daily free allocation", "quota_or_rate_limit"),
    ("Google HTTP 429", "quota_or_rate_limit"),
    ("provider_rate_limited", "quota_or_rate_limit"),
    ("Too Many Requests", "quota_or_rate_limit"),
    ('{"reason":"all_translation_backends_unavailable"}', "all_translation_backends_unavailable"),
    ("HTTP 503 all translation backends unavailable", "all_translation_backends_unavailable"),
    ("HTTP 503 temporary overload", None),
    ("socket timeout", None),
]
for detail, expected in cases:
    actual = builder.translation_stop_reason(detail)
    assert actual == expected, (detail, actual, expected)

def make_http_error(code, body):
    return urllib.error.HTTPError(
        "https://seekveraglobal.com/api/ui-translate",
        code,
        "blocked",
        None,
        BytesIO(body.encode()),
    )

# A terminal quota/rate-limit/backend-unavailable response must not split
# a failed batch into more requests.
for code, body in [
    (429, '{"reason":"provider_rate_limited"}'),
    (503, '{"reason":"all_translation_backends_unavailable"}'),
    (503, '{"reason":"daily_free_ai_limit"}'),
]:
    calls = []
    def fail_once(language, strings, error=make_http_error(code, body)):
        calls.append((language, list(strings)))
        raise error
    with patch.object(builder, "translate", side_effect=fail_once):
        try:
            builder.translate_small("Dhivehi", ["a", "b", "c", "d"])
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"Expected terminal stop for HTTP {code}")
    assert len(calls) == 1, (code, calls)

print("TRANSLATION_STOP_BOUNDARY_PASS: 10 classifications; 3 terminal no-split cases")
