import calendar
import html
import re
import sys
from datetime import datetime, timezone, timedelta

import feedparser

from . import FetchedItem


def _strip_html(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _entry_published_utc(entry) -> datetime | None:
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if t is None:
        return None
    return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc)


def _snippet(entry) -> str:
    for field in ("content", "summary", "itunes_summary", "description"):
        val = getattr(entry, field, None)
        if val:
            if isinstance(val, list) and val:
                val = val[0].get("value", "")
            if isinstance(val, str) and val.strip():
                return _strip_html(val)[:500]
    return ""


def fetch_rss(
    url: str,
    source_name: str,
    source_type: str = "rss",
    max_age_hours: int = 24,
    max_items: int = 10,
    timeout: int = 10,
) -> list[FetchedItem]:
    try:
        feed = feedparser.parse(url, request_headers={"User-Agent": "daily-digest/1.0"})
        if feed.bozo and not feed.entries:
            return []

        cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=max_age_hours)
        items: list[FetchedItem] = []

        for entry in feed.entries:
            if len(items) >= max_items:
                break
            pub = _entry_published_utc(entry)
            if pub is not None and pub < cutoff:
                continue
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            if not title or not link:
                continue
            items.append(FetchedItem(
                title=title,
                url=link,
                published=pub.isoformat() if pub else "",
                content_snippet=_snippet(entry),
                source_name=source_name,
                source_type=source_type,
                area_name="",
            ))

        return items
    except Exception as exc:
        print(f"ERROR fetch_rss({url}): {exc}", file=sys.stderr)
        return []
