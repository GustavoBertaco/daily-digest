"""
Confirm-at-digest dedup: record every URL that actually made it into a digest so
it never resurfaces in a later one. Run this AFTER the digest is written and
edited, just before committing. Pairs with the filter-only read in src/fetch.py:
fetch.py drops already-recorded URLs but no longer records new ones, so an item
that is fetched but never digested stays eligible until it lands in a digest.

Usage:
  python src/mark_seen.py digests/YYYY-MM-DD.md [--seen-file data/seen_urls.json]
"""
import argparse
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

from seen import load_seen, normalize_url, prune, save_seen

# Markdown inline links: ](url) — covers both `**[Title](url)**` items and any
# `### [Title](url)` heading variants. Over-matching an incidental in-prose link
# is harmless: a URL that is never a feed item can never resurface as one.
_LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)")


def extract_urls(markdown: str) -> list[str]:
    return _LINK_RE.findall(markdown)


def mark_seen(digest_path: Path, seen_path: Path, day: str | None = None) -> int:
    """Record every URL in the digest, returning how many were newly added."""
    day = day or datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    markdown = digest_path.read_text(encoding="utf-8")
    seen = load_seen(seen_path)
    added = 0
    for url in extract_urls(markdown):
        key = normalize_url(url)
        if key not in seen:
            seen[key] = day
            added += 1
    save_seen(seen_path, prune(seen))
    return added


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Record a digest's URLs in the seen registry (confirm-at-digest dedup)"
    )
    parser.add_argument("digest", help="Path to the digest markdown file")
    parser.add_argument("--seen-file", default="data/seen_urls.json")
    args = parser.parse_args()

    digest_path = Path(args.digest)
    if not digest_path.exists():
        print(f"ERROR: digest not found: {digest_path}", file=sys.stderr)
        sys.exit(1)

    added = mark_seen(digest_path, Path(args.seen_file))
    print(f"Marked {added} new URL(s) as seen from {digest_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
