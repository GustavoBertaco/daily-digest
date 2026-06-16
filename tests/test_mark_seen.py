from mark_seen import extract_urls, mark_seen
from seen import load_seen

_DIGEST = """---
date: 2026-06-15
tags: [digest]
---

# Daily Digest — June 15, 2026

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
    digest = tmp_path / "2026-06-15.md"
    digest.write_text(_DIGEST, encoding="utf-8")
    seen_path = tmp_path / "seen.json"

    added = mark_seen(digest, seen_path, day="2026-06-15")

    assert added == 2
    seen = load_seen(seen_path)
    assert seen["https://www.youtube.com/watch?v=c-2eEv2ou7Y"] == "2026-06-15"
    assert seen["https://www.databricks.com/blog/skip-learning-curve"] == "2026-06-15"


def test_mark_seen_is_idempotent_and_preserves_first_seen(tmp_path):
    digest = tmp_path / "2026-06-15.md"
    digest.write_text(_DIGEST, encoding="utf-8")
    seen_path = tmp_path / "seen.json"

    mark_seen(digest, seen_path, day="2026-06-15")
    added_again = mark_seen(digest, seen_path, day="2026-06-16")

    assert added_again == 0
    seen = load_seen(seen_path)
    # Original first-seen date is kept, not overwritten by the later run.
    assert seen["https://www.youtube.com/watch?v=c-2eEv2ou7Y"] == "2026-06-15"
