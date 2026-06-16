from fetch import _write_log


def _area(**overrides):
    area = {
        "name": "Technology",
        "emoji": "💻",
        "folder": "Tech",
        "summary_style": "insight",
        "tags": [],
        "items": [],
        "errors": [],
        "deduped_sources": {},
    }
    area.update(overrides)
    return area


def _write(tmp_path, areas):
    output = {"fetched_at": "2026-06-15T15:32:23Z", "max_age_hours": 26, "areas": areas}
    path = tmp_path / "run.md"
    _write_log(str(path), output)
    return path.read_text(encoding="utf-8")


def test_deduped_only_source_stays_visible(tmp_path):
    # Airbnb fetched 1 item but it was already digested -> 0 items, 0 errors.
    # It must still appear in the log instead of silently vanishing.
    text = _write(tmp_path, [
        _area(
            errors=[{"source_name": "Netflix Tech Blog",
                     "error": "No items returned (feed empty or all outside time window)"}],
            deduped_sources={"Airbnb Tech": 1},
        )
    ])
    assert "Airbnb Tech" in text
    assert "↩️ 1 already digested" in text
    assert "Netflix Tech Blog" in text


def test_deduped_source_not_counted_as_error(tmp_path):
    text = _write(tmp_path, [_area(deduped_sources={"Airbnb Tech": 2})])
    assert "↩️ 2 already digested" in text
    # A stale-but-healthy source is not an error.
    assert "- Sources with errors: 0" in text


def test_source_with_kept_items_takes_precedence_over_dedup(tmp_path):
    # If a source has surviving items it is reported via those, never as deduped.
    text = _write(tmp_path, [
        _area(
            items=[{"source_name": "Airbnb Tech", "url": "https://x", "title": "t"}],
            deduped_sources={},  # main() omits sources that kept items
        )
    ])
    assert "| Airbnb Tech | Technology | 1 | ✅ |" in text
    assert "already digested" not in text
