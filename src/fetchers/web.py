import json
import sys
from datetime import datetime, timezone

import feedparser
import trafilatura
from dateutil import parser as dateparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from . import FetchedItem
from ._http import safe_get
from .rss import _snippet, _entry_published_utc

_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _headers(referer: str) -> dict:
    return {**_BROWSER_HEADERS, "Referer": referer}


def _rss_from_link_tag(html: str, base_url: str) -> str | None:
    """Find RSS/Atom URL declared in the page <head> link tags."""
    soup = BeautifulSoup(html, "html.parser")
    from urllib.parse import urlparse
    base_root = ".".join(urlparse(base_url).netloc.split(".")[-2:])
    for link in soup.find_all("link", type=True):
        t = link["type"].lower()
        if "rss" in t or "atom" in t:
            href = link.get("href", "")
            if href:
                resolved = href if href.startswith("http") else urljoin(base_url, href)
                link_root = ".".join(urlparse(resolved).netloc.split(".")[-2:])
                if link_root == base_root:
                    return resolved
    return None


def _article_links(html: str, base_url: str, limit: int = 15) -> list[str]:
    """Extract candidate article links from a listing page, same domain only."""
    from urllib.parse import urlparse
    # Match on root domain (last two parts) to allow subdomains e.g. eng.uber.com -> www.uber.com
    base_root = ".".join(urlparse(base_url).netloc.split(".")[-2:])
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        parsed = urlparse(href)
        link_root = ".".join(parsed.netloc.split(".")[-2:])
        path = parsed.path
        # Same root domain only; path must look like an article slug (not pure nav)
        if (link_root == base_root
                and href not in seen
                and href != base_url
                and path.count("/") >= 2
                and len(path) > 20):
            seen.add(href)
            links.append(href)
            if len(links) >= limit:
                break
    return links


def _parse_dt(value: str) -> datetime | None:
    """Parse a date string into a tz-aware UTC datetime, or None on failure."""
    try:
        dt = dateparser.parse(value)
    except (ValueError, OverflowError, TypeError):
        return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _jsonld_date(data) -> datetime | None:
    """Walk a JSON-LD blob (dict, list, or @graph) for a datePublished value."""
    if isinstance(data, list):
        for item in data:
            dt = _jsonld_date(item)
            if dt:
                return dt
        return None
    if isinstance(data, dict):
        if "@graph" in data:
            dt = _jsonld_date(data["@graph"])
            if dt:
                return dt
        val = data.get("datePublished")
        if isinstance(val, str):
            return _parse_dt(val)
    return None


# Meta tags publishers set explicitly to mark publication time, in priority order.
_PUBLISH_META_KEYS = (
    ("property", "article:published_time"),
    ("name", "article:published_time"),
    ("property", "og:published_time"),
    ("itemprop", "datePublished"),
    ("name", "publish-date"),
    ("name", "publication_date"),
    ("name", "publishdate"),
    ("name", "parsely-pub-date"),
    ("name", "sailthru.date"),
    ("name", "DC.date.issued"),
    ("name", "date"),
)


def _extract_publish_date(html: str) -> datetime | None:
    """Extract an article's *publication* date from explicit, semantic signals only.

    Deliberately ignores htmldate/trafilatura's heuristic date guessing, which can
    latch onto non-publication timestamps baked into a page — e.g. a CDN
    "page_generated_at" render time — making stale articles look freshly published.
    We only trust fields a publisher sets to mark publication: standard meta tags,
    JSON-LD datePublished, or a semantically-marked <time> element. Keeping this
    source-agnostic means new website sources work without per-site special-casing.
    Returns a tz-aware UTC datetime, or None when no reliable signal is present.
    """
    soup = BeautifulSoup(html, "html.parser")

    # 1. Standard publication meta tags
    for attr, val in _PUBLISH_META_KEYS:
        tag = soup.find("meta", attrs={attr: val})
        if tag and tag.get("content"):
            dt = _parse_dt(tag["content"])
            if dt:
                return dt

    # 2. JSON-LD datePublished
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            dt = _jsonld_date(json.loads(raw))
        except (ValueError, TypeError):
            continue
        if dt:
            return dt

    # 3. <time> element explicitly marked as the publication date
    for time_tag in soup.find_all("time"):
        dt_attr = time_tag.get("datetime")
        if not dt_attr:
            continue
        itemprop = (time_tag.get("itemprop") or "").lower()
        classes = " ".join(time_tag.get("class") or []).lower()
        if (time_tag.has_attr("pubdate")
                or itemprop == "datepublished"
                or any(h in classes for h in ("publish", "posted", "pubdate"))):
            dt = _parse_dt(dt_attr)
            if dt:
                return dt

    return None


def _items_from_feed(feed_url: str, source_name: str, base_url: str,
                     max_age_hours: int, max_items: int, timeout: int) -> list[FetchedItem]:
    """Fetch an RSS/Atom feed using browser headers (bypasses WAF blocks on feed paths)."""
    from datetime import datetime, timezone, timedelta
    try:
        r = safe_get(feed_url, headers=_headers(base_url), timeout=timeout)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
        if not feed.entries:
            return []

        cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=max_age_hours)
        items: list[FetchedItem] = []
        for entry in feed.entries:
            if len(items) >= max_items:
                break
            pub = _entry_published_utc(entry)
            if pub and pub < cutoff:
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
                source_type="website",
                area_name="",
            ))
        return items
    except Exception:
        return []


def fetch_website(
    url: str,
    source_name: str,
    max_age_hours: int = 24,
    max_items: int = 10,
    timeout: int = 10,
) -> list[FetchedItem]:
    # Step 1: Fetch the homepage with browser headers
    try:
        r = safe_get(url, headers=_headers(url), timeout=timeout)
        r.raise_for_status()
        homepage_html = r.text
    except Exception as exc:
        print(f"ERROR fetch_website({url}): {exc}", file=sys.stderr)
        return []

    # Step 2: Find RSS from <link> tag in page head (catches sites that block /feed paths)
    rss_url = _rss_from_link_tag(homepage_html, url)
    if rss_url:
        items = _items_from_feed(rss_url, source_name, url, max_age_hours, max_items, timeout)
        if items:
            return items

    # Step 3: Try common RSS path suffixes
    for suffix in ("/feed", "/feed/", "/rss", "/rss/", "/atom.xml"):
        candidate = url.rstrip("/") + suffix
        items = _items_from_feed(candidate, source_name, url, max_age_hours, max_items, timeout)
        if items:
            return items

    # Step 4: Scrape article links from the listing page and extract content
    from datetime import timedelta
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=max_age_hours)

    items: list[FetchedItem] = []
    for link in _article_links(homepage_html, url):
        if len(items) >= max_items:
            break
        try:
            ar = safe_get(link, headers=_headers(url), timeout=timeout)
            ar.raise_for_status()
            metadata = trafilatura.extract_metadata(ar.text)
            body = trafilatura.extract(ar.text) or ""
            title = (metadata.title if metadata else "") or link
            if not body:
                continue

            # Use only explicit publication-date signals (see _extract_publish_date).
            # A scraped article whose publish date we cannot verify is dropped: in a
            # freshness-gated digest, an unverifiable date is treated as not-fresh
            # rather than risk surfacing stale content with a misleading timestamp.
            pub_dt = _extract_publish_date(ar.text)
            if pub_dt is None or pub_dt < cutoff:
                if pub_dt is None:
                    print(f"SKIP no publish date: {link}", file=sys.stderr)
                continue

            items.append(FetchedItem(
                title=title,
                url=link,
                published=pub_dt.isoformat() if pub_dt else "",
                content_snippet=body[:500],
                source_name=source_name,
                source_type="website",
                area_name="",
            ))
        except Exception:
            continue

    return items
