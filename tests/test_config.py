from pathlib import Path

import pytest
import yaml

from fetch import load_config

FIXTURE = Path(__file__).parent / "fixtures" / "sources_test.yaml"


def test_load_valid_fixture():
    cfg = load_config(str(FIXTURE))
    assert cfg["areas"][0]["name"] == "Test Area"
    assert cfg["settings"]["user_agent"] == "daily-digest/test"


def _write(tmp_path, data):
    path = tmp_path / "sources.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return str(path)


_BASE_AREA = {
    "name": "A",
    "emoji": "x",
    "folder": "A",
    "sources": [{"type": "rss", "url": "https://e.com/feed", "name": "f"}],
}


def test_rejects_bad_request_timeout(tmp_path):
    cfg = _write(tmp_path, {
        "settings": {"request_timeout_seconds": 0},
        "areas": [_BASE_AREA],
    })
    with pytest.raises(SystemExit):
        load_config(cfg)


def test_rejects_empty_user_agent(tmp_path):
    cfg = _write(tmp_path, {
        "settings": {"user_agent": "  "},
        "areas": [_BASE_AREA],
    })
    with pytest.raises(SystemExit):
        load_config(cfg)


def test_rejects_unknown_source_type(tmp_path):
    bad_area = {**_BASE_AREA, "sources": [{"type": "tiktok", "url": "https://e.com"}]}
    cfg = _write(tmp_path, {"areas": [bad_area]})
    with pytest.raises(SystemExit):
        load_config(cfg)


def test_rejects_bad_source_timeout(tmp_path):
    bad_area = {**_BASE_AREA, "sources": [
        {"type": "rss", "url": "https://e.com/feed", "name": "f", "request_timeout_seconds": 0},
    ]}
    cfg = _write(tmp_path, {"areas": [bad_area]})
    with pytest.raises(SystemExit):
        load_config(cfg)


def test_rejects_non_bool_skip_dedup(tmp_path):
    bad_area = {**_BASE_AREA, "sources": [
        {"type": "rss", "url": "https://e.com/feed", "name": "f", "skip_dedup": "yes"},
    ]}
    cfg = _write(tmp_path, {"areas": [bad_area]})
    with pytest.raises(SystemExit):
        load_config(cfg)


def test_accepts_per_source_overrides(tmp_path):
    area = {**_BASE_AREA, "sources": [
        {"type": "rss", "url": "https://e.com/feed", "name": "f",
         "request_timeout_seconds": 30, "skip_dedup": True},
    ]}
    cfg = load_config(_write(tmp_path, {"areas": [area]}))
    src = cfg["areas"][0]["sources"][0]
    assert src["request_timeout_seconds"] == 30
    assert src["skip_dedup"] is True
