from typing import TypedDict


class FetchedItem(TypedDict):
    title: str
    url: str
    published: str       # ISO-8601 UTC string
    content_snippet: str # First ~500 chars of body; empty string if unavailable
    source_name: str     # Human-readable name from config
    source_type: str     # "rss" | "podcast" | "youtube" | "website"
    area_name: str       # Injected by fetch.py after calling the fetcher
