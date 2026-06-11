"""
Checks whether data/latest_fetch.json is fresh enough to build today's digest.

Usage:
  python src/check_freshness.py [--file data/latest_fetch.json] [--max-age-hours 3]

Exit codes: 0 = fresh, 1 = stale or missing/unreadable.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def is_fresh(fetched_at_iso: str, now: datetime, max_age_hours: float) -> tuple[bool, float]:
    """Returns (fresh, age_in_hours). Raises ValueError on unparseable timestamp."""
    fetched_at = datetime.strptime(fetched_at_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    age_hours = (now - fetched_at).total_seconds() / 3600
    return age_hours <= max_age_hours, age_hours


def main() -> None:
    parser = argparse.ArgumentParser(description="Check freshness of fetched content")
    parser.add_argument("--file", default="data/latest_fetch.json")
    parser.add_argument("--max-age-hours", type=float, default=3)
    args = parser.parse_args()

    path = Path(args.file)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        fetched_at = data["fetched_at"]
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"MISSING file={args.file} ({e})")
        sys.exit(1)

    try:
        fresh, age_hours = is_fresh(fetched_at, datetime.now(tz=timezone.utc), args.max_age_hours)
    except ValueError:
        print(f"STALE fetched_at={fetched_at} (unparseable timestamp)")
        sys.exit(1)

    if fresh:
        print(f"FRESH age={age_hours:.1f}h fetched_at={fetched_at}")
        sys.exit(0)
    print(f"STALE age={age_hours:.1f}h fetched_at={fetched_at}")
    sys.exit(1)


if __name__ == "__main__":
    main()
