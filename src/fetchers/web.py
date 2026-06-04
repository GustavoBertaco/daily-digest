from . import FetchedItem
from .rss import fetch_rss

try:
    import trafilatura
    _HAS_TRAFILATURA = True
except ImportError:
    _HAS_TRAFILATURA = False

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


def fetch_website(
    url: str,
    source_name: str,
    max_age_hours: int = 24,
    max_items: int = 10,
    timeout: int = 10,
) -> list[FetchedItem]:
    # Strategy 1: autodiscover an RSS/Atom feed and hand off to the RSS fetcher
    if _HAS_TRAFILATURA:
        try:
            feed_urls = trafilatura.feeds.find_feed_urls(url, target_lang=None)
            if feed_urls:
                items = fetch_rss(feed_urls[0], source_name, source_type="website",
                                  max_age_hours=max_age_hours, max_items=max_items)
                if items:
                    return items
        except Exception:
            pass

    # Strategy 2: fetch homepage and extract individual article links
    if not _HAS_REQUESTS or not _HAS_TRAFILATURA:
        return []

    try:
        resp = _requests.get(url, timeout=timeout,
                             headers={"User-Agent": "daily-digest/1.0"})
        resp.raise_for_status()
        homepage_html = resp.text
    except Exception:
        return []

    try:
        links = trafilatura.extract_links(homepage_html, base_url=url)
        if not links:
            return []
    except Exception:
        return []

    items: list[FetchedItem] = []
    seen: set[str] = set()
    candidate_links = [lnk for lnk in links if lnk not in seen and not seen.add(lnk)][:15]

    for link in candidate_links:
        if len(items) >= max_items:
            break
        try:
            r = _requests.get(link, timeout=timeout,
                              headers={"User-Agent": "daily-digest/1.0"})
            r.raise_for_status()
            metadata = trafilatura.extract_metadata(r.text)
            body = trafilatura.extract(r.text) or ""
            title = (metadata.title if metadata else "") or link
            snippet = body[:500] if body else ""
            items.append(FetchedItem(
                title=title,
                url=link,
                published="",
                content_snippet=snippet,
                source_name=source_name,
                source_type="website",
                area_name="",
            ))
        except Exception:
            continue

    return items
