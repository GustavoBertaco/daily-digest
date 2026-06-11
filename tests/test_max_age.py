from fetch import resolve_max_age


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
