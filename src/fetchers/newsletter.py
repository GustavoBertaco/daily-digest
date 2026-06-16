"""Fetch a newsletter delivered via a kill-the-newsletter Atom feed.

The email body is **untrusted** — anyone can email a kill-the-newsletter address,
so its subject/body text is never summarized or shown to an LLM. We use the email
*solely to harvest article links*, then fetch and summarize each destination page
through the same trusted path `website` sources use. Two gates keep junk and
attacker-controlled mail out:

  1. Sender allowlist — only entries whose structured ``<author><email>`` matches a
     configured sender are processed (``_entry_sender`` / ``senders``).
  2. Link-only + denylist — only ``http(s)`` ``<a href>`` URLs are taken, and
     non-article noise (unsubscribe, social shares, image CDNs, Substack app/profile
     action links) is dropped (``_extract_links`` / ``_is_article_link``).

Every fetch goes through ``safe_get`` (SSRF guard + per-hop redirect re-validation),
which also unwraps Substack tracking-redirect links to their final destination.
"""
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

import feedparser
import trafilatura
from bs4 import BeautifulSoup

from . import FetchedItem
from ._http import safe_get
from .rss import _entry_published_utc
from .web import _headers

# Hosts/path fragments that are never article destinations. Matched case-insensitively
# against the URL. Keeps the curated links (real articles) and drops newsletter chrome.
_DENY_HOST_SUFFIXES = (
    "substackcdn.com",        # image/asset CDN
    "twitter.com",
    "x.com",
    "facebook.com",
    "linkedin.com",
    "instagram.com",
    "youtube.com",            # handled by the dedicated youtube source type
    "youtu.be",
)
_DENY_PATH_FRAGMENTS = (
    "/unsubscribe",
    "/manage",
    "/subscribe",
    "/account",
    "/profile",
    "/comments",
    "/comment",
    "/app/",
    "/action/",
    "/redirect/feed",
)


def _entry_sender(entry) -> str | None:
    """The sender email from the Atom ``<author><email>`` element, lowercased.

    kill-the-newsletter records the originating address in a structured author
    element, which feedparser surfaces as ``entry.author_detail.email``. Returns
    None when absent (those entries are dropped by the allowlist check).
    """
    detail = getattr(entry, "author_detail", None)
    email = (detail or {}).get("email") if isinstance(detail, dict) else getattr(detail, "email", None)
    if email and isinstance(email, str):
        return email.strip().lower()
    return None


def _is_article_link(url: str) -> bool:
    """True only for http(s) links that look like real article destinations."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    if any(host == d or host.endswith("." + d) for d in _DENY_HOST_SUFFIXES):
        return False
    path = parsed.path.lower()
    if any(frag in path for frag in _DENY_PATH_FRAGMENTS):
        return False
    return True


def _extract_links(html: str) -> list[str]:
    """Harvest article URLs from email HTML — links only, never the surrounding text.

    Only ``<a href>`` values survive; the email's prose is deliberately ignored so no
    attacker-controlled text reaches the digest. Applies the scheme + denylist filter
    and dedups while preserving first-seen order.
    """
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or not _is_article_link(href):
            continue
        if href in seen:
            continue
        seen.add(href)
        links.append(href)
    return links


def fetch_newsletter(
    url: str,
    source_name: str,
    senders: list[str],
    max_age_hours: int = 180,
    max_items: int = 10,
    timeout: int = 10,
    user_agent: str = "daily-digest/1.0",
) -> list[FetchedItem]:
    allow = {s.strip().lower() for s in senders if isinstance(s, str)}
    try:
        r = safe_get(url, headers={"User-Agent": user_agent}, timeout=timeout)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
    except Exception as exc:
        print(f"ERROR fetch_newsletter({url}): {exc}", file=sys.stderr)
        return []

    if not feed.entries:
        return []

    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=max_age_hours)

    # Collect candidate links from every in-window entry sent by an allowed sender.
    # The newsletter *issue* is the fresh unit: each link inherits its issue's date,
    # so a weekly roundup can legitimately surface older-than-26h articles.
    candidates: list[tuple[str, datetime | None]] = []
    seen_links: set[str] = set()
    for entry in feed.entries:
        sender = _entry_sender(entry)
        if sender is None or sender not in allow:
            continue
        pub = _entry_published_utc(entry)
        if pub is not None and pub < cutoff:
            continue
        body = ""
        content = getattr(entry, "content", None)
        if content and isinstance(content, list):
            body = content[0].get("value", "") or ""
        if not body:
            body = getattr(entry, "summary", "") or ""
        for link in _extract_links(body):
            if link in seen_links:
                continue
            seen_links.add(link)
            candidates.append((link, pub))

    items: list[FetchedItem] = []
    for link, pub in candidates:
        if len(items) >= max_items:
            break
        try:
            ar = safe_get(link, headers=_headers(url), timeout=timeout)
            ar.raise_for_status()
            metadata = trafilatura.extract_metadata(ar.text)
            body = trafilatura.extract(ar.text) or ""
            if not body:
                continue
            final_url = ar.url or link  # safe_get unwraps tracking redirects
            title = (metadata.title if metadata else "") or final_url
            items.append(FetchedItem(
                title=title,
                url=final_url,
                published=pub.isoformat() if pub else "",
                content_snippet=body[:500],
                source_name=source_name,
                source_type="website",  # flows through the insight pipeline
                area_name="",
            ))
        except Exception:
            continue

    return items
