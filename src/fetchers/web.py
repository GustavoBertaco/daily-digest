import sys

import feedparser
import trafilatura
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
            items.append(FetchedItem(
                title=title,
                url=link,
                published="",
                content_snippet=body[:500],
                source_name=source_name,
                source_type="website",
                area_name="",
            ))
        except Exception:
            continue

    return items
