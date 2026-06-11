from datetime import datetime, timezone

from seen import load_seen, normalize_url, prune, save_seen


def test_normalize_strips_tracking_params_and_trailing_slash():
    url = "HTTPS://Example.com/Blog/Post/?utm_source=rss&utm_medium=feed&ref=home&id=2"
    assert normalize_url(url) == "https://example.com/Blog/Post?id=2"


def test_normalize_keeps_meaningful_query_and_drops_fragment():
    assert normalize_url("https://a.com/p?page=2#section") == "https://a.com/p?page=2"


def test_normalize_bare_domain():
    assert normalize_url("https://example.com/") == "https://example.com/"


def test_round_trip(tmp_path):
    path = tmp_path / "seen.json"
    seen = {"https://a.com/x": "2026-06-11", "https://b.com/y": "2026-06-01"}
    save_seen(path, seen)
    assert load_seen(path) == seen


def test_load_missing_file_returns_empty(tmp_path):
    assert load_seen(tmp_path / "nope.json") == {}


def test_load_corrupt_file_returns_empty(tmp_path):
    path = tmp_path / "seen.json"
    path.write_text("{not json", encoding="utf-8")
    assert load_seen(path) == {}


def test_prune_drops_old_keeps_recent():
    now = datetime(2026, 6, 30, tzinfo=timezone.utc)
    seen = {
        "https://old.com/a": "2026-05-29",   # 32 days old
        "https://recent.com/b": "2026-06-01",  # 29 days old
        "https://bad.com/c": "not-a-date",
    }
    assert prune(seen, retention_days=30, now=now) == {"https://recent.com/b": "2026-06-01"}
