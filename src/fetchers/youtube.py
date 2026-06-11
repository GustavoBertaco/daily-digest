import re
import sys

import requests

from . import FetchedItem
from .rss import fetch_rss

_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
_TRANSCRIPT_CHAR_LIMIT = 3000
_SHORTS_MAX_SECONDS = 120


def _video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return url.split("/")[-1].split("?")[0]


def _duration_seconds(vid_id: str) -> int | None:
    try:
        r = requests.get(
            f"https://www.youtube.com/watch?v={vid_id}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        m = re.search(r'"lengthSeconds":"(\d+)"', r.text)
        return int(m.group(1)) if m else None
    except Exception:
        return None


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
    try:
        url = _FEED_URL.format(channel_id=channel_id)
        # Fetch more than needed to account for Shorts being filtered out
        candidates = fetch_rss(url, source_name, source_type="youtube",
                               max_age_hours=max_age_hours, max_items=max_items * 3)

        items: list[FetchedItem] = []
        for item in candidates:
            if len(items) >= max_items:
                break

            # Normalise to full watch URL
            if "youtu.be/" in item["url"] or "youtube.com/watch" not in item["url"]:
                vid_id = _video_id(item["url"])
                item["url"] = f"https://www.youtube.com/watch?v={vid_id}"
            else:
                vid_id = _video_id(item["url"])

            # Skip Shorts (≤ 60s). If duration is unavailable, include the video.
            duration = _duration_seconds(vid_id)
            if duration is not None and duration <= _SHORTS_MAX_SECONDS:
                continue

            # Prefer transcript over RSS description for richer summarisation
            transcript = _fetch_transcript(vid_id)
            if transcript:
                item["content_snippet"] = transcript

            items.append(item)

        return items
    except Exception as exc:
        print(f"ERROR fetch_youtube({channel_id}): {exc}", file=sys.stderr)
        return []
