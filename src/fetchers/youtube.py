from . import FetchedItem
from .rss import fetch_rss

_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
_TRANSCRIPT_CHAR_LIMIT = 3000


def _video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return url.split("/")[-1].split("?")[0]


def _fetch_transcript(vid_id: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        transcript = api.fetch(vid_id)
        text = " ".join(s.text for s in transcript)
        return text[:_TRANSCRIPT_CHAR_LIMIT]
    except Exception:
        return ""


def fetch_youtube(
    channel_id: str,
    source_name: str,
    max_age_hours: int = 24,
    max_items: int = 10,
) -> list[FetchedItem]:
    url = _FEED_URL.format(channel_id=channel_id)
    items = fetch_rss(url, source_name, source_type="youtube",
                      max_age_hours=max_age_hours, max_items=max_items)

    for item in items:
        # Normalise URL to full watch URL
        if "youtu.be/" in item["url"] or "youtube.com/watch" not in item["url"]:
            vid_id = _video_id(item["url"])
            item["url"] = f"https://www.youtube.com/watch?v={vid_id}"
        else:
            vid_id = _video_id(item["url"])

        # Prefer transcript over description for richer summarisation
        transcript = _fetch_transcript(vid_id)
        if transcript:
            item["content_snippet"] = transcript

    return items
