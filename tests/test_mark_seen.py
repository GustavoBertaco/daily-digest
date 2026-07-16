from datetime import datetime, timedelta, timezone

from mark_seen import extract_urls, mark_seen
from seen import load_seen

# mark_seen() prunes against the real wall-clock date (no `now` override), so
# fixture dates must float with "today" rather than being pinned to a fixed
# calendar date — a hardcoded date eventually ages past the 30-day retention
# window and gets silently pruned, failing the test.
_TODAY = datetime.now(tz=timezone.utc).date()
_DAY1 = _TODAY.isoformat()
_DAY2 = (_TODAY + timedelta(days=1)).isoformat()

_DIGEST = f"""---
date: {_DAY1}
tags: [digest]
---

# Daily Digest — {_DAY1}

# 🤖 AI & Machine Learning

## AI Engineer

**[Why MCP Apps Use Double Iframes](https://www.youtube.com/watch?v=c-2eEv2ou7Y)**
Framing sentence. See the docs at https://example.com/plain (not a markdown link).

### [A heading-style item](https://www.databricks.com/blog/skip-learning-curve)
Some summary text.
"""


def test_extract_urls_finds_markdown_links_only():
    urls = extract_urls(_DIGEST)
    assert urls == [
        "https://www.youtube.com/watch?v=c-2eEv2ou7Y",
        "https://www.databricks.com/blog/skip-learning-curve",
    ]
    # A bare in-prose URL without markdown link syntax is not captured.
    assert "https://example.com/plain" not in urls


def test_mark_seen_adds_normalized_urls(tmp_path):
    digest = tmp_path / f"{_DAY1}.md"
    digest.write_text(_DIGEST, encoding="utf-8")
    seen_path = tmp_path / "seen.json"

    added = mark_seen(digest, seen_path, day=_DAY1)

    assert added == 2
    seen = load_seen(seen_path)
    assert seen["https://www.youtube.com/watch?v=c-2eEv2ou7Y"] == _DAY1
    assert seen["https://www.databricks.com/blog/skip-learning-curve"] == _DAY1


def test_mark_seen_is_idempotent_and_preserves_first_seen(tmp_path):
    digest = tmp_path / f"{_DAY1}.md"
    digest.write_text(_DIGEST, encoding="utf-8")
    seen_path = tmp_path / "seen.json"

    mark_seen(digest, seen_path, day=_DAY1)
    added_again = mark_seen(digest, seen_path, day=_DAY2)

    assert added_again == 0
    seen = load_seen(seen_path)
    # Original first-seen date is kept, not overwritten by the later run.
    assert seen["https://www.youtube.com/watch?v=c-2eEv2ou7Y"] == _DAY1
