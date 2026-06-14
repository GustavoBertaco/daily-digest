"""
Seen-URL registry: prevents items (especially undated scraped pages) from
reappearing in consecutive digests. Stored as JSON with a rolling retention
window so the file stays small.

Semantics note: fetch.py marks URLs as seen at *fetch* time, not at digest time.
If the fetch succeeds but the downstream digest never runs, those items are still
recorded as seen and won't resurface. The 30-day retention window bounds the loss,
but a future improvement is to have the digest step confirm inclusion before a URL
is committed to the registry.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_TRACKING_PARAMS_PREFIXES = ("utm_",)
_TRACKING_PARAMS = {"ref", "source"}


def normalize_url(url: str) -> str:
    """Canonical form for dedup: lowercase scheme/host, no trailing slash, no tracking params."""
    parsed = urlparse(url.strip())
    query = [
        (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if k not in _TRACKING_PARAMS and not k.lower().startswith(_TRACKING_PARAMS_PREFIXES)
    ]
    return urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/") or "/",
        parsed.params,
        urlencode(query),
        "",  # drop fragment
    ))


def load_seen(path: Path) -> dict[str, str]:
    """Returns {normalized_url: first_seen_date}. Missing or corrupt file -> empty registry."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        urls = data.get("urls", {})
        if isinstance(urls, dict):
            return {str(k): str(v) for k, v in urls.items()}
    except (OSError, json.JSONDecodeError, AttributeError) as e:
        if path.exists():
            print(f"WARNING: could not read seen registry {path}: {e}", file=sys.stderr)
    return {}


def prune(seen: dict[str, str], retention_days: int = 30,
          now: datetime | None = None) -> dict[str, str]:
    """Drop entries first seen more than retention_days ago (malformed dates are dropped too)."""
    now = now or datetime.now(tz=timezone.utc)
    cutoff = (now - timedelta(days=retention_days)).strftime("%Y-%m-%d")
    kept: dict[str, str] = {}
    for url, day in seen.items():
        try:
            datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            continue
        if day >= cutoff:
            kept[url] = day
    return kept


def save_seen(path: Path, seen: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "urls": dict(sorted(seen.items()))}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
