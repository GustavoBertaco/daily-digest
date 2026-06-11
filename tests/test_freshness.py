from datetime import datetime, timezone

import pytest

from check_freshness import is_fresh

NOW = datetime(2026, 6, 11, 12, 0, 0, tzinfo=timezone.utc)


def test_fresh_quarter_hour():
    fresh, age = is_fresh("2026-06-11T11:45:00Z", NOW, max_age_hours=3)
    assert fresh
    assert age == pytest.approx(0.25)


def test_stale_yesterday():
    fresh, age = is_fresh("2026-06-10T12:00:00Z", NOW, max_age_hours=3)
    assert not fresh
    assert age == pytest.approx(24)


def test_boundary_exactly_at_threshold_is_fresh():
    fresh, _ = is_fresh("2026-06-11T09:00:00Z", NOW, max_age_hours=3)
    assert fresh


def test_malformed_timestamp_raises():
    with pytest.raises(ValueError):
        is_fresh("yesterday-ish", NOW, max_age_hours=3)
