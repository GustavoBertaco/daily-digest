from . import FetchedItem
from .rss import fetch_rss

_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def fetch_youtube(
    channel_id: str,
    source_name: str,
    max_age_hours: int = 24,
    max_items: int = 10,
) -> list[FetchedItem]:
    url = _FEED_URL.format(channel_id=channel_id)
    items = fetch_rss(url, source_name, source_type="youtube",
                      max_age_hours=max_age_hours, max_items=max_items)
    # Rewrite short URLs to full watch URLs when feedparser returns the short form
    for item in items:
        if "youtu.be/" in item["url"] or "youtube.com/watch" not in item["url"]:
            vid_id = item["url"].split("/")[-1].split("?")[0]
            item["url"] = f"https://www.youtube.com/watch?v={vid_id}"
    return items
