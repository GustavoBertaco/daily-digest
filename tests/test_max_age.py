from fetch import resolve_max_age, resolve_max_items, resolve_timeout


def test_source_override_wins():
    src = {"type": "rss", "max_age_hours": 180}
    settings = {"max_age_hours": 26, "max_age_hours_by_type": {"rss": 50}}
    assert resolve_max_age(src, settings) == 180


def test_type_default_beats_global():
    src = {"type": "podcast"}
    settings = {"max_age_hours": 26, "max_age_hours_by_type": {"podcast": 180}}
    assert resolve_max_age(src, settings) == 180


def test_global_fallback():
    src = {"type": "rss"}
    settings = {"max_age_hours": 26, "max_age_hours_by_type": {"podcast": 180}}
    assert resolve_max_age(src, settings) == 26


def test_library_default_when_no_settings():
    assert resolve_max_age({"type": "rss"}, {}) == 24


def test_forced_cli_value_wins_over_all():
    src = {"type": "podcast", "max_age_hours": 180}
    settings = {
        "max_age_hours": 72,
        "_max_age_forced": True,
        "max_age_hours_by_type": {"podcast": 180},
    }
    assert resolve_max_age(src, settings) == 72


def test_timeout_source_override_wins():
    assert resolve_timeout({"request_timeout_seconds": 30}, {"request_timeout_seconds": 10}) == 30


def test_timeout_global_fallback():
    assert resolve_timeout({"type": "rss"}, {"request_timeout_seconds": 15}) == 15


def test_timeout_library_default():
    assert resolve_timeout({"type": "rss"}, {}) == 10


def test_max_items_source_override_wins():
    assert resolve_max_items({"max_items": 25}, {"max_items_per_source": 10}) == 25


def test_max_items_global_fallback():
    assert resolve_max_items({"type": "rss"}, {"max_items_per_source": 8}) == 8


def test_max_items_library_default():
    assert resolve_max_items({"type": "rss"}, {}) == 10


def test_max_items_forced_cli_wins_over_source():
    src = {"max_items": 25}
    settings = {"max_items_per_source": 3, "_max_items_forced": True}
    assert resolve_max_items(src, settings) == 3
