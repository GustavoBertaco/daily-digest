"""
Entry point: reads config/sources.yaml, fetches all sources, writes JSON.

Usage:
  python src/fetch.py [--config PATH] [--output PATH] [--max-age-hours N]
                      [--max-items N] [--area NAME] [--dry-run]
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from fetchers import FetchedItem
from fetchers.rss import fetch_rss
from fetchers.youtube import fetch_youtube
from fetchers.web import fetch_website

_REQUIRED_AREA_KEYS = {"name", "emoji", "folder", "sources"}
_REQUIRED_SOURCE_KEYS_BY_TYPE = {
    "rss": {"url"},
    "podcast": {"url"},
    "youtube": {"channel_id"},
    "website": {"url"},
}


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        print(f"ERROR: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: invalid YAML in {config_path}: {e}", file=sys.stderr)
        sys.exit(1)

    areas = cfg.get("areas")
    if not areas or not isinstance(areas, list):
        print("ERROR: sources.yaml must have a non-empty 'areas' list", file=sys.stderr)
        sys.exit(1)

    for area in areas:
        missing = _REQUIRED_AREA_KEYS - area.keys()
        if missing:
            print(f"ERROR: area '{area.get('name', '?')}' missing fields: {missing}", file=sys.stderr)
            sys.exit(1)
        for src in area["sources"]:
            src_type = src.get("type")
            required = _REQUIRED_SOURCE_KEYS_BY_TYPE.get(src_type)
            if required is None:
                print(f"ERROR: unknown source type '{src_type}' in area '{area['name']}'", file=sys.stderr)
                sys.exit(1)
            missing_src = required - src.keys()
            if missing_src:
                print(f"ERROR: source '{src.get('name','?')}' missing fields: {missing_src}", file=sys.stderr)
                sys.exit(1)

    return cfg


def fetch_area(area: dict, settings: dict, filter_areas: list[str]) -> dict:
    if filter_areas and area["name"] not in filter_areas:
        return None

    max_age = settings.get("max_age_hours", 24)
    max_items = settings.get("max_items_per_source", 10)

    result = {
        "name": area["name"],
        "emoji": area["emoji"],
        "folder": area["folder"],
        "tags": area.get("tags", []),
        "items": [],
        "errors": [],
    }

    for src in area["sources"]:
        src_type = src["type"]
        src_name = src.get("name", src_type)
        try:
            if src_type in ("rss", "podcast"):
                items = fetch_rss(src["url"], src_name, source_type=src_type,
                                  max_age_hours=max_age, max_items=max_items)
            elif src_type == "youtube":
                items = fetch_youtube(src["channel_id"], src_name,
                                      max_age_hours=max_age, max_items=max_items)
            elif src_type == "website":
                items = fetch_website(src["url"], src_name,
                                      max_age_hours=max_age, max_items=max_items)
            else:
                items = []

            for item in items:
                item["area_name"] = area["name"]
            result["items"].extend(items)

            if not items:
                result["errors"].append({"source_name": src_name, "error": "No items returned (feed empty or all outside time window)"})

        except Exception as e:
            result["errors"].append({"source_name": src_name, "error": str(e)})

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch daily digest content")
    parser.add_argument("--config", default="config/sources.yaml")
    parser.add_argument("--output", default=None, help="Write JSON to file (default: stdout)")
    parser.add_argument("--max-age-hours", type=int, default=None)
    parser.add_argument("--max-items", type=int, default=None)
    parser.add_argument("--area", action="append", default=[], dest="areas",
                        help="Fetch only this area name (repeatable)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate config and print summary without fetching")
    args = parser.parse_args()

    cfg = load_config(args.config)
    settings = cfg.get("settings", {})
    if args.max_age_hours is not None:
        settings["max_age_hours"] = args.max_age_hours
    if args.max_items is not None:
        settings["max_items_per_source"] = args.max_items

    if args.dry_run:
        print(f"Config OK — {len(cfg['areas'])} areas:")
        for a in cfg["areas"]:
            print(f"  {a['emoji']} {a['name']} ({len(a['sources'])} sources)")
        sys.exit(0)

    fetched_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    output = {
        "fetched_at": fetched_at,
        "max_age_hours": settings.get("max_age_hours", 24),
        "areas": [],
    }

    all_empty = True
    for area in cfg["areas"]:
        area_result = fetch_area(area, settings, args.areas)
        if area_result is None:
            continue
        output["areas"].append(area_result)
        if area_result["items"]:
            all_empty = False

    json_out = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json_out, encoding="utf-8")
        print(f"Wrote {len(json_out)} bytes to {args.output}", file=sys.stderr)
    else:
        print(json_out)

    if all_empty:
        sys.exit(2)


if __name__ == "__main__":
    main()
